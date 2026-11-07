import os, sys

CORE = r"C:\Users\toome\Desktop\SovereignCore"
PROJ = r"C:\Users\toome\monday_project"
for b in [CORE, PROJ]:
    for s in ["data", "data/backups", "data/reports", "data/assets", "config", "modules", "logs", ".github/workflows"]:
        os.makedirs(os.path.join(b, s), exist_ok=True)

def wboth(rel, txt):
    for b in [CORE, PROJ]:
        with open(os.path.join(b, rel), "w", encoding="utf-8", newline="\n") as f:
            f.write(txt.strip() + "\n")

wboth("modules/db.py", '''
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
''')

for b in [CORE, PROJ]:
    vp = os.path.join(b, "modules", "vault.py")
    vt = open(vp, "r", encoding="utf-8").read()
    if "__main__" not in vt:
        vt += '\nif __name__ == "__main__":\n    import sys\n    if len(sys.argv)>=4 and sys.argv[1]=="set": set_secret(sys.argv[2], sys.argv[3]); print(f"[VAULT] Encrypted {sys.argv[2]}")\n    elif len(sys.argv)>=3 and sys.argv[1]=="get": print(get_secret(sys.argv[2]) or "")\n    elif len(sys.argv)>=2 and sys.argv[1]=="list": print(list_secret_keys())\n'
        open(vp, "w", encoding="utf-8").write(vt)

wboth("modules/revenue_engine.py", '''
import os, sys, uuid, json, zipfile, logging, smtplib
from email.message import EmailMessage
from datetime import datetime
BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "modules"))
import db, vault
ASSET_DIR = os.path.join(BASE_DIR, "data", "assets")
os.makedirs(ASSET_DIR, exist_ok=True)
CATALOG = {
    "guide_52wk": {"sku":"guide_52wk", "name":"Oracle 52-Week Collective Reading & Media Blueprint", "price_cents":2900, "badge":"DIGITAL BUNDLE", "desc":"52-week 30-min collective reading scripts, viral hooks, daily schedule & monetization guide."},
    "pro_node": {"sku":"pro_node", "name":"SovereignCore Pro Automation Node License", "price_cents":9900, "badge":"PRO SOFTWARE", "desc":"4-worker thread swarm engine, DPAPI encryption vault, telemetry exporter & lifetime Pro license key."},
    "creator_suite": {"sku":"creator_suite", "name":"Oracle Studio & Merchandising Automation Suite", "price_cents":24900, "badge":"CREATOR ENGINE", "desc":"Automated studio batch workflows, high-margin merchandise launch templates (apparel & mugs) & funnels."},
    "enterprise_swarm": {"sku":"enterprise_swarm", "name":"Oracle Systems Enterprise Custom Swarm Deployment", "price_cents":150000, "badge":"ENTERPRISE TIER", "desc":"Full dual-cloud enterprise deployment, custom Stripe revenue engine, priority webhooks & commercial license."}
}
def build_customer_bundle(info):
    os.makedirs(ASSET_DIR, exist_ok=True)
    zp = os.path.join(ASSET_DIR, f"Oracle_Bundle_{info['download_token']}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("01_LICENSE_CERTIFICATE.txt", f"ORACLE SYSTEMS LLC // VERIFIED LICENSE\nProduct: {info['product_name']}\nCustomer: {info['email']}\nLicense Key: {info['license_key']}\nOrder ID: {info['session_id']}\nAmount: ${info['amount_cents']/100:.2f} USD\nIssued: {datetime.now().isoformat()}\n")
        zf.writestr("02_52_WEEK_MEDIA_AND_REVENUE_BLUEPRINT.md", "# ORACLE SYSTEMS 52-WEEK MEDIA & $1,500/DAY REVENUE BLUEPRINT\n1. 00:00-02:30 Hook & Energy Theme\n2. 02:30-12:00 Past Foundation\n3. 12:00-22:00 Turning Point\n4. 22:00-30:00 Extended Reading & Storefront CTA (/store)\n")
        zf.writestr("03_SOVEREIGN_NODE_CONFIG.json", json.dumps({"org":"Oracle Systems LLC","license_key":info["license_key"],"sku":info["sku"],"workers":4,"verified":True}, indent=2))
    return zp
def process_successful_checkout(sess):
    cust, meta = sess.get("customer_details") or {}, sess.get("metadata") or {}
    sku = meta.get("sku", "pro_node")
    prod = CATALOG.get(sku, CATALOG["pro_node"])
    email = cust.get("email") or meta.get("email") or "client@oraclesystems.io"
    amt = int(sess.get("amount_total") or prod["price_cents"])
    sid = sess.get("id") or f"ord_{uuid.uuid4().hex[:8]}"
    lkey = "ORCL-" + "-".join(uuid.uuid4().hex[:4].upper() for _ in range(4))
    dtok = f"tok_{uuid.uuid4().hex}"
    info = {"session_id":sid, "email":email, "amount_cents":amt, "sku":sku, "product_name":prod["name"], "license_key":lkey, "download_token":dtok}
    db.record_revenue(sid, email, amt, "PAID", sku, prod["name"], lkey, dtok)
    build_customer_bundle(info)
    logging.info(f"[REVENUE ENGINE] Fulfilled {prod['name']} (${amt/100:.2f}) | Key: {lkey}")
    return info
''')
print("[+] Block 1 Complete: Database, Vault CLI & Multi-Tier ZIP Engine Ready!")