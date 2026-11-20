import base64
import datetime as dt
import json
import os
import re
import sqlite3
import sys


def safe_slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", (text or "prospect")).strip("_")[:40]


def build_email(row, domain, sender_name, sender_email):
    company = row["company"]
    contact = (row["contact"] or "Team").strip()
    first_name = contact.split()[0] if contact else "there"
    stage = row["stage"]
    notes = (row["notes"] or "").strip()
    note_line = f"\nRe: {notes}\n" if notes else "\n"

    if stage in ("Lead", "Contacted"):
        subject = f"{company} x Oracle Systems LLC - Dedicated Autonomous Media & Fulfillment Node"
        body = (
            f"Hi {first_name},\n\n"
            f"I am reaching out because Oracle Systems LLC deploys dedicated, single-tenant autonomous compute, "
            f"52-week media pipelines, and instant digital fulfillment stacks (Pro_Node) for operators scaling high-margin digital offers.\n"
            f"{note_line}"
            f"What is included in a turnkey Pro_Node deployment ($49,999 one-time):\n"
            f"  1. Isolated High-Availability Cloud Cluster (dual dedicated nodes, load balancer, HA PostgreSQL, CDN - 12 months hosted).\n"
            f"  2. Full SovereignCore automation suite: storefront, customer fulfillment portal, UTM click attribution, and weekly treasury audits.\n"
            f"  3. Two live architecture onboarding sessions + 12 months priority engineering support.\n\n"
            f"I can walk you through a live 3-minute sandbox demo showing automated checkout-to-fulfillment in real time.\n"
            f"Do you have 10 minutes this week?\n\n"
            f"Best regards,\n{sender_name}\nPrincipal, Oracle Systems LLC\n{sender_email} | https://{domain}\n"
        )
    elif stage == "DemoBooked":
        subject = f"Confirming our 3-Minute Pro_Node Live Sandbox Demo - {company}"
        body = (
            f"Hi {first_name},\n\n"
            f"Looking forward to walking {company} through the live Pro_Node sandbox.\n"
            f"{note_line}"
            f"In 3 minutes we will cover:\n"
            f"  - Live storefront-to-Stripe checkout & automated ZIP/MP4 fulfillment portal.\n"
            f"  - Dedicated Tier 3 High-Availability cloud architecture & security isolation.\n"
            f"  - 50/50 Milestone deployment timeline ($24,999.50 kickoff / $24,999.50 handoff via ACH or Wire).\n\n"
            f"Reply if you want any specific workflow tested during the call.\n\n"
            f"Best regards,\n{sender_name}\nOracle Systems LLC\n{sender_email}\n"
        )
    else:
        subject = f"Pro_Node Proposal & Milestone 1 ACH Kickoff - {company}"
        body = (
            f"Hi {first_name},\n\n"
            f"Following up on the Pro_Node Enterprise Deployment proposal for {company} ($49,999 total, including 12 months dedicated HA infrastructure).\n"
            f"{note_line}"
            f"To lock in your provisioning slot:\n"
            f"  - Milestone 1 (50% Kickoff Deposit): $24,999.50 USD via Stripe ACH Direct Debit or Wire (zero card surcharges).\n"
            f"  - Milestone 2 (50% Production Handoff): $24,999.50 USD upon acceptance.\n\n"
            f"Reply 'Approved' and I will issue your Net-7 Stripe ACH Invoice and SOW today so we can spin up {company}'s dedicated HA cluster immediately.\n\n"
            f"Best regards,\n{sender_name}\nPrincipal, Oracle Systems LLC\n{sender_email} | https://{domain}\n"
        )
    return subject, body


