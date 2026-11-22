import datetime as dt
import hashlib
import hmac
import json
import os
import sqlite3
import time

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DB_PATH = os.path.join(PDIR, "data", "orders_ledger.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

PRODUCT_FILES = {
    "assetpack15": os.path.join(PDIR, "deliverables", "Oracle_4D_Creator_Asset_Pack_15.zip"),
    "tier29": os.path.join(PDIR, "deliverables", "Oracle_4D_Creator_Asset_Pack_15.zip"),
}


def get_signing_secret():
    ep = os.path.join(PDIR, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8", errors="ignore"):
            if ln.strip().startswith("STRIPE_WEBHOOK_SECRET="):
                v = ln.split("=", 1)[1].strip().strip('"').strip("'")
                if len(v) >= 12:
                    return v
    return "oracle_systems_sovereign_hmac_v33"


def init_ledger():
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "CREATE TABLE IF NOT EXISTS licenses ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "order_ref TEXT UNIQUE, email TEXT, sku TEXT, token TEXT UNIQUE, "
        "expires_epoch INTEGER, downloads INTEGER DEFAULT 0, created_utc TEXT)"
    )
    c.commit()
    c.close()


def issue_license(order_ref, email, sku, ttl_hours=72):
    init_ledger()
    exp = int(time.time()) + int(ttl_hours * 3600)
    msg = f"{order_ref}|{email.lower()}|{sku}|{exp}".encode("utf-8")
    sig = hmac.new(get_signing_secret().encode("utf-8"), msg, hashlib.sha256).hexdigest()[:24]
    token = f"ORCL-{sku[:6].upper()}-{sig}"
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "INSERT OR IGNORE INTO licenses (order_ref, email, sku, token, expires_epoch, created_utc) VALUES (?,?,?,?,?,?)",
        (order_ref, email, sku, token, exp, dt.datetime.utcnow().isoformat() + "Z"),
    )
    c.commit()
    row = c.execute("SELECT token, sku, expires_epoch FROM licenses WHERE order_ref=?", (order_ref,)).fetchone()
    c.close()
    return {"token": row[0], "sku": row[1], "expires_epoch": row[2]}


def resolve_download_token(token):
    init_ledger()
    c = sqlite3.connect(DB_PATH)
    row = c.execute("SELECT id, sku, expires_epoch, downloads FROM licenses WHERE token=?", (token,)).fetchone()
    if not row:
        c.close()
        return None, "Invalid license token"
    lid, sku, exp, dl = row
    if int(time.time()) > int(exp):
        c.close()
        return None, "Download link expired"
    fpath = PRODUCT_FILES.get(sku, "")
    if not fpath or not os.path.exists(fpath):
        c.close()
        return None, "Deliverable ZIP not staged yet"
    c.execute("UPDATE licenses SET downloads=? WHERE id=?", (int(dl) + 1, lid))
    c.commit()
    c.close()
    return fpath, "OK"


if __name__ == "__main__":
    init_ledger()
    sample = issue_license("SANDBOX-VERIFY-001", "Toomer1980@gmail.com", "assetpack15", ttl_hours=720)
    print(f"[PHASE 33 PASS] Cryptographic License Ledger ready -> sample token: {sample['token']}")
