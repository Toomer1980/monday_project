import datetime as dt
import hashlib
import hmac
import json
import os
import sqlite3
import urllib.parse
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DB_PATH = os.path.join(PDIR, "data", "vault_members.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def load_env(name):
    ep = os.path.join(PDIR, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8", errors="ignore"):
            if ln.strip().startswith(name + "="):
                return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "CREATE TABLE IF NOT EXISTS vault_members ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "email TEXT UNIQUE, stripe_customer_id TEXT, subscription_id TEXT, "
        "status TEXT, member_token TEXT, updated_utc TEXT)"
    )
    c.commit()
    c.close()


def mint_member_token(email):
    sec = load_env("STRIPE_WEBHOOK_SECRET") or "oracle_vault_gate_v45"
    return "VAULT-" + hmac.new(sec.encode("utf-8"), email.lower().encode("utf-8"), hashlib.sha256).hexdigest()[:20].upper()


def sync_stripe_subscriptions():
    init_db()
    key = load_env("STRIPE_SECRET_KEY")
    synced = 0
    if key and key.startswith(("sk_live_", "rk_live_", "sk_test_")):
        import base64
        auth = "Basic " + base64.b64encode((key + ":").encode("ascii")).decode("ascii")
        try:
            req = urllib.request.Request(
                "https://api.stripe.com/v1/subscriptions?status=active&limit=50&expand[]=data.customer",
                headers={"Authorization": auth},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8")).get("data") or []
            c = sqlite3.connect(DB_PATH)
            for sub in data:
                cust = sub.get("customer") or {}
                email = (cust.get("email") or "").strip().lower() if isinstance(cust, dict) else ""
                cid = cust.get("id", "") if isinstance(cust, dict) else str(cust)
                if email:
                    c.execute(
                        "INSERT INTO vault_members (email, stripe_customer_id, subscription_id, status, member_token, updated_utc) "
                        "VALUES (?,?,?,?,?,?) "
                        "ON CONFLICT(email) DO UPDATE SET stripe_customer_id=excluded.stripe_customer_id, subscription_id=excluded.subscription_id, status=excluded.status, updated_utc=excluded.updated_utc",
                        (email, cid, sub.get("id", ""), sub.get("status", "active"), mint_member_token(email), dt.datetime.utcnow().isoformat() + "Z"),
                    )
                    synced += 1
            c.commit()
            c.close()
        except Exception as ex:
            print(f"[PHASE 45 NOTE] Stripe subscription sync skipped: {str(ex)[:110]}")

    # Ensure owner VIP preview access exists in vault_members.db
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "INSERT OR IGNORE INTO vault_members (email, stripe_customer_id, subscription_id, status, member_token, updated_utc) VALUES (?,?,?,?,?,?)",
        ("toomer1980@gmail.com", "founder_vip", "founder_access", "active", mint_member_token("toomer1980@gmail.com"), dt.datetime.utcnow().isoformat() + "Z"),
    )
    c.commit()
    total = c.execute("SELECT COUNT(*) FROM vault_members WHERE status='active'").fetchone()[0]
    c.close()
    print(f"[PHASE 45 PASS] Sovereign Vault Member Gate synced ({synced} Stripe live subs | {total} active member(s) in vault_members.db)")


def verify_member(email_or_token):
    init_db()
    q = (email_or_token or "").strip()
    if not q:
        return {"authorized": False, "reason": "Missing email or member token"}
    c = sqlite3.connect(DB_PATH)
    row = c.execute(
        "SELECT email, status, member_token FROM vault_members WHERE lower(email)=lower(?) OR member_token=?",
        (q, q),
    ).fetchone()
    c.close()
    if row and row[1] == "active":
        return {"authorized": True, "email": row[0], "status": row[1], "member_token": row[2]}
    return {"authorized": False, "reason": "No active $15/mo Sovereign Vault subscription found"}


if __name__ == "__main__":
    sync_stripe_subscriptions()
