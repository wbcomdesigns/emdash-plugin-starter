#!/usr/bin/env python3
"""Clean a copy of the showcase database for the model-site snapshot, then verify it.

One rule set drives both the cleaning and the check, and the check reads stored values
(JSON parsed, percent-encoding decoded), not a text dump. Any finding exits non-zero,
and snapshot.sh then discards the copy. Usage: scrub.py <copy-of-data.db>
"""
import json, re, sqlite3, sys, urllib.parse

# ---- the single rule set ----------------------------------------------------------
SENSITIVE_TABLE = re.compile(r"sess|auth|cred|token|oauth|challenge|secret|device_code|audit|rate_limit|404_log|transfer|upload_attempt", re.I)
SENSITIVE_OPTION = re.compile(r"secret|salt|token|password|passwd|key|smtp|api|credential|private", re.I)
TRACE_COLUMNS = {"_emdash_comments": ["ip_hash", "user_agent", "moderation_metadata"], "_emdash_comment_reactions": ["voter_hash"]}
TRACE_KEYS = {"ip", "ip_hash", "ipaddress", "ip_address", "user_agent", "useragent", "visitor_ip", "remote_addr", "x_forwarded_for", "password", "token", "secret"}
ALLOWED_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@(([A-Za-z0-9-]+\.)*example(\.com)?|emdash\.local)$", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# -------------------------------------------------------------------------------------

def tables(db):
    return [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]

def clean_json(value):
    """Drop trace keys at any depth; visitor ids become a neutral placeholder."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k.lower() in TRACE_KEYS:
                continue
            out[k] = "model-visitor" if k.lower() == "visitor" and isinstance(v, str) and v else clean_json(v)
        return out
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    return value

def scrub(db):
    for t in tables(db):
        if SENSITIVE_TABLE.search(t):
            db.execute(f'DELETE FROM "{t}"')
    for (name,) in db.execute("SELECT name FROM options").fetchall():
        if SENSITIVE_OPTION.search(name):
            db.execute("DELETE FROM options WHERE name = ?", (name,))
    for t, cols in TRACE_COLUMNS.items():
        if t in tables(db):
            db.execute(f'UPDATE "{t}" SET ' + ", ".join(f'"{c}" = NULL' for c in cols))
    for rowid, data in db.execute("SELECT rowid, data FROM _plugin_storage").fetchall():
        try:
            parsed = json.loads(data)
        except (TypeError, ValueError):
            continue
        db.execute("UPDATE _plugin_storage SET data = ? WHERE rowid = ?", (json.dumps(clean_json(parsed)), rowid))
    db.commit()

def strings(value):
    """Every string inside a stored value: the value itself, decoded forms, and JSON contents."""
    if isinstance(value, bytes):
        value = value.decode("utf-8", "ignore")
    if not isinstance(value, str):
        return
    yield value
    yield urllib.parse.unquote(value)
    try:
        parsed = json.loads(value)
    except ValueError:
        return
    stack = [parsed]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for k, v in item.items():
                yield "KEY:" + str(k)
                stack.append(v)
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str):
            yield item

def verify(db):
    problems = []
    for t in tables(db):
        if SENSITIVE_TABLE.search(t) and db.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]:
            problems.append(f"table {t} still has rows")
    problems += [f"secret-like setting {n}" for (n,) in db.execute("SELECT name FROM options") if SENSITIVE_OPTION.search(n)]
    for t, cols in TRACE_COLUMNS.items():
        if t in tables(db):
            for c in cols:
                if db.execute(f'SELECT count(*) FROM "{t}" WHERE "{c}" IS NOT NULL AND "{c}" <> ""').fetchone()[0]:
                    problems.append(f"{t}.{c} still has values")
    for rowid, data in db.execute("SELECT rowid, data FROM _plugin_storage"):
        try:
            stack = [json.loads(data)]
        except (TypeError, ValueError):
            continue
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for k, v in item.items():
                    if k.lower() == "visitor" and v not in ("", "model-visitor", None):
                        problems.append("_plugin_storage: a visitor id is not the placeholder")
                    stack.append(v)
            elif isinstance(item, list):
                stack.extend(item)
    for t in tables(db):
        cols = [r[1] for r in db.execute(f'PRAGMA table_info("{t}")')]
        for row in db.execute(f'SELECT * FROM "{t}"'):
            for col, value in zip(cols, row):
                for s in strings(value):
                    if s.startswith("KEY:"):
                        if s[4:].lower() in TRACE_KEYS:
                            problems.append(f"{t}.{col}: key {s[4:]}")
                        continue
                    for email in EMAIL.findall(s):
                        if not ALLOWED_EMAIL.match(email):
                            problems.append(f"{t}.{col}: email {email}")
    return sorted(set(problems))

if __name__ == "__main__":
    db = sqlite3.connect(sys.argv[1])
    if len(sys.argv) < 3 or sys.argv[2] != "--verify-only":
        scrub(db)
    found = verify(db)
    db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    db.execute("PRAGMA journal_mode=DELETE")
    db.execute("VACUUM")
    db.close()
    if found:
        print("STOP: " + "; ".join(found[:20]), file=sys.stderr)
        sys.exit(1)
    print("Scrub check passed.")
