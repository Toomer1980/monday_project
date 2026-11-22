import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import datetime as dt
import json
import sqlite3
import subprocess
import sys

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DB_PATH = os.path.join(PDIR, "data", "aura49_orders.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "CREATE TABLE IF NOT EXISTS aura_orders ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "order_ref TEXT UNIQUE, customer_name TEXT, customer_email TEXT, "
        "focus_topic TEXT, voice_accent TEXT DEFAULT 'Irish', "
        "status TEXT DEFAULT 'PENDING_PAYMENT', video_path TEXT DEFAULT '', "
        "download_token TEXT DEFAULT '', created_utc TEXT, fulfilled_utc TEXT DEFAULT '')"
    )
    c.commit()
    c.close()


def queue_intake(name, email, focus_topic, accent="Irish", status="PENDING_PAYMENT"):
    init_db()
    ref = "AURA49-" + dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "INSERT OR IGNORE INTO aura_orders (order_ref, customer_name, customer_email, focus_topic, voice_accent, status, created_utc) "
        "VALUES (?,?,?,?,?,?,?)",
        (ref, (name or "Seeker").strip()[:60], (email or "").strip().lower(), (focus_topic or "Abundance & Alignment").strip()[:120],
         "Australian" if str(accent).lower().startswith("aus") else "Irish", status, dt.datetime.utcnow().isoformat() + "Z"),
    )
    c.commit()
    c.close()
    return ref


def process_paid_queue(limit=2):
    init_db()
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    rows = c.execute("SELECT * FROM aura_orders WHERE status='PAID_QUEUED' ORDER BY id ASC LIMIT ?", (limit,)).fetchall()
    if not rows:
        c.close()
        print("[PHASE 44] 0 PAID_QUEUED custom $49 Aura readings waiting right now.")
        return 0

    sys.path.insert(0, os.path.join(PDIR, "Modules"))
    from license_fulfillment_engine import issue_license
    from google_mail_engine import send_oracle_email

    pub_p = os.path.join(PDIR, "config", "public_url.txt")
    pub = open(pub_p, "r", encoding="utf-8").read().strip().rstrip("/") if os.path.exists(pub_p) else "https://oraclesystemsllc.com"

    done = 0
    for r in rows:
        topic = f"{r['customer_name']} - {r['focus_topic']}"
        res = subprocess.run([
            sys.executable, os.path.join(PDIR, "Modules", "render_real_full_reading.py"),
            "--week", str(90 + int(r["id"])), "--topic", topic, "--target-minutes", "3", "--accent", r["voice_accent"],
        ])
        if res.returncode == 0:
            lic = issue_license(r["order_ref"], r["customer_email"], "assetpack15", ttl_hours=168)
            subj = f"Your Custom Living-3D Aura Reading Is Ready ({r['order_ref']}) - Oracle Systems LLC"
            body = (
                f"Hi {r['customer_name']},\n\n"
                f"Your custom Living-3D Aura Reading on '{r['focus_topic']}' has finished rendering with warm {r['voice_accent']} studio narration.\n\n"
                f"- Order Reference: {r['order_ref']}\n"
                f"- Member Portal Access: {pub}/portal\n"
                f"- Verified License Token: {lic['token']}\n\n"
                f"Thank you for choosing Oracle Systems LLC.\n"
            )
            try:
                if "@" in r["customer_email"]:
                    send_oracle_email(PDIR, r["customer_email"], subj, body)
            except Exception as ex:
                print(f"[PHASE 44 WARN] Email delivery note: {ex}")
            c.execute(
                "UPDATE aura_orders SET status='FULFILLED', download_token=?, fulfilled_utc=? WHERE id=?",
                (lic["token"], dt.datetime.utcnow().isoformat() + "Z", r["id"]),
            )
            c.commit()
            done += 1
            print(f"[PHASE 44 FULFILLED] {r['order_ref']} -> {r['customer_email']}")
    c.close()
    return done


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--process-queue", action="store_true")
    args = ap.parse_args()
    init_db()
    if args.process_queue:
        process_paid_queue()
    else:
        print(f"[PHASE 44 PASS] Hands-Free $49 Personalized Aura Intake & Fulfillment DB ready -> {DB_PATH}")