def write_demo_checklist(out_dir, domain):
    checklist = (
        "========================================================================\n"
        "ORACLE SYSTEMS LLC - PRO_NODE ($49,999) 3-MINUTE LIVE SANDBOX DEMO SCRIPT\n"
        "========================================================================\n\n"
        "[PRE-CALL 60-SECOND CHECK]\n"
        "  [ ] Run .\\optimize_ram_and_boot.ps1 -TrimNow (keep RAM < 75%)\n"
        "  [ ] Run .\\test_stripe_webhook.ps1 (verify /store, /portal, /dashboard HTTP 200)\n"
        "  [ ] Open 3 clean tabs: /dashboard, /store, and /portal (Receipt 2352-8553)\n\n"
        "[MINUTE 1: EXECUTIVE MATRIX & LIVE TELEMETRY (0:00 - 1:00)]\n"
        "  - Show /dashboard: real-time worker swarm heartbeats, live Stripe mode, SKU telemetry.\n"
        "  - Highlight Block 10 automated weekly treasury reconciliation + tax reserve + cloud margin guard.\n\n"
        "[MINUTE 2: ZERO-TOUCH CHECKOUT TO INSTANT FULFILLMENT (1:00 - 2:00)]\n"
        "  - Show /store and /go/<tier> UTM attribution tracking (proving ROI per traffic campaign).\n"
        "  - Open /portal with Receipt 2352-8553: demonstrate instant license key + .ZIP + 17.5 MB .MP4 delivery.\n"
        "  - Mention 52-week autonomous content vault (52 Full Videos + 52 Shorts ready for scheduled distribution).\n\n"
        "[MINUTE 3: ENTERPRISE ISOLATION & 50/50 ACH CLOSE (2:00 - 3:00)]\n"
        "  - Walk through Tier 3 Dedicated HA Cluster (dual dedicated nodes, load balancer, HA Postgres, custom SSL).\n"
        "  - Present 50/50 Milestone terms: $24,999.50 kickoff + $24,999.50 handoff via Stripe ACH Direct Debit.\n"
        "  - Close: 'Once you confirm the billing email, I trigger your Net-7 Stripe ACH invoice right from our CLI.'\n"
        f"  - Command to send immediately on approval:\n"
        f"      .\\pronode_crm.ps1 -Action Invoice -Id <PROSPECT_ID> -Milestone M1 -InvoiceMode LIVE -SendInvoice\n"
        f"  - Production Domain Target: https://{domain}\n"
    )
    path = os.path.join(out_dir, "ProNode_3Min_Demo_Checklist.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(checklist)
    return path


def main():
    db_path = sys.argv[1]
    out_dir = sys.argv[2]
    cfg = json.loads(base64.b64decode(sys.argv[3]).decode("utf-8"))

    os.makedirs(out_dir, exist_ok=True)
    checklist_path = write_demo_checklist(out_dir, cfg.get("domain", "oraclesystemsllc.com"))
    print(f"[PASS] Generated 3-minute demo checklist -> {checklist_path}")

    if not os.path.exists(db_path):
        print("[INFO] CRM database not initialized yet. Run .\\pronode_crm.ps1 -Action Init first.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    today_str = dt.date.today().isoformat()

    if cfg.get("all_active"):
        rows = cur.execute(
            "SELECT * FROM prospects WHERE stage NOT IN ('ClosedWon','Lost') ORDER BY next_followup ASC"
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM prospects WHERE stage NOT IN ('ClosedWon','Lost') AND next_followup <= ? ORDER BY next_followup ASC",
            (today_str,),
        ).fetchall()
    conn.close()

    if not rows:
        print(f"[INFO] 0 prospects due on or before {today_str}. Use -AllActive to draft for all active prospects, or add prospects via pronode_crm.ps1.")
        return

    ymd = dt.date.today().strftime("%Y%m%d")
    generated = 0
    for r in rows:
        subj, body = build_email(r, cfg.get("domain", "oraclesystemsllc.com"), cfg.get("sender_name", "Thomas Toomer"), cfg.get("sender_email", "Toomer1980@gmail.com"))
        fname = f"{ymd}_ID{r['id']}_{safe_slug(r['company'])}_{r['stage']}.txt"
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w", encoding="utf-8", newline="") as f:
            f.write(f"TO: {r['email']}\nSUBJECT: {subj}\nSTAGE: {r['stage']} | FOLLOW-UP: {r['next_followup']}\n")
            f.write("-" * 72 + "\n\n" + body)
        print(f"[DRAFTED] #{r['id']} {r['company']} ({r['stage']}) -> {fname}")
        generated += 1

    print(f"[COMPLETE] Generated {generated} personalized outreach email(s) in {out_dir}")


if __name__ == "__main__":
    main()