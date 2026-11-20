import base64
import csv
import datetime as dt
import json
import os
import sqlite3
import sys


def main():
    if len(sys.argv) < 4:
        print("[ERROR] Usage: pronode_crm_engine.py <db_path> <action> <b64_json>")
        sys.exit(1)

    db_path = sys.argv[1]
    action = sys.argv[2]
    payload = json.loads(base64.b64decode(sys.argv[3]).decode("utf-8"))

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
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

    now_utc = dt.datetime.utcnow().isoformat() + "Z"
    today_str = dt.date.today().isoformat()

    stage_weights = {
        "Lead": 0.05,
        "Contacted": 0.10,
        "DemoBooked": 0.25,
        "ProposalSent": 0.50,
        "InvoicedM1": 0.80,
        "ClosedWon": 1.00,
        "Lost": 0.00,
    }

    if action == "Init":
        print(f"[PASS] Pro_Node B2B CRM ready at {db_path}")

    elif action == "Add":
        if not payload.get("company") or not payload.get("email"):
            print("[ERROR] -Company and -Email are required for -Action Add")
            sys.exit(1)
        cur.execute(
            "INSERT INTO prospects (company, contact, email, stage, next_followup, notes, created_utc, updated_utc) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                payload["company"],
                payload.get("contact", ""),
                payload["email"],
                payload.get("stage", "Lead"),
                payload.get("next_followup", today_str),
                payload.get("notes", ""),
                now_utc,
                now_utc,
            ),
        )
        conn.commit()
        print(
            f"[ADDED] Prospect #{cur.lastrowid}: {payload['company']} <{payload['email']}> "
            f"| Stage: {payload.get('stage', 'Lead')} | Follow-Up: {payload.get('next_followup', today_str)}"
        )

    elif action == "Update":
        pid = int(payload.get("id", 0))
        if pid <= 0:
            print("[ERROR] Specify -Id <number> for -Action Update")
            sys.exit(1)
        cur.execute(
            "UPDATE prospects SET stage=?, next_followup=?, notes=COALESCE(NULLIF(?, ''), notes), updated_utc=? WHERE id=?",
            (payload["stage"], payload["next_followup"], payload.get("notes", ""), now_utc, pid),
        )
        conn.commit()
        print(f"[UPDATED] Prospect #{pid} -> Stage: {payload['stage']} | Next Follow-Up: {payload['next_followup']}")

    elif action in ("List", "Due"):
        if action == "Due":
            rows = cur.execute(
                "SELECT * FROM prospects WHERE stage NOT IN ('ClosedWon','Lost') AND next_followup <= ? ORDER BY next_followup ASC",
                (today_str,),
            ).fetchall()
            print(f"=== PRO_NODE FOLLOW-UPS DUE ON OR BEFORE {today_str} ({len(rows)}) ===")
        else:
            rows = cur.execute("SELECT * FROM prospects ORDER BY id DESC").fetchall()
            print(f"=== ALL PRO_NODE B2B PROSPECTS ({len(rows)}) ===")
        if not rows:
            print("(No prospects matched yet. Add one with: .\\pronode_crm.ps1 -Action Add -Company 'Acme' -Contact 'Jane' -Email 'jane@acme.com')")
        else:
            print(f"{'ID':<4} {'Company':<22} {'Email':<26} {'Stage':<13} {'FollowUp':<11} {'InvoiceID'}")
            print("-" * 92)
            for r in rows:
                print(
                    f"{r['id']:<4} {r['company'][:21]:<22} {r['email'][:25]:<26} "
                    f"{r['stage']:<13} {(r['next_followup'] or ''):<11} {r['last_invoice_id'] or '-'}"
                )

    elif action == "Summary":
        rows = cur.execute("SELECT * FROM prospects").fetchall()
        active = [r for r in rows if r["stage"] not in ("ClosedWon", "Lost")]
        won = [r for r in rows if r["stage"] == "ClosedWon"]
        due = [r for r in active if (r["next_followup"] or "9999-12-31") <= today_str]
        open_gross = sum(r["deal_value_usd"] for r in active)
        open_ach_net = sum(r["ach_net_usd"] for r in active)
        weighted_ach = sum(r["ach_net_usd"] * stage_weights.get(r["stage"], 0.0) for r in active)
        won_ach = sum(r["ach_net_usd"] for r in won)
        print("=== PRO_NODE ($49,999) B2B OUTREACH & PIPELINE SUMMARY ===")
        print("Weekly Outreach Target : 20 qualified prospects/week (80/month)")
        print(f"Total Prospects Logged : {len(rows)} | Active Pipeline: {len(active)} | Follow-Ups Due Today: {len(due)} | Closed Won: {len(won)}")
        print(f"Active Gross Pipeline  : ${open_gross:,.2f} (Est. 50/50 ACH Net: ${open_ach_net:,.2f})")
        print(f"Stage-Weighted ACH Net : ${weighted_ach:,.2f}")
        print(f"Closed-Won ACH Net     : ${won_ach:,.2f} (saves $2,990/deal vs Card Payment Link)")

    elif action == "GetForInvoice":
        row = cur.execute("SELECT * FROM prospects WHERE id=?", (int(payload["id"]),)).fetchone()
        if not row:
            print("NOT_FOUND")
            sys.exit(2)
        print(json.dumps(dict(row)))

    elif action == "MarkInvoiced":
        new_stage = "InvoicedM1" if payload.get("milestone") == "M1" else "ClosedWon"
        cur.execute(
            "UPDATE prospects SET stage=?, last_invoice_id=?, updated_utc=? WHERE id=?",
            (new_stage, payload["invoice_id"], now_utc, int(payload["id"])),
        )
        conn.commit()
        print(f"[CRM UPDATED] Prospect #{payload['id']} -> Stage: {new_stage} | Stripe Invoice: {payload['invoice_id']}")

    elif action == "ExportCsv":
        out_csv = payload["export_csv"]
        rows = cur.execute("SELECT * FROM prospects ORDER BY id ASC").fetchall()
        with open(out_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "company", "contact", "email", "stage", "deal_value_usd", "ach_net_usd", "next_followup", "last_invoice_id", "notes", "created_utc", "updated_utc"])
            for r in rows:
                w.writerow([r[k] for k in r.keys()])
        print(f"[EXPORTED] Saved {len(rows)} prospects to {out_csv}")

    conn.close()


if __name__ == "__main__":
    main()