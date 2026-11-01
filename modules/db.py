import os, json, sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "sovereign_tasks.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS task_history (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT NOT NULL, payload TEXT, status TEXT NOT NULL, queued_at TEXT NOT NULL, completed_at TEXT, duration_sec REAL, error_msg TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS revenue_ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, customer_email TEXT, amount_cents INTEGER, status TEXT, created_at TEXT)")
    conn.close()

def record_task_queued(task_name, payload):
    conn = get_connection()
    with conn:
        cur = conn.execute("INSERT INTO task_history (task_name, payload, status, queued_at) VALUES (?, ?, ?, ?)", (task_name, json.dumps(payload or {}), "QUEUED", datetime.now().isoformat()))
        tid = cur.lastrowid
    conn.close()
    return tid

def record_task_completed(tid, dur):
    conn = get_connection()
    with conn:
        conn.execute("UPDATE task_history SET status = ?, completed_at = ?, duration_sec = ? WHERE id = ?", ("COMPLETED", datetime.now().isoformat(), dur, tid))
    conn.close()

def record_task_failed(tid, err, dur=0.0):
    conn = get_connection()
    with conn:
        conn.execute("UPDATE task_history SET status = ?, completed_at = ?, duration_sec = ?, error_msg = ? WHERE id = ?", ("FAILED", datetime.now().isoformat(), dur, str(err), tid))
    conn.close()

def record_task_cancelled(tid):
    conn = get_connection()
    with conn:
        conn.execute("UPDATE task_history SET status = ?, completed_at = ?, error_msg = ? WHERE id = ?", ("CANCELLED", datetime.now().isoformat(), "Purged", tid))
    conn.close()

def record_revenue(session_id, email, amount_cents, status="PAID"):
    conn = get_connection()
    with conn:
        conn.execute("INSERT INTO revenue_ledger (session_id, customer_email, amount_cents, status, created_at) VALUES (?, ?, ?, ?, ?)", (session_id, email, int(amount_cents), status, datetime.now().isoformat()))
    conn.close()

def get_revenue_summary():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total_cents, COUNT(*) AS tx_count FROM revenue_ledger WHERE status = ?", ("PAID",))
    row = dict(cur.fetchone())
    conn.close()
    return {"total_usd": round(row["total_cents"] / 100.0, 2), "transactions": row["tx_count"]}

def get_recent_tasks(limit=8):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_all_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_history ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

init_db()
