import datetime as dt
import os
import sqlite3
import sys
import time


def main():
    pdir = sys.argv[1]
    send_live = (len(sys.argv) > 2 and sys.argv[2].upper() == "LIVE")
    spacing = int(sys.argv[3]) if len(sys.argv) > 3 else 35

    sys.path.insert(0, os.path.join(pdir, "Modules"))
    from google_mail_engine import send_oracle_email, load_env

    db_path = os.path.join(pdir, "data", "pronode_crm.db")
    if not os.path.exists(db_path):
        print("[INFO] pronode_crm.db not found.")
        return

    today = dt.date.today()
    today_iso = today.isoformat()
    next_touch = (today + dt.timedelta(days=4)).isoformat()
    pub_url = load_env(pdir).get("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, company, contact, email, stage, next_followup, notes FROM prospects "
        "WHERE lower(stage) IN ('contacted', 'demobooked', 'proposalsent') "
        "AND next_followup IS NOT NULL AND next_followup <= ? ORDER BY next_followup ASC LIMIT 25",
        (today_iso,),
    ).fetchall()

    print(f"=== PRO_NODE 3-DAY FOLLOW-UP AUTOMATION ({'LIVE' if send_live else 'DRY-RUN'}) ===")
    print(f"Due Today ({today_iso}): {len(rows)} prospect(s)")
    if not rows:
        conn.close()
        return

    sent = 0
    for idx, r in enumerate(rows, 1):
        first = (r["contact"] or "Team").split()[0]
        subj = f"Quick follow-up: 3-Min Live Sandbox for {r['company']}"
        body = (
            f"Hi {first},\n\n"
            f"Floating this back to the top of your inbox in case it got buried. Happy to run a live 3-minute screen-share "
            f"of Oracle Systems Pro_Node showing autonomous 4D media rendering, local AI inference, and Stripe ACH milestone billing.\n\n"
            f"Live Preview: {pub_url}/store\n\n"
            f"Would Tuesday or Thursday work for a 3-minute walkthrough?\n\n"
            f"Best,\nThomas Toomer\nOracle Systems LLC\n"
        )
        if send_live:
            via = send_oracle_email(pdir, r["email"], subj, body)
            now_z = dt.datetime.utcnow().isoformat() + "Z"
            n_notes = ((r["notes"] or "") + f" | 3-day follow-up sent {today_iso}").strip(" |")
            cur.execute(
                "UPDATE prospects SET next_followup=?, notes=?, updated_utc=? WHERE id=?",
                (next_touch, n_notes, now_z, r["id"]),
            )
            conn.commit()
            sent += 1
            print(f"  [FOLLOW-UP SENT {idx}/{len(rows)}] #{r['id']} {r['company']} <{r['email']}> via {via} -> Next: {next_touch}")
            if idx < len(rows) and spacing > 0:
                time.sleep(spacing)
        else:
            print(f"  [DUE PREVIEW {idx}/{len(rows)}] #{r['id']} {r['company']} <{r['email']}> (Due: {r['next_followup']})")

    conn.close()
    print(f"[DONE] Follow-ups sent: {sent}/{len(rows)}")


if __name__ == "__main__":
    main()