import os, json, sqlite3
from datetime import datetime
BASE = "C:/Users/toome/Desktop/SovereignCore"
if os.name != "nt" or not os.path.exists(BASE):
    BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE, "data", "sovereign_tasks.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS task_history (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT NOT NULL, payload TEXT, status TEXT NOT NULL, queued_at TEXT NOT NULL, completed_at TEXT, duration_sec REAL, error_msg TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS revenue_ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, customer_email TEXT, amount_cents INTEGER, status TEXT, created_at TEXT, product_sku TEXT, product_name TEXT, license_key TEXT, download_token TEXT)")
        for col in ["product_sku TEXT", "product_name TEXT", "license_key TEXT", "download_token TEXT"]:
            try: conn.execute(f"ALTER TABLE revenue_ledger ADD COLUMN {col}")
            except Exception: pass
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
    with conn: conn.execute("UPDATE task_history SET status=?, completed_at=?, duration_sec=? WHERE id=?", ("COMPLETED", datetime.now().isoformat(), dur, tid))
    conn.close()

def record_task_failed(tid, err, dur=0.0):
    conn = get_connection()
    with conn: conn.execute("UPDATE task_history SET status=?, completed_at=?, duration_sec=?, error_msg=? WHERE id=?", ("FAILED", datetime.now().isoformat(), dur, str(err), tid))
    conn.close()

def record_task_cancelled(tid):
    conn = get_connection()
    with conn: conn.execute("UPDATE task_history SET status=?, completed_at=?, error_msg=? WHERE id=?", ("CANCELLED", datetime.now().isoformat(), "Purged", tid))
    conn.close()

def record_revenue(session_id, email, amount_cents, status="PAID", sku="pro_node", product_name="SovereignCore Pro", license_key="", download_token=""):
    conn = get_connection()
    with conn:
        conn.execute("INSERT INTO revenue_ledger (session_id, customer_email, amount_cents, status, created_at, product_sku, product_name, license_key, download_token) VALUES (?,?,?,?,?,?,?,?,?)",
                     (session_id, email, int(amount_cents), status, datetime.now().isoformat(), sku, product_name, license_key, download_token))
    conn.close()

def get_order_by_token(tok):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM revenue_ledger WHERE download_token=? OR session_id=? OR license_key=? ORDER BY id DESC LIMIT 1", (tok, tok, tok))
    r = cur.fetchone()
    conn.close()
    return dict(r) if r else None

def get_recent_orders(limit=6):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM revenue_ledger ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_revenue_summary():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(amount_cents),0) AS c, COUNT(*) AS n FROM revenue_ledger WHERE status=?", ("PAID",))
    r = dict(cur.fetchone())
    conn.close()
    usd, tx = round(r["c"]/100.0, 2), r["n"]
    return {"total_usd": usd, "transactions": tx, "aov_usd": round(usd/tx, 2) if tx else 0.0}

def get_recent_tasks(limit=6):
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
