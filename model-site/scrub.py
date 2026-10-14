#!/usr/bin/env python3
"""Clean a copy of the showcase database for the model-site snapshot, then verify it.

Fail closed:
- Only tables on ALLOWED_TABLES may hold rows. A new table with rows (a future EmDash or
  plugin table) stops the snapshot until someone reviews it and adds it here.
- One rule set drives both the cleaning and the check.
- The check reads stored values: every string is decoded (percent-encoding and HTML entities,
  repeatedly), and JSON inside it is parsed at any depth, including JSON stored in JSON strings.
  A value that looks like JSON but does not parse is a finding, never skipped.
Usage: scrub.py <copy-of-data.db> [--verify-only]
"""
import html, json, re, sqlite3, sys, urllib.parse

# ---- the single rule set ----------------------------------------------------------
ALLOWED_TABLES = {
    "_emdash_bylines", "_emdash_collections", "_emdash_comments", "_emdash_content_bylines",
    "_emdash_cron_tasks", "_emdash_fields", "_emdash_media_usage", "_emdash_media_usage_activation",
    "_emdash_media_usage_cleanup", "_emdash_media_usage_index_status", "_emdash_media_usage_sources",
    "_emdash_media_usage_work", "_emdash_menu_items", "_emdash_menus", "_emdash_migrations",
    "_emdash_migrations_lock", "_emdash_redirect_state", "_emdash_redirect_write_lock",
    "_emdash_sections", "_emdash_taxonomy_def_groups", "_emdash_taxonomy_defs",
    "_emdash_widget_areas", "_emdash_widgets", "_plugin_indexes", "_plugin_state", "_plugin_storage",
    "content_taxonomies", "media", "options", "revisions", "taxonomies", "users",
}
CONTENT_TABLE = re.compile(r"^ec_[a-z0-9_]+$")          # one table per content type
SEARCH_INDEX = re.compile(r"^_emdash_fts_[a-z0-9_]+$")  # derived copies of content, never edited
SENSITIVE_OPTION = re.compile(r"secret|salt|token|password|passwd|key|smtp|api|credential|private|session|cookie", re.I)
TRACE_COLUMNS = {"_emdash_comments": ["ip_hash", "user_agent", "moderation_metadata"]}
TRACE_KEY_EXACT = {"ip", "ipaddress", "iphash", "clientip", "remoteip", "userip", "visitorip", "remoteaddr",
                   "xforwardedfor", "forwardedfor", "xrealip", "cfconnectingip", "voterhash", "fingerprint"}
TRACE_KEY_PART = ("useragent", "password", "passwd", "secret", "token", "salt", "sessionid", "cookie",
                  "authorization", "apikey", "privatekey")
VISITOR_KEYS = {"visitor", "visitorid", "visitortoken", "anonid"}
VISITOR_PLACEHOLDER = "model-visitor"
ALLOWED_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@(([A-Za-z0-9-]+\.)*example(\.com)?|emdash\.local)$", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# -------------------------------------------------------------------------------------

def norm(key):
    return re.sub(r"[^a-z0-9]", "", str(key).lower())

def is_trace_key(key):
    n = norm(key)
    return n in TRACE_KEY_EXACT or any(part in n for part in TRACE_KEY_PART)

def looks_json(s):
    s = s.strip()
    return len(s) > 1 and s[0] in "[{" and s[-1] in "]}"

def decode(s):
    """Percent-encoding and HTML entities, repeated until nothing changes (max 5 rounds)."""
    for _ in range(5):
        nxt = html.unescape(urllib.parse.unquote(s))
        if nxt == s:
            break
        s = nxt
    return s

