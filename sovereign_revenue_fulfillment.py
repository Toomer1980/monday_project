import os, json, time, sqlite3, smtplib, threading, hashlib
from datetime import datetime
from email.message import EmailMessage

ROOT = "C:/Users/toome/Desktop/SovereignCore"
LEADS_DB = ROOT + "/data/leads.db"
ORDERS_DB = ROOT + "/data/fulfillment_queue.db"
EVO_DB = ROOT + "/data/evolution_memory.db"
DELIV_DIR = ROOT + "/static/deliverables"
LOG_FILE = ROOT + "/logs/revenue_fulfillment.log"
os.makedirs(ROOT + "/data", exist_ok=True)
os.makedirs(DELIV_DIR, exist_ok=True)

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try: open(LOG_FILE, "a", encoding="utf-8").write(line + "\n")
    except Exception: pass

def init_dbs():
    c1 = sqlite3.connect(LEADS_DB, timeout=30.0)
    c1.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, name TEXT, focus TEXT, portrait_url TEXT, aura_hex TEXT, converted INTEGER DEFAULT 0, ts TEXT)")
    c1.commit(); c1.close()
    c2 = sqlite3.connect(ORDERS_DB, timeout=30.0)
    c2.execute("CREATE TABLE IF NOT EXISTS orders (session_id TEXT PRIMARY KEY, sku TEXT, email TEXT, name TEXT, focus TEXT, portrait_url TEXT, aura_hex TEXT, amount_usd REAL, status TEXT, download_url TEXT, created_at TEXT, completed_at TEXT)")
    c2.commit(); c2.close()

def capture_lead(email, name="", focus="", portrait_url="", aura_hex="#38bdf8"):
    init_dbs()
    c = sqlite3.connect(LEADS_DB, timeout=30.0)
    c.execute("INSERT INTO leads (email, name, focus, portrait_url, aura_hex, ts) VALUES (?, ?, ?, ?, ?, ?)", (email.strip(), name[:60], focus[:200], portrait_url[:200], aura_hex[:16], datetime.now().isoformat()))
    c.commit(); c.close()
    log(f"[LEAD] Captured: {email} | Focus: {focus[:50]}")

def reward_evolution_with_sale(amount_usd):
    if not os.path.exists(EVO_DB): return
    try:
        c = sqlite3.connect(EVO_DB, timeout=30.0)
        c.execute("UPDATE genomes SET conversions = conversions + 1, revenue_usd = revenue_usd + ? WHERE active = 1", (float(amount_usd),))
        c.commit(); c.close()
        log(f"[EVOLUTION-FEEDBACK] Rewarded active genomes with +${amount_usd:.2f} real conversion.")
    except Exception as e:
        log(f"[EVOLUTION-FEEDBACK] Note: {e}")

def send_delivery_email(to_email, subject, body):
    pwd = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    if not pwd:
        log(f"[EMAIL-QUEUED] Set GMAIL_APP_PASSWORD to auto-send email to {to_email}: {subject}")
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = subject; msg["From"] = "Toomer1980@gmail.com"; msg["To"] = to_email
        msg.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as s:
            s.login("Toomer1980@gmail.com", pwd)
            s.send_message(msg)
        log(f"[EMAIL-SENT] Delivered to {to_email}: {subject}")
        return True
    except Exception as e:
        log(f"[EMAIL-ERR] {e}"); return False

