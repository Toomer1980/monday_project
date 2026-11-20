import datetime as dt
import os
import smtplib
import sqlite3
import sys
import time
from email.message import EmailMessage


def load_env(pdir):
    out = {}
    ep = os.path.join(pdir, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8"):
            t = ln.strip()
            if t and not t.startswith("#") and "=" in t:
                k, v = t.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def main():
    pdir = sys.argv[1]
    limit = int(sys.argv[2])
    spacing_sec = int(sys.argv[3])
    send_live = (sys.argv[4].upper() == "LIVE")

    db_path = os.path.join(pdir, "data", "pronode_crm.db")
    if not os.path.exists(db_path):
        print("[INFO] pronode_crm.db not found. Add leads first via .\\build_pronode_leads.ps1 -InteractiveAdd -ImportToCrm")
        return

    env = load_env(pdir)
    g_user = env.get("GMAIL_USER", "Toomer1980@gmail.com")
    g_pass = (env.get("GMAIL_APP_PASSWORD", "") or "").replace(" ", "")
    pub_url = env.get("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, company, contact, email, stage, notes FROM prospects "
        "WHERE lower(stage) IN ('lead', 'new') ORDER BY id ASC LIMIT ?",
        (limit,),
    ).fetchall()

    print(f"=== PRO_NODE ($49,999) WEEKLY OUTREACH SPRINT ({'LIVE SMTP' if send_live else 'DRY-RUN PREVIEW'}) ===")
    print(f"Queued Leads: {len(rows)} (Cap: {limit} | Spacing: {spacing_sec}s)")
    if not rows:
        print("[INFO] 0 uncontacted Lead rows in pronode_crm.db. Run .\\build_pronode_leads.ps1 to import your 20 weekly prospects.")
        conn.close()
        return

    if send_live and (not g_pass or "PASTE_16_CHAR" in g_pass):
        print("[ERROR] GMAIL_APP_PASSWORD is missing in .env. Run .\\setup_gmail_smtp.ps1 first.")
        conn.close()
        sys.exit(2)

    today = dt.date.today()
    followup_date = (today + dt.timedelta(days=3)).isoformat()
    sent_count = 0
    report_lines = [f"# Oracle Systems LLC - Pro_Node Outreach Sprint ({today.isoformat()})", f"- Mode: {'LIVE' if send_live else 'DRY-RUN'} | Candidates: {len(rows)}", ""]

    server = None
    if send_live:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        server.starttls()
        server.login(g_user, g_pass)

    try:
        for idx, r in enumerate(rows, 1):
            first = (r["contact"] or "Team").split()[0]
            subj = f"Dedicated Sovereign AI Node for {r['company']} (3-Min Live Sandbox)"
            body = (
                f"Hi {first},\n\n"
                f"We built Oracle Systems Pro_Node so teams like {r['company']} can run autonomous 4D media pipelines, "
                f"CRM automation, and local AI inference on dedicated turnkey infrastructure with zero per-seat SaaS lock-in.\n\n"
                f"- Turnkey Deployment: $49,999 ($24,999.50 Milestone 1 ACH deposit, Stripe-verified)\n"
                f"- Live Storefront & Architecture Preview: {pub_url}/store\n\n"
                f"Would you be open to a 3-minute live sandbox walkthrough this week?\n\n"
                f"Best regards,\nThomas Toomer\nOracle Systems LLC\n"
            )
            if send_live:
                msg = EmailMessage()
                msg["From"] = g_user
                msg["To"] = r["email"]
                msg["Subject"] = subj
                msg.set_content(body)
                server.send_message(msg)
                now_z = dt.datetime.utcnow().isoformat() + "Z"
                new_notes = ((r["notes"] or "") + f" | Sprint emailed {today.isoformat()}").strip(" |")
                cur.execute(
                    "UPDATE prospects SET stage='Contacted', next_followup=?, notes=?, updated_utc=? WHERE id=?",
                    (followup_date, new_notes, now_z, r["id"]),
                )
                conn.commit()
                sent_count += 1
                print(f"  [SENT {idx}/{len(rows)}] #{r['id']} {r['company']} <{r['email']}> -> Follow-up set: {followup_date}")
                report_lines.append(f"- [SENT] #{r['id']} {r['company']} ({r['email']}) -> Follow-up {followup_date}")
                if idx < len(rows) and spacing_sec > 0:
                    time.sleep(spacing_sec)
            else:
                print(f"  [PREVIEW {idx}/{len(rows)}] #{r['id']} {r['company']} <{r['email']}> | Subject: {subj}")
                report_lines.append(f"- [PREVIEW] #{r['id']} {r['company']} ({r['email']}) | {subj}")
    finally:
        if server:
            server.quit()
        conn.close()

    rep_p = os.path.join(pdir, "reports", "ProNode_Sprint_Report.md")
    open(rep_p, "w", encoding="utf-8", newline="").write("\n".join(report_lines) + "\n")
    print(f"[DONE] Sent: {sent_count}/{len(rows)} | Report saved: {rep_p}")


if __name__ == "__main__":
    main()