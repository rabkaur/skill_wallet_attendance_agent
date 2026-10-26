import sqlite3, threading, csv, io, os
import config
_lock = threading.Lock()

def _conn():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    c = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def reset():
    with _lock, _conn() as c:
        c.executescript("""
        DROP TABLE IF EXISTS attendance; DROP TABLE IF EXISTS engagement; DROP TABLE IF EXISTS suggestions;
        CREATE TABLE attendance(student_id TEXT PRIMARY KEY, marked_at TEXT, last_seen TEXT, present_seconds REAL);
        CREATE TABLE engagement(ts TEXT, score REAL, attention REAL, inactivity REAL, audio REAL, students INTEGER);
        CREATE TABLE suggestions(ts TEXT, text TEXT);""")

def upsert_attendance(sid, marked_at, last_seen, secs):
    with _lock, _conn() as c:
        c.execute("""INSERT INTO attendance VALUES(?,?,?,?) ON CONFLICT(student_id)
                     DO UPDATE SET last_seen=?, present_seconds=?""", (sid, marked_at, last_seen, secs, last_seen, secs))

def add_window(ts, w):
    with _lock, _conn() as c:
        c.execute("INSERT INTO engagement VALUES(?,?,?,?,?,?)",
                  (ts, w["score"], w["attention"], w["inactivity"], w["audio"], w["students"]))

def add_suggestions(ts, items):
    with _lock, _conn() as c:
        c.executemany("INSERT INTO suggestions VALUES(?,?)", [(ts, t) for t in items])

def rows(table):
    with _lock, _conn() as c:
        return [dict(r) for r in c.execute(f"SELECT * FROM {table}")]

def attendance_csv():
    out = io.StringIO(); r = rows("attendance")
    w = csv.writer(out); w.writerow(["student_id", "marked_at", "last_seen", "present_seconds"])
    for x in r: w.writerow([x["student_id"], x["marked_at"], x["last_seen"], round(x["present_seconds"], 1)])
    return out.getvalue()
