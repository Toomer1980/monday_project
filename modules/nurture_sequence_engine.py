import argparse
import datetime as dt
import os
import sqlite3
import sys

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DB_PATH = os.path.join(PDIR, "data", "nurture_crm.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "CREATE TABLE IF NOT EXISTS subscribers ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "email TEXT UNIQUE, name TEXT, source TEXT, step INTEGER DEFAULT 0, "
        "next_send_date TEXT, unsubscribed INTEGER DEFAULT 0, created_utc TEXT)"
    )
    c.commit()
    c.close()


def enroll_subscriber(email, name="Friend", source="store"):
    init_db()
    today = dt.date.today().isoformat()
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "INSERT OR IGNORE INTO subscribers (email, name, source, step, next_send_date, created_utc) VALUES (?,?,?,?,?,?)",
        (email.strip().lower(), name.strip() or "Friend", source, 0, today, dt.datetime.utcnow().isoformat() + "Z"),
    )
    c.commit()
    c.close()


def get_public_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "https://oraclesystemsllc.com"


def run_nurture(send_live=False):
    init_db()
    pub = get_public_url()
    today = dt.date.today()
    today_iso = today.isoformat()
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    due = c.execute(
        "SELECT * FROM subscribers WHERE unsubscribed=0 AND step < 3 AND next_send_date <= ? LIMIT 15",
        (today_iso,),
    ).fetchall()

    print(f"[PHASE 34] Nurture Engine ({'LIVE' if send_live else 'DRY-RUN'}) | Due today: {len(due)}")
    sent = 0
    for r in due:
        step = int(r["step"])
        name = r["name"] or "Friend"
        if step == 0:
            subj = "Welcome to the Living 3D Tarot Portal - Oracle Systems LLC"
            body = f"Hi {name},\n\nYour Living 3D Tarot Portal is open anytime:\n{pub}/store\n\nGrab the $15 Creator Asset Pack here:\n{pub}/go/assetpack15?utm_source=nurture&utm_medium=email&utm_campaign=day0\n\nReply UNSUBSCRIBE to opt out anytime.\nOracle Systems LLC\n"
            next_d = (today + dt.timedelta(days=2)).isoformat()
        elif step == 1:
            subj = "Your Custom 4D Aura Reading ($49) - Rendered With Your Name"
            body = f"Hi {name},\n\nReady for a bespoke multi-chapter reading rendered specifically for your focus topic with warm studio narration?\nOrder here: {pub}/go/auravideo49?utm_source=nurture&utm_medium=email&utm_campaign=day2\n\nReply UNSUBSCRIBE to opt out anytime.\nOracle Systems LLC\n"
            next_d = (today + dt.timedelta(days=3)).isoformat()
        else:
            subj = "Unlock Unlimited Full Readings Inside the $15/mo Sovereign Vault"
            body = f"Hi {name},\n\nStep inside the monthly Sovereign Member Vault for unlimited full-length readings and ad-free studio audio drops:\n{pub}/go/vaultsub15?utm_source=nurture&utm_medium=email&utm_campaign=day5\n\nReply UNSUBSCRIBE to opt out anytime.\nOracle Systems LLC\n"
            next_d = "2099-12-31"

        if send_live:
            sys.path.insert(0, os.path.join(PDIR, "Modules"))
            from google_mail_engine import send_oracle_email
            via = send_oracle_email(PDIR, r["email"], subj, body)
            c.execute("UPDATE subscribers SET step=?, next_send_date=? WHERE id=?", (step + 1, next_d, r["id"]))
            c.commit()
            sent += 1
            print(f"  [NURTURE SENT] Step {step+1}/3 -> {r['email']} via {via}")
        else:
            print(f"  [NURTURE PREVIEW] Step {step+1}/3 -> {r['email']} | {subj}")
    c.close()
    print(f"[PHASE 34 PASS] Processed {len(due)} due nurture record(s) (sent: {sent})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--enroll-test", action="store_true")
    args = ap.parse_args()
    init_db()
    if args.enroll_test:
        enroll_subscriber("Toomer1980@gmail.com", "Thomas", "internal_verify")
    run_nurture(send_live=args.live)
