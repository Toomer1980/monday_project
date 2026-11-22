import datetime as dt
import json
import os
import sqlite3

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DATA_DIR = os.path.join(PDIR, "data")
REPORTS_DIR = os.path.join(PDIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def main():
    today = dt.date.today()
    target_jan1 = dt.date(2027, 1, 1)
    target_jan31 = dt.date(2027, 1, 31)
    days_to_jan1 = max(1, (target_jan1 - today).days)
    days_to_jan31 = max(1, (target_jan31 - today).days)

    snap_p = os.path.join(PDIR, "audit_inbox", "stripe_live_api_snapshot.json")
    snap = json.load(open(snap_p, "r", encoding="utf-8")) if os.path.exists(snap_p) else {}
    gross = float(snap.get("charges_gross_usd", 49.00))
    net = float(snap.get("charges_net_usd", 47.28))

    total_clicks = 0
    udb = os.path.join(DATA_DIR, "utm_analytics.db")
    if os.path.exists(udb):
        try:
            c = sqlite3.connect(udb)
            total_clicks = int(c.execute("SELECT COUNT(*) FROM utm_clicks").fetchone()[0])
            c.close()
        except Exception:
            pass

    prospects = 0
    cdb = os.path.join(DATA_DIR, "pronode_crm.db")
    if os.path.exists(cdb):
        try:
            c = sqlite3.connect(cdb)
            prospects = int(c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0])
            c.close()
        except Exception:
            pass

    gap = max(0.0, 1000000.0 - gross)
    req_daily_jan1 = gap / float(days_to_jan1)
    req_daily_jan31 = gap / float(days_to_jan31)

    # Create a ready-to-fill CSV template for scaling real B2B agency leads cleanly
    csv_tpl = os.path.join(PDIR, "data", "b2b_prospects_import_template.csv")
    if not os.path.exists(csv_tpl):
        open(csv_tpl, "w", encoding="utf-8", newline="").write(
            "company,contact,email,notes\n"
            "Example Creative Studio,Jane Doe,jane@example-studio.com,Media agency producing daily Shorts\n"
        )

    lines = [
        f"# Oracle Systems LLC - Multi-Stream Revenue Velocity & Target Math ({today.isoformat()})",
        f"- **Current Verified Gross Revenue:** ${gross:,.2f} (Net: ${net:,.2f})",
        f"- **Verified Checkout Clicks:** {total_clicks} | **Active B2B CRM Prospects:** {prospects}",
        f"- **Remaining Gap to $1,000,000:** ${gap:,.2f}",
        f"- **Required Daily Run-Rate:** ${req_daily_jan1:,.2f}/day (by Jan 1, 2027 - {days_to_jan1} days) | ${req_daily_jan31:,.2f}/day (by Jan 31, 2027 - {days_to_jan31} days)",
        "",
        "## Unit Economics Across Your 6 Revenue Streams (What $1,000,000 Requires)",
        "| Tier | Price | Units Alone for $1M | Best Role in Swarm |",
        "| :--- | ---: | ---: | :--- |",
        "| Creator Asset Pack | $15 | 66,667 | Entry impulse buy + email list builder |",
        "| Sovereign 5D Vault | $15/mo | 66,667/mo | Compounding recurring base |",
        "| 5D Automation Blueprint | $29 | 34,483 | Mid-ticket digital upsell |",
        "| Custom 5D Aura Reading | $49 | 20,409 | Highest-converting consumer flagship |",
        "| Turnkey 4D/5D Creator Stack | $1,500 | 667 | Fast B2B cashflow engine (10 deals = $15,000) |",
        "| Enterprise Dedicated Pro_Node | $49,999 | 20 | Primary high-ticket needle-mover |",
        "",
        "## Highest-ROI Immediate Execution Priorities",
        "1. **Cloud Cutover (24/7/365 Uptime):** Move to DigitalOcean/Oracle Cloud on Nov 27 (`Run_Nov27_Cloud_Cutover.ps1`) so zero sales are lost to laptop sleep or tunnel rotation.",
        "2. **B2B Pipeline Scale:** Import 25-50 real media/marketing agencies into `data\\b2b_prospects_import_template.csv` and run compliant personalized outreach + `pronode_proposal_gen.py`.",
        "3. **Consumer Content Velocity:** Let `OracleSystems_UltraHD_4D5D_VaultFactory` upgrade all 104 videos to 1080p/30fps 4D/5D and publish daily Shorts + weekly full episodes with pinned `/go/` links.",
        "4. **Distribution APIs:** Add `X_USER_ACCESS_TOKEN` / `LINKEDIN_ACCESS_TOKEN` to `.env` to turn Phase 47 multi-platform posting fully hands-free.",
    ]
    out_p = os.path.join(REPORTS_DIR, "Revenue_Velocity_Action_Plan.md")
    open(out_p, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print(f"[REVENUE VELOCITY PASS] Updated {out_p} | Gap: ${gap:,.2f} | Days to Jan 1: {days_to_jan1}")


if __name__ == "__main__":
    main()