def clean_value(value):
    """Clean a decoded Python value: drop trace keys, neutralise visitor ids, recurse into JSON strings."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if is_trace_key(k):
                continue
            if norm(k) in VISITOR_KEYS and isinstance(v, str) and v:
                out[k] = VISITOR_PLACEHOLDER
                continue
            out[k] = clean_value(v)
        return out
    if isinstance(value, list):
        return [clean_value(v) for v in value]
    if isinstance(value, str) and looks_json(value):
        try:
            return json.dumps(clean_value(json.loads(value)))
        except ValueError:
            return value  # left for verify() to report
    return value

def tables(db):
    return [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]

def text_columns(db, table):
    return [r[1] for r in db.execute(f'PRAGMA table_info("{table}")') if (r[2] or "").upper() in ("", "TEXT", "JSON")]

def scrub(db):
    for t in tables(db):
        if t not in ALLOWED_TABLES and not CONTENT_TABLE.match(t) and not SEARCH_INDEX.match(t):
            db.execute(f'DELETE FROM "{t}"')
    for (name,) in db.execute("SELECT name FROM options").fetchall():
        if SENSITIVE_OPTION.search(name):
            db.execute("DELETE FROM options WHERE name = ?", (name,))
    for t, cols in TRACE_COLUMNS.items():
        db.execute(f'UPDATE "{t}" SET ' + ", ".join(f'"{c}" = NULL' for c in cols))
    for t in tables(db):
        if SEARCH_INDEX.match(t):
            continue
        for col in text_columns(db, t):
            for rowid, value in db.execute(f'SELECT rowid, "{col}" FROM "{t}"').fetchall():
                if isinstance(value, str) and looks_json(value):
                    try:
                        cleaned = json.dumps(clean_value(json.loads(value)))
                    except ValueError:
                        continue  # verify() reports it
                    if cleaned != value:
                        db.execute(f'UPDATE "{t}" SET "{col}" = ? WHERE rowid = ?', (cleaned, rowid))
    db.commit()

def walk(value, where, problems, depth=0):
    """Report trace keys, non-placeholder visitor ids, stray emails and unparseable JSON."""
    if depth > 20:
        problems.append(f"{where}: nested too deep to check")
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if is_trace_key(k):
                problems.append(f"{where}: key {k}")
            if norm(k) in VISITOR_KEYS and v not in ("", VISITOR_PLACEHOLDER, None):
                problems.append(f"{where}: visitor id {k} is not the placeholder")
            walk(v, where, problems, depth + 1)
    elif isinstance(value, list):
        for v in value:
            walk(v, where, problems, depth + 1)
    elif isinstance(value, (str, bytes)):
        s = value.decode("utf-8", "ignore") if isinstance(value, bytes) else value
        for form in {s, decode(s)}:
            for email in EMAIL.findall(form):
                if not ALLOWED_EMAIL.match(email):
                    problems.append(f"{where}: email {email}")
            if looks_json(form):
                try:
                    walk(json.loads(form), where, problems, depth + 1)
                except ValueError:
                    problems.append(f"{where}: value looks like JSON but does not parse")

def verify(db):
    problems = []
    for t in tables(db):
        allowed = t in ALLOWED_TABLES or CONTENT_TABLE.match(t) or SEARCH_INDEX.match(t)
        if not allowed and db.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]:
            problems.append(f"table {t} has rows and is not on the allowlist")
    problems += [f"secret-like setting {n}" for (n,) in db.execute("SELECT name FROM options") if SENSITIVE_OPTION.search(n)]
    for t, cols in TRACE_COLUMNS.items():
        for c in cols:
            if db.execute(f'SELECT count(*) FROM "{t}" WHERE "{c}" IS NOT NULL AND "{c}" <> ""').fetchone()[0]:
                problems.append(f"{t}.{c} still has values")
    for t in tables(db):
        cols = [r[1] for r in db.execute(f'PRAGMA table_info("{t}")')]
        for row in db.execute(f'SELECT * FROM "{t}"'):
            for col, value in zip(cols, row):
                if SEARCH_INDEX.match(t) and isinstance(value, bytes):
                    # Binary search-index pages: only look for addresses, never parse.
                    for email in EMAIL.findall(value.decode("utf-8", "ignore")):
                        if not ALLOWED_EMAIL.match(email):
                            problems.append(f"{t}.{col}: email {email}")
                    continue
                walk(value, f"{t}.{col}", problems)
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
        print("STOP: " + "; ".join(found[:25]), file=sys.stderr)
        sys.exit(1)
    print("Scrub check passed.")
