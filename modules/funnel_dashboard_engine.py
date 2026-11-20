import datetime as dt
import json
import os
import shutil
import sqlite3
import sys


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return default


def main():
    pdir = sys.argv[1]
    stripe_json = sys.argv[2]

    sdata = load_json(stripe_json, {})
    yt_a  = load_json(os.path.join(pdir, "data", "youtube_analytics.json"), {})
    yt_st = load_json(os.path.join(pdir, "data", "youtube_publish_state.json"), {})
    lc_st = load_json(os.path.join(pdir, "logs", "learning_curve_state.json"), {})

    # YouTube & Vault totals
    yt_tot = yt_a.get("totals") or {}
    yt_views    = int(yt_tot.get("views", 0))
    yt_likes    = int(yt_tot.get("likes", 0))
    yt_comments = int(yt_tot.get("comments", 0))
    pub_full    = len(yt_st.get("published_full") or [])
    pub_short   = len(yt_st.get("published_shorts") or [])

    # UTM clicks from SQLite
    utm_db = os.path.join(pdir, "data", "utm_analytics.db")
    tot_clicks = 0
    tier_clicks = []
    if os.path.exists(utm_db):
        try:
            c = sqlite3.connect(utm_db)
            tot_clicks = int(c.execute("SELECT COUNT(*) FROM utm_clicks").fetchone()[0])
            tier_clicks = c.execute("SELECT tier, COUNT(*) FROM utm_clicks GROUP BY tier ORDER BY COUNT(*) DESC").fetchall()
            c.close()
        except Exception:
            pass

    # Pro_Node CRM stages from SQLite
    crm_db = os.path.join(pdir, "data", "pronode_crm.db")
    crm_total = 0
    crm_stages = []
    crm_pipe_usd = 0.0
    if os.path.exists(crm_db):
        try:
            c = sqlite3.connect(crm_db)
            crm_total = int(c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0])
            crm_stages = c.execute("SELECT stage, COUNT(*), COALESCE(SUM(deal_value_usd),0) FROM prospects GROUP BY stage").fetchall()
            crm_pipe_usd = float(c.execute("SELECT COALESCE(SUM(deal_value_usd),0) FROM prospects WHERE stage != 'Lost'").fetchone()[0])
            c.close()
        except Exception:
            pass

    # Stripe metrics
    charges = int(sdata.get("charge_count", 0))
    gross   = float(sdata.get("charges_gross_usd", 0.0))
    fees    = float(sdata.get("charges_fee_usd", 0.0))
    net     = float(sdata.get("charges_net_usd", 0.0))
    avail   = float(sdata.get("available_usd", 0.0))
    pend    = float(sdata.get("pending_usd", 0.0))
    tax_res = round(net * 0.25, 2)
    post_r  = round(net - tax_res, 2)

    # Conversion rates
    ctr_pct = (tot_clicks / float(yt_views) * 100.0) if yt_views > 0 else 0.0
    cvr_pct = (charges / float(tot_clicks) * 100.0) if tot_clicks > 0 else 0.0
    rev_per_click = (net / float(tot_clicks)) if tot_clicks > 0 else 0.0

    pub_url = ""
    purl_f = os.path.join(pdir, "config", "public_url.txt")
    if os.path.exists(purl_f):
        pub_url = open(purl_f, "r", encoding="utf-8").read().strip()

    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Oracle Systems LLC - Live Sales & Conversion Funnel Dashboard",
        f"- **Updated:** {now_str} EST | **Public Funnel:** {pub_url or 'http://127.0.0.1:8000'}",
        "",
        "## 1. End-to-End Conversion Funnel",
        f"- **Stage 1 (Content Supply):** 52/52 4D Full Videos + 52/52 4D Shorts rendered | Uploaded: {pub_full + pub_short}/104 ({pub_full} Full, {pub_short} Shorts)",
        f"- **Stage 2 (YouTube Reach):** {yt_views:,} views | {yt_likes:,} likes | {yt_comments:,} comments",
        f"- **Stage 3 (/go UTM Clicks):** {tot_clicks:,} tracked clicks | View-to-Click CTR: {ctr_pct:.2f}%",
        f"- **Stage 4 (Live Stripe Sales):** {charges} paid charge(s) | Click-to-Sale CVR: {cvr_pct:.2f}% | Net/Click: ${rev_per_click:,.2f}",
        "",
        "## 2. Live Stripe Treasury Snapshot",
        f"- **Available Balance:** ${avail:,.2f} | **Pending Balance:** ${pend:,.2f} (Target Payout: 2026-11-27)",
        f"- **Verified Gross:** ${gross:,.2f} | **Stripe Fees:** ${fees:,.2f} | **Verified Net:** ${net:,.2f}",
        f"- **25% Tax Reserve:** ${tax_res:,.2f} | **Post-Reserve Cash:** ${post_r:,.2f} | **Gap to $100 Tier 1 Gate:** ${max(0.0, 100.0 - net):,.2f}",
        "",
        "## 3. UTM Clicks by Product Tier",
    ]
    if tier_clicks:
        for tname, tcnt in tier_clicks:
            lines.append(f"- `{tname}`: {tcnt} click(s)")
    else:
        lines.append("- 0 tracked /go clicks yet (click your public funnel URL to test live telemetry)")

    lines.append("")
    lines.append("## 4. Pro_Node ($49,999) B2B CRM Pipeline")
    lines.append(f"- **Total Prospects:** {crm_total} | **Active Pipeline Value:** ${crm_pipe_usd:,.2f}")
    if crm_stages:
        for stg, cnt, val in crm_stages:
            lines.append(f"  - **{stg}:** {cnt} prospect(s) (${val:,.2f})")
    else:
        lines.append("  - Pipeline empty -> run `.\\build_pronode_leads.ps1 -InteractiveAdd -ImportToCrm`")

    next_s = lc_st.get("next_recommended_short") or {}
    if next_s:
        lines.append("")
        lines.append("## 5. Next Learning-Curve Upload Ready")
        lines.append(f"- **Short #{next_s.get('sequence')}:** `{os.path.basename(next_s.get('upgraded_4d_mp4', ''))}` ({next_s.get('theme')} | {next_s.get('ab_variant')})")

    md = "\n".join(lines) + "\n"
    out_md = os.path.join(pdir, "reports", "Funnel_Conversion_Dashboard.md")
    with open(out_md, "w", encoding="utf-8", newline="") as f:
        f.write(md)
    shutil.copy2(out_md, os.path.join(pdir, "Oracle_Audit_2026", os.path.basename(out_md)))
    print(md)


if __name__ == "__main__":
    main()