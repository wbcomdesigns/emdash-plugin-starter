"""Planted-case check for scrub.py: python3 -I model-site/test_scrub.py
Each case plants a value in a copy of the snapshot and expects scrub.py to clean it or stop.
"""
import os, tempfile
import json, shutil, sqlite3, subprocess, sys
M = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(tempfile.mkdtemp(), "scrubtest.db")
failed = False
def case(label, plant, expect_stop, after=None):
    shutil.copy(f"{M}/snapshot/data.db", T)
    db = sqlite3.connect(T); plant(db); db.commit(); db.close()
    r = subprocess.run(["python3", f"{M}/scrub.py", T], capture_output=True, text=True)
    extra = after(sqlite3.connect(T)) if after else ""
    ok = (r.returncode != 0) == expect_stop
    global failed
    failed = failed or not ok
    print(f"{'PASS' if ok else 'FAIL'} [{label}] exit {r.returncode} {r.stderr.strip()[:140]} {extra}")
def first_storage(db):
    return db.execute("select rowid, data from _plugin_storage where data like '{%' order by rowid limit 1").fetchone()
def put(db, key, value):
    rowid, data = first_storage(db); d = json.loads(data); d[key] = value
    db.execute("update _plugin_storage set data=? where rowid=?", (json.dumps(d), rowid))
case("email in JSON-in-JSON, double-encoded", lambda db: put(db, "note", {"inner": json.dumps({"contact": "jane%2540gmail.com"})}), True)
case("userAgent and clientIp keys cleaned", lambda db: put(db, "meta", {"userAgent": "Mozilla/5.0", "clientIp": "10.1.2.3"}), False,
     lambda db: "left=" + str(db.execute("select count(*) from _plugin_storage where data like '%userAgent%' or data like '%clientIp%'").fetchone()[0]))
case("unparseable JSON value", lambda db: db.execute("update ec_posts set excerpt='{\"a\": \"x}' where slug='small-tools-big-impact'"), True)
case("HTML-entity email in a post", lambda db: db.execute("update ec_posts set excerpt='mail jane&#64;gmail.com' where slug='small-tools-big-impact'"), True)
case("unknown table with rows is wiped", lambda db: (db.execute("create table secret_new(x text)"), db.execute("insert into secret_new values('jane@gmail.com')")), False,
     lambda db: "rows=" + str(db.execute("select count(*) from secret_new").fetchone()[0]))
case("visitor id not placeholder after cleaning", lambda db: put(db, "visitor", "abc123"), False,
     lambda db: "real-visitor-left=" + str(db.execute("select count(*) from _plugin_storage where data like '%abc123%'").fetchone()[0]))

sys.exit(1 if failed else 0)
