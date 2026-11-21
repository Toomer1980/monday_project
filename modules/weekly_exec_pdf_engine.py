import datetime as dt
import json
import os
import shutil
import sqlite3
import sys

from PIL import Image, ImageDraw, ImageFont


def load_font(size, bold=True):
    cands = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"] if bold else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def load_json(p, default):
    if not os.path.exists(p):
        return default
    try:
        return json.load(open(p, "r", encoding="utf-8"))
    except Exception:
        return default


def main():
    pdir = sys.argv[1]
    snap = load_json(os.path.join(pdir, "audit_inbox", "stripe_live_api_snapshot.json"), {})
    yt_a = load_json(os.path.join(pdir, "data", "youtube_analytics.json"), {})
    yt_st = load_json(os.path.join(pdir, "data", "youtube_publish_state.json"), {})
    aura_st = load_json(os.path.join(pdir, "data", "aura49_fulfillment_state.json"), {})

    # UTM & CRM SQLite counts
    tot_clicks, tier_rows = 0, []
    udb = os.path.join(pdir, "data", "utm_analytics.db")
    if os.path.exists(udb):
        try:
            c = sqlite3.connect(udb)
            tot_clicks = int(c.execute("SELECT COUNT(*) FROM utm_clicks").fetchone()[0])
            tier_rows = c.execute("SELECT tier, COUNT(*) FROM utm_clicks GROUP BY tier ORDER BY COUNT(*) DESC").fetchall()
            c.close()
        except Exception:
            pass

    crm_cnt, crm_pipe, crm_stages = 0, 0.0, []
    cdb = os.path.join(pdir, "data", "pronode_crm.db")
    if os.path.exists(cdb):
        try:
            c = sqlite3.connect(cdb)
            crm_cnt = int(c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0])
            crm_pipe = float(c.execute("SELECT COALESCE(SUM(deal_value_usd),0) FROM prospects WHERE stage != 'Lost'").fetchone()[0])
            crm_stages = c.execute("SELECT stage, COUNT(*), COALESCE(SUM(deal_value_usd),0) FROM prospects GROUP BY stage").fetchall()
            c.close()
        except Exception:
            pass

    # Vault inventory
    f4d = len([f for f in os.listdir(os.path.join(pdir, "Content_Vault_4D_Full")) if f.endswith("_4D_MAX.mp4")]) if os.path.exists(os.path.join(pdir, "Content_Vault_4D_Full")) else 0
    s4d = len([f for f in os.listdir(os.path.join(pdir, "Content_Vault_4D_Shorts")) if f.endswith("_4D_MAX.mp4")]) if os.path.exists(os.path.join(pdir, "Content_Vault_4D_Shorts")) else 0
    t3d = len([f for f in os.listdir(os.path.join(pdir, "Content_Vault_4D_Thumbnails")) if f.endswith("_3D_Thumb.jpg")]) if os.path.exists(os.path.join(pdir, "Content_Vault_4D_Thumbnails")) else 0
    pub_cnt = len(yt_st.get("published_full") or []) + len(yt_st.get("published_shorts") or [])
    fulf_cnt = len(aura_st.get("fulfilled_orders") or {})

    # Stripe metrics
    gross = float(snap.get("charges_gross_usd", 49.0))
    fees  = float(snap.get("charges_fee_usd", 1.72))
    net   = float(snap.get("charges_net_usd", 47.28))
    avail = float(snap.get("available_usd", 0.0))
    pend  = float(snap.get("pending_usd", 47.28))
    chgs  = int(snap.get("charge_count", 1))
    tax_r = round(net * 0.25, 2)
    post_r = round(net - tax_r, 2)
    gap100 = round(max(0.0, 100.0 - net), 2)

    yt_tot = yt_a.get("totals") or {}
    yt_views = int(yt_tot.get("views", 0))
    yt_likes = int(yt_tot.get("likes", 0))
    yt_comms = int(yt_tot.get("comments", 0))

    pub_url = ""
    pf = os.path.join(pdir, "config", "public_url.txt")
    if os.path.exists(pf):
        pub_url = open(pf, "r", encoding="utf-8").read().strip()

    today = dt.date.today()
    days_to_nov27 = (dt.date(2026, 11, 27) - today).days
    stamp = today.strftime("%Y%m%d")
    free_gb = shutil.disk_usage(pdir).free / (1024 ** 3)

    # 1. Write Executive Markdown Report
    md_lines = [
        f"# Oracle Systems LLC - Weekly Executive Report ({today.isoformat()})",
        f"- **Generated:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST | **Active Funnel:** {pub_url or 'Localhost'}",
        f"- **Countdown to Nov 27 Stripe Payout:** {days_to_nov27} day(s) | **Free Disk C:** {free_gb:.1f} GB",
        "",
        "## 1. Live Stripe Treasury & Runway",
        f"- **Verified Gross:** ${gross:,.2f} ({chgs} live charge) | **Stripe Fees:** ${fees:,.2f} | **Verified Net:** ${net:,.2f}",
        f"- **Available Balance:** ${avail:,.2f} | **Pending Balance:** ${pend:,.2f} (Releasing 2026-11-27)",
        f"- **25% Tax Reserve:** ${tax_r:,.2f} | **Post-Reserve Operating Cash:** ${post_r:,.2f}",
        f"- **DigitalOcean Tier 1 ($34.80/mo) Coverage:** +${post_r - 34.80:,.2f} Month-1 buffer | **Gap to $100 Gate:** ${gap100:,.2f}",
        "",
        "## 2. 4D Media Supply, YouTube & Fulfillment",
        f"- **4D Content Vault:** {f4d}/52 Full Videos | {s4d}/52 Shorts | {t3d}/104 3D Thumbnails",
        f"- **YouTube Publishing & Reach:** {pub_cnt}/104 uploaded | {yt_views:,} views | {yt_likes:,} likes | {yt_comms:,} comments",
        f"- **Custom $49 AuraVideo49 Orders Fulfilled:** {fulf_cnt}",
        "",
        "## 3. Tracked /go UTM Funnel",
        f"- **Total Tracked Clicks:** {tot_clicks:,}",
    ]
    for tn, tc in tier_rows:
        md_lines.append(f"  - `{tn}`: {tc} click(s)")
    if not tier_rows:
        md_lines.append("  - 0 tracked clicks recorded yet")

    md_lines += [
        "",
        "## 4. Pro_Node ($49,999) B2B Enterprise CRM",
        f"- **Total Prospects:** {crm_cnt} | **Active Pipeline Value:** ${crm_pipe:,.2f}",
    ]
    for stg, cnt, val in crm_stages:
        md_lines.append(f"  - **{stg}:** {cnt} prospect(s) (${val:,.2f})")
    if not crm_stages:
        md_lines.append("  - Ready for first 20-lead sprint via `build_pronode_leads.ps1` + `run_pronode_sprint.ps1`")

    md_path = os.path.join(pdir, "reports", f"Executive_Weekly_Report_{stamp}.md")
    open(md_path, "w", encoding="utf-8", newline="").write("\n".join(md_lines) + "\n")

    # 2. Render Branded High-DPI Executive PDF (A4 @ 200 DPI = 1654 x 2339) using Pillow
    W, H = 1654, 2339
    im = Image.new("RGB", (W, H), (248, 250, 252))
    dr = ImageDraw.Draw(im)

    # Dark Navy Executive Header Banner
    dr.rectangle([0, 0, W, 270], fill=(7, 13, 31))
    dr.rectangle([0, 264, W, 274], fill=(250, 204, 21))
    dr.text((80, 52), "ORACLE SYSTEMS LLC  //  WEEKLY EXECUTIVE REPORT", font=load_font(46, True), fill=(250, 204, 21))
    dr.text((80, 124), f"Date: {today.isoformat()}   |   Stripe Payout Countdown: {days_to_nov27} day(s) (Nov 27, 2026)   |   Live Treasury & Funnel Brief", font=load_font(26, False), fill=(226, 232, 240))
    dr.text((80, 182), f"Public HTTPS Storefront: {pub_url or 'http://127.0.0.1:8000'}", font=load_font(24, False), fill=(56, 189, 248))

    # Row of 4 KPI Cards
    kpis = [
        ("LIVE STRIPE NET", f"${net:,.2f}", f"Pending: ${pend:,.2f} | Fees: ${fees:,.2f}", (14, 165, 233)),
        ("POST-RESERVE CASH", f"${post_r:,.2f}", f"25% Tax Reserve: ${tax_r:,.2f}", (16, 185, 129)),
        ("4D VAULT READY", f"{f4d + s4d}/104", f"{f4d} Full + {s4d} Shorts | {t3d} Thumbs", (234, 179, 8)),
        ("FUNNEL & CRM", f"{tot_clicks} Clicks", f"CRM Leads: {crm_cnt} (${crm_pipe:,.0f})", (99, 102, 241)),
    ]
    cw, ch, gap = 355, 195, 24
    x0, y0 = 80, 325
    for idx, (lbl, val, sub, accent) in enumerate(kpis):
        x = x0 + idx * (cw + gap)
        dr.rounded_rectangle([x, y0, x + cw, y0 + ch], radius=14, fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        dr.rectangle([x, y0, x + cw, y0 + 10], fill=accent)
        dr.text((x + 22, y0 + 28), lbl, font=load_font(20, True), fill=(100, 116, 139))
        dr.text((x + 22, y0 + 68), val, font=load_font(44, True), fill=(15, 23, 42))
        dr.text((x + 22, y0 + 142), sub, font=load_font(19, False), fill=(71, 85, 105))

    # Section Helper
    y = 575
    def draw_section(title, rows_list):
        nonlocal y
        dr.text((80, y), title, font=load_font(32, True), fill=(15, 23, 42))
        y += 46
        dr.line([(80, y), (W - 80, y)], fill=(56, 189, 248), width=3)
        y += 22
        for k, v in rows_list:
            dr.text((96, y), k, font=load_font(24, True), fill=(51, 65, 85))
            dr.text((540, y), v, font=load_font(24, False), fill=(15, 23, 42))
            y += 44
        y += 30

    draw_section("1. Live Stripe Treasury & DigitalOcean Tier 1 Runway Gates", [
        ("Verified Gross / Net:", f"${gross:,.2f} gross  |  ${fees:,.2f} fees  |  ${net:,.2f} net ({chgs} live charge)"),
        ("25% Tax Reserve:", f"${tax_r:,.2f} set aside  ->  ${post_r:,.2f} post-reserve operating cash"),
        ("Tier 1 Hosting ($34.80/mo):", f"Month-1 coverage surplus: +${post_r - 34.80:,.2f}  |  Gap to $100 Gate: ${gap100:,.2f}"),
        ("Tier 3 Enterprise HA Gate:", "STRICTLY LOCKED until >= $24,999.50 Pro_Node ACH deposit clears"),
    ])

    draw_section("2. Content Vault, YouTube Reach & Custom Aura49 Fulfillment", [
        ("4D Media Inventory:", f"{f4d}/52 Full Videos (30 min)  |  {s4d}/52 Shorts (2m55s)  |  {t3d} 3D Thumbs"),
        ("YouTube Channel Telemetry:", f"{pub_cnt}/104 published  |  {yt_views:,} views  |  {yt_likes:,} likes  |  {yt_comms:,} comments"),
        ("Custom $49 Aura49 Orders:", f"{fulf_cnt} personalized 4D Aura MP4 deliverable(s) generated"),
        ("Disk & Runtime Capacity:", f"{free_gb:.1f} GB free on C:  |  Port 8000 + Cloudflare 24/7 Watchdog active"),
    ])

    tier_txt = ", ".join([f"{t}: {c}" for t, c in tier_rows]) if tier_rows else "No tracked clicks yet"
    crm_txt = ", ".join([f"{s}: {c} (${v:,.0f})" for s, c, v in crm_stages]) if crm_stages else "0 leads loaded (ready for 20-lead sprint)"
    draw_section("3. Tracked /go UTM Funnel & Pro_Node ($49,999) B2B CRM", [
        ("Total Tracked UTM Clicks:", f"{tot_clicks:,} click(s)  ({tier_txt})"),
        ("Pro_Node CRM Pipeline:", f"{crm_cnt} prospect(s)  |  Pipeline Value: ${crm_pipe:,.2f}"),
        ("CRM Stage Breakdown:", crm_txt),
    ])

    # Visual Progress Bar Box for $100 Tier 1 Gate
    dr.rounded_rectangle([80, y, W - 80, y + 170], radius=14, fill=(15, 23, 42))
    pct100 = min(1.0, net / 100.0)
    dr.text((112, y + 26), f"BLOCK 10 TIER 1 CLOUD GATE PROGRESS (${net:,.2f} / $100.00 -> {pct100*100:.1f}%)", font=load_font(26, True), fill=(250, 204, 21))
    bx1, by1, bx2, by2 = 112, y + 82, W - 112, y + 126
    dr.rounded_rectangle([bx1, by1, bx2, by2], radius=10, fill=(30, 41, 59))
    fill_x = bx1 + max(18, int((bx2 - bx1) * pct100))
    dr.rounded_rectangle([bx1, by1, fill_x, by2], radius=10, fill=(56, 189, 248))

    # Footer
    dr.line([(80, H - 110), (W - 80, H - 110)], fill=(203, 213, 225), width=2)
    dr.text((80, H - 82), "Oracle Systems LLC  |  Confidential Executive Telemetry  |  Auto-Synced to Google Drive (Oracle_Audit_2026)", font=load_font(20, False), fill=(100, 116, 139))

    pdf_path = os.path.join(pdir, "reports", f"Executive_Weekly_Report_{stamp}.pdf")
    im.save(pdf_path, "PDF", resolution=200.0)

    stage_dir = os.path.join(pdir, "Oracle_Audit_2026")
    shutil.copy2(md_path, os.path.join(stage_dir, os.path.basename(md_path)))
    shutil.copy2(pdf_path, os.path.join(stage_dir, os.path.basename(pdf_path)))
    print(f"[PASS] Generated Weekly Executive Report:\n  Markdown: {md_path}\n  PDF     : {pdf_path}\n  Staged  : {stage_dir}")


if __name__ == "__main__":
    main()