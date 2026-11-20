import datetime as dt
import json
import os
import re
import sqlite3
import sys

PRONODE_M1_CENTS = 2499950
PRONODE_FULL_CENTS = 4999900


def ensure_crm(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS prospects ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "company TEXT NOT NULL, "
        "contact TEXT, "
        "email TEXT NOT NULL, "
        "stage TEXT NOT NULL DEFAULT 'Lead', "
        "deal_value_usd REAL NOT NULL DEFAULT 49999.00, "
        "ach_net_usd REAL NOT NULL DEFAULT 49789.00, "
        "next_followup TEXT, "
        "last_invoice_id TEXT, "
        "notes TEXT, "
        "created_utc TEXT, "
        "updated_utc TEXT)"
    )
    conn.commit()


def unlock_tier3_configs(project_dir, invoice_id, amount_usd, email):
    toml_path = os.path.join(project_dir, "config", "sovereign_block10.toml")
    ini_path = os.path.join(project_dir, "config", "sovereign_treasury.ini")
    flag_path = os.path.join(project_dir, "logs", "tier3_ha_unlocked.json")

    if os.path.exists(toml_path):
        with open(toml_path, "r", encoding="utf-8") as f:
            raw = f.read()
        raw = re.sub(r'(?m)^active_tier\s*=\s*"[^"]*"', 'active_tier = "TIER_3_ENTERPRISE_HA_UNLOCKED"', raw)
        with open(toml_path, "w", encoding="utf-8", newline="") as f:
            f.write(raw)

    if os.path.exists(ini_path):
        with open(ini_path, "r", encoding="utf-8") as f:
            raw = f.read()
        raw = re.sub(r'(?m)^current_tier\s*=\s*.*$', 'current_tier = TIER_3_ENTERPRISE_HA_UNLOCKED', raw)
        with open(ini_path, "w", encoding="utf-8", newline="") as f:
            f.write(raw)

    flag_data = {
        "unlocked_utc": dt.datetime.utcnow().isoformat() + "Z",
        "trigger_invoice_id": invoice_id,
        "amount_paid_usd": round(amount_usd, 2),
        "client_email": email,
        "cloud_tier": "TIER_3_ENTERPRISE_HA_UNLOCKED",
    }
    with open(flag_path, "w", encoding="utf-8") as f:
        json.dump(flag_data, f, indent=2)
    return flag_path


def main():
    if len(sys.argv) < 4:
        print("[ERROR] Usage: stripe_crm_reconciler.py <project_dir> <invoices_json> <mode>")
        sys.exit(1)

    project_dir = sys.argv[1]
    inv_json_path = sys.argv[2]
    mode = sys.argv[3].upper()
    db_path = os.path.join(project_dir, "data", "pronode_crm.db")

    if not os.path.exists(inv_json_path):
        print(f"[INFO] No paid invoices JSON found at {inv_json_path}")
        return

    with open(inv_json_path, "r", encoding="utf-8") as f:
        invoices = json.load(f)
    if isinstance(invoices, dict):
        invoices = invoices.get("data", [])

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ensure_crm(conn)
    cur = conn.cursor()

    now_utc = dt.datetime.utcnow().isoformat() + "Z"
    updated = 0
    inserted = 0
    tier3_trigger = None

    for inv in invoices:
        if (inv.get("status") or "").lower() != "paid":
            continue
        inv_id = inv.get("id") or ""
        amt_cents = int(inv.get("amount_paid") or inv.get("total") or 0)
        amt_usd = amt_cents / 100.0
        email = (inv.get("customer_email") or "").strip().lower()
        name = (inv.get("customer_name") or "Enterprise Client").strip()
        meta = inv.get("metadata") or {}
        sku = (meta.get("sku") or "").lower()
        milestone = (meta.get("milestone") or "").upper()

        is_pronode = (sku == "pro_node") or (amt_cents >= PRONODE_M1_CENTS)
        if not is_pronode:
            continue

        if amt_cents >= PRONODE_FULL_CENTS or milestone in ("M2", "FULL"):
            target_stage = "ClosedWon"
        else:
            target_stage = "InvoicedM1"

        row = cur.execute("SELECT * FROM prospects WHERE last_invoice_id = ?", (inv_id,)).fetchone()
        if not row and email:
            row = cur.execute("SELECT * FROM prospects WHERE lower(email) = ?", (email,)).fetchone()

        if mode == "LIVE":
            if row:
                note_add = f" | PAID {inv_id} (${amt_usd:,.2f}) on {now_utc[:10]}"
                new_notes = (row["notes"] or "")
                if inv_id not in new_notes:
                    new_notes = (new_notes + note_add).strip(" |")
                cur.execute(
                    "UPDATE prospects SET stage=?, last_invoice_id=?, notes=?, updated_utc=? WHERE id=?",
                    (target_stage, inv_id, new_notes, now_utc, row["id"]),
                )
                updated += 1
                print(f"[RECONCILED] CRM #{row['id']} ({row['company']}) -> {target_stage} | Paid ${amt_usd:,.2f} ({inv_id})")
            else:
                cur.execute(
                    "INSERT INTO prospects (company, contact, email, stage, deal_value_usd, ach_net_usd, next_followup, last_invoice_id, notes, created_utc, updated_utc) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, name, email or "unknown@client.com", target_stage, max(49999.0, amt_usd), 49789.0, dt.date.today().isoformat(), inv_id, f"Auto-imported from paid Stripe invoice {inv_id}", now_utc, now_utc),
                )
                inserted += 1
                print(f"[AUTO-ADDED] New CRM #{cur.lastrowid} ({name}) -> {target_stage} | Paid ${amt_usd:,.2f} ({inv_id})")

            if amt_cents >= PRONODE_M1_CENTS:
                tier3_trigger = (inv_id, amt_usd, email)
        else:
            print(f"[TEST MODE MATCH] Paid sandbox invoice {inv_id} (${amt_usd:,.2f}, {email}) -> would set {target_stage} (live CRM/Tier 3 untouched)")

    conn.commit()
    conn.close()

    if tier3_trigger and mode == "LIVE":
        flag_path = unlock_tier3_configs(project_dir, *tier3_trigger)
        print(f"[TIER 3 HA UNLOCKED] Funded Pro_Node deposit (${tier3_trigger[1]:,.2f}) verified -> configs updated & flag written to {flag_path}")
    else:
        print(f"[SUMMARY] Mode: {mode} | Paid Pro_Node Reconciled: {updated} updated, {inserted} added | Tier 3 HA Gate: LOCKED")


if __name__ == "__main__":
    main()