def fulfill_order_worker(session_id):
    init_dbs()
    c = sqlite3.connect(ORDERS_DB, timeout=30.0)
    row = c.execute("SELECT sku, email, name, focus, portrait_url, aura_hex, amount_usd, status FROM orders WHERE session_id=?", (session_id,)).fetchone()
    c.close()
    if not row or row[7] == "COMPLETED": return
    sku, email, name, focus, portrait_url, aura_hex, amount_usd, _ = row
    store_base = open(ROOT + "/CURRENT_STORE_URL.txt").read().strip().replace("/store", "") if os.path.exists(ROOT + "/CURRENT_STORE_URL.txt") else "http://127.0.0.1:8000"
    dl_url = f"{store_base}/portal?session_id={session_id}"
    if sku == "personal_3d_video":
        try:
            import oracle_3d_renderer, oracle_art_factory
            oid = hashlib.md5(session_id.encode()).hexdigest()[:10]
            out_mp4 = f"{DELIV_DIR}/oracle_3d_{oid}.mp4"
            oracle_art_factory.ensure_card_art("The Tower"); oracle_art_factory.ensure_card_art("The Star"); oracle_art_factory.ensure_card_art("Ace of Pentacles")
            spoken = f"Welcome {name or 'Sovereign Seeker'}. Your personalized three-D Oracle reading is ready. Regarding {focus or 'your next major breakthrough'}, The Tower clears outdated limits, The Star pours clarity into your present step, and the Ace of Pentacles anchors tangible abundance arriving over the next seventy-two hours."
            oracle_3d_renderer.render_3d_video(out_mp4, focus or "Personalized Breakthrough", "The Tower", "The Star", "Ace of Pentacles", spoken, kicker=f"PERSONALIZED 3D READING // {(name or 'SOVEREIGN').upper()}", aura=aura_hex or "#38bdf8", portrait_url=portrait_url or "", mode="1080p")
            dl_url = f"{store_base}/static/deliverables/oracle_3d_{oid}.mp4"
        except Exception as e:
            log(f"[FULFILL-ERR] {session_id}: {e}")
    c = sqlite3.connect(ORDERS_DB, timeout=30.0)
    c.execute("UPDATE orders SET status='COMPLETED', download_url=?, completed_at=? WHERE session_id=?", (dl_url, datetime.now().isoformat(), session_id))
    c.commit(); c.close()
    send_delivery_email(email, "Your Oracle Systems Digital Delivery Is Ready", f"Thank you for your order ({sku}, ${amount_usd:.2f}).\n\nAccess your download here:\n{dl_url}\n\n- Oracle Systems LLC")
    send_delivery_email("Toomer1980@gmail.com", f"[LIVE SALE +${amount_usd:.2f}] {sku}", f"Buyer: {email}\nSKU: {sku}\nAmount: ${amount_usd:.2f}\nDelivered URL: {dl_url}")
    log(f"[FULFILLED] {session_id} -> {dl_url}")

def enqueue_paid_order(session_id, sku, email, amount_usd, meta=None):
    init_dbs(); meta = meta or {}
    c = sqlite3.connect(ORDERS_DB, timeout=30.0)
    exists = c.execute("SELECT status FROM orders WHERE session_id=?", (session_id,)).fetchone()
    if exists: c.close(); return False
    c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (session_id, sku, email, meta.get("name",""), meta.get("focus",""), meta.get("portrait_url",""), meta.get("aura_hex","#38bdf8"), float(amount_usd), "PENDING", "", datetime.now().isoformat(), ""))
    c.commit(); c.close()
    cL = sqlite3.connect(LEADS_DB, timeout=30.0)
    cL.execute("UPDATE leads SET converted=1 WHERE email=?", (email,)); cL.commit(); cL.close()
    reward_evolution_with_sale(amount_usd)
    threading.Thread(target=fulfill_order_worker, args=(session_id,), daemon=True).start()
    return True

def process_pending_orders():
    init_dbs()
    c = sqlite3.connect(ORDERS_DB, timeout=30.0)
    rows = c.execute("SELECT session_id FROM orders WHERE status='PENDING'").fetchall()
    c.close()
    for (sid,) in rows: fulfill_order_worker(sid)

def get_dashboard():
    init_dbs()
    c1 = sqlite3.connect(LEADS_DB, timeout=30.0); leads_cnt = c1.execute("SELECT COUNT(*) FROM leads").fetchone()[0]; c1.close()
    c2 = sqlite3.connect(ORDERS_DB, timeout=30.0)
    tot = c2.execute("SELECT COUNT(*), COALESCE(SUM(amount_usd), 0.0) FROM orders").fetchone()
    pend = c2.execute("SELECT COUNT(*) FROM orders WHERE status='PENDING'").fetchone()[0]; c2.close()
    return {"leads_captured": leads_cnt, "paid_orders": tot[0], "verified_revenue_usd": round(tot[1], 2), "pending_fulfillments": pend}

if __name__ == "__main__":
    init_dbs(); print("[+] Revenue Fulfillment & Lead Engine ready:", json.dumps(get_dashboard()))
