import datetime as dt
import html
import json
import os
import sqlite3
import requests

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DATA_DIR = os.path.join(PDIR, "data")
REPORTS_DIR = os.path.join(PDIR, "reports")
TOK_P = os.path.join(PDIR, "config", "youtube_token.json")
YT_UPLOADS = os.path.join(DATA_DIR, "youtube_ultra_4d5d_uploads.json")
COMMENT_LOG = os.path.join(DATA_DIR, "yt_promo_comments_posted.json")
LEADS_JSON = os.path.join(DATA_DIR, "verified_b2b_agency_leads.json")
BROADCAST_MD = os.path.join(REPORTS_DIR, "Live_Revenue_Promo_Broadcast.md")
HUB_HTML = os.path.join(REPORTS_DIR, "Oracle_Revenue_Lead_Command_Center.html")


def get_pub_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "https://oraclesystemsllc.com"


def load_env():
    env = {}
    ep = os.path.join(PDIR, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8", errors="ignore"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get_yt_token():
    if not os.path.exists(TOK_P):
        return ""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = Credentials.from_authorized_user_file(TOK_P)
        if not creds.valid or creds.expired or not creds.token:
            creds.refresh(Request())
        return creds.token
    except Exception:
        return ""


def post_youtube_conversion_comments(pub_url):
    token = get_yt_token()
    if not token:
        print("[YT-PROMO] No YouTube OAuth token found; skipping live comment boost.")
        return 0

    posted = json.load(open(COMMENT_LOG, "r", encoding="utf-8")) if os.path.exists(COMMENT_LOG) else {}
    up = json.load(open(YT_UPLOADS, "r", encoding="utf-8")) if os.path.exists(YT_UPLOADS) else {}
    vid_map = dict(up.get("uploaded_files") or {})
    # Ensure our newly published live videos are included
    for fname, vid in [
        ("Week_01_Sudden_Breakthrough_4D_MAX.mp4", "koFpuMKuN8Y"),
        ("Week_02_Silent_Abundance_Financial_Breakthrough_REAL_FULL.mp4", "rYqNeXOpAWw"),
        ("Short_01_Sudden_Breakthrough_4D_MAX.mp4", "fup8wv10BUY"),
        ("Short_13_Abundance_Magnet_4D_MAX.mp4", "pmvlbk78ioc"),
        ("Short_14_Clearing_Blockages_4D_MAX.mp4", "_ei8UAZ371Q"),
    ]:
        vid_map.setdefault(fname, vid)

    hdrs = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    posted_now = 0
    for fname, vid in vid_map.items():
        if vid in posted:
            continue
        is_short = fname.lower().startswith("short_")
        if is_short:
            text = (
                "Full 10-minute 4D Tesseract & 5D Mobius reading is live here: https://youtu.be/koFpuMKuN8Y\n"
                f"Draw your own live 3-card 4D/5D spread or claim a custom $49 Aura Reading: {pub_url}/store?utm_source=yt_comment&utm_medium=short&utm_campaign={vid}\n"
                "Drop 'I CLAIM THIS 5D SHIFT' below if this resonated!"
            )
        else:
            text = (
                f"Step into the live interactive 4D Tesseract & 5D Mobius Tarot Portal here: {pub_url}/store?utm_source=yt_comment&utm_medium=full&utm_campaign={vid}\n"
                f"Custom Personalized 5D Aura Reading ($49): {pub_url}/go/auravideo49?utm_source=yt_comment&utm_campaign={vid}\n"
                f"4D/5D Creator Asset Pack ($15 instant ZIP): {pub_url}/go/assetpack15?utm_source=yt_comment&utm_campaign={vid}\n"
                "Which card spoke loudest to your timeline today?"
            )
        payload = {
            "snippet": {
                "videoId": vid,
                "topLevelComment": {"snippet": {"textOriginal": text}},
            }
        }
        try:
            r = requests.post(
                "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet",
                headers=hdrs, data=json.dumps(payload).encode("utf-8"), timeout=20,
            )
            if r.status_code in (200, 201):
                posted[vid] = {"posted_utc": dt.datetime.utcnow().isoformat() + "Z", "comment_id": r.json().get("id", "")}
                posted_now += 1
                print(f"  [YT COMMENT LIVE] Posted conversion comment on https://youtu.be/{vid}")
            else:
                print(f"  [YT COMMENT NOTE] {vid}: HTTP {r.status_code} ({r.text[:110]})")
        except Exception as ex:
            print(f"  [YT COMMENT NOTE] {vid}: {str(ex)[:110]}")

    json.dump(posted, open(COMMENT_LOG, "w", encoding="utf-8"), indent=2)
    return posted_now


def try_live_social_apis(env, x_text, li_text):
    sent_channels = []
    x_tok = env.get("X_USER_ACCESS_TOKEN") or env.get("TWITTER_BEARER_USER_TOKEN")
    if x_tok:
        try:
            r = requests.post(
                "https://api.twitter.com/2/tweets",
                headers={"Authorization": f"Bearer {x_tok}", "Content-Type": "application/json"},
                json={"text": x_text[:278]}, timeout=15,
            )
            if r.status_code in (200, 201):
                sent_channels.append("X_LIVE")
        except Exception:
            pass
    li_tok = env.get("LINKEDIN_ACCESS_TOKEN")
    li_urn = env.get("LINKEDIN_AUTHOR_URN")
    if li_tok and li_urn:
        try:
            r = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers={"Authorization": f"Bearer {li_tok}", "X-Restli-Protocol-Version": "2.0.0", "Content-Type": "application/json"},
                json={
                    "author": li_urn, "lifecycleState": "PUBLISHED",
                    "specificContent": {"com.linkedin.ugc.ShareContent": {"shareCommentary": {"text": li_text}, "shareMediaCategory": "NONE"}},
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
                }, timeout=15,
            )
            if r.status_code in (200, 201):
                sent_channels.append("LINKEDIN_LIVE")
        except Exception:
            pass
    return sent_channels


def build_command_hub_html(pub_url, leads_data, streams, yt_comments_posted):
    direct = leads_data.get("direct_email_leads") or []
    forms = leads_data.get("contact_form_leads") or []
    today_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M EST")

    pitch_tpl = (
        f"Hi Team,%0A%0AWe built a private turnkey 4D/5D media & local AI automation stack at Oracle Systems LLC "
        f"that replaces $3k-$10k/mo in fragmented SaaS rendering, WebGL storefront, YouTube API & Stripe automation tools.%0A%0A"
        f"Live 4D Tesseract & 5D Mobius Demo: {pub_url}/store%0A"
        f"Turnkey Creator Stack ($1,500 one-time): {pub_url}/go/fullstorefront%0A"
        f"Dedicated Enterprise Pro_Node ($49,999): {pub_url}/go/pro_node%0A%0A"
        f"Open to a quick 10-min walkthrough this week?%0A%0ABest,%0AThomas Toomer — Oracle Systems LLC"
    )

    stream_cards = ""
    for st in streams:
        stream_cards += (
            f'<div class="card">'
            f'<div class="kicker">{html.escape(st["role"])}</div>'
            f'<div class="price">{html.escape(st["price"])}</div>'
            f'<div class="name">{html.escape(st["name"])}</div>'
            f'<p>{html.escape(st["hook"])}</p>'
            f'<a class="btn" href="{html.escape(st["url"])}" target="_blank">Open Tracked Checkout / Demo</a>'
            f'</div>'
        )

    email_rows = ""
    for r in direct:
        mailto = f"mailto:{r['email']}?subject=Private%204D%2F5D%20AI%20%26%20Video%20Automation%20Stack%20for%20{requests.utils.quote(r['company'])}&body={pitch_tpl}"
        email_rows += (
            f"<tr><td><span class='pill'>{r['icp_score']}</span></td>"
            f"<td><strong>{html.escape(r['company'])}</strong></td>"
            f"<td><code>{html.escape(r['email'])}</code></td>"
            f"<td>{html.escape(r['target_tier'])}</td>"
            f"<td>{html.escape(r['niche'])}</td>"
            f"<td><a class='mini-btn' href='{mailto}'>1-Click Email</a></td></tr>"
        )

    form_rows = ""
    for r in forms:
        form_rows += (
            f"<tr><td><span class='pill'>{r['icp_score']}</span></td>"
            f"<td><strong>{html.escape(r['company'])}</strong></td>"
            f"<td>{html.escape(r['target_tier'])}</td>"
            f"<td>{html.escape(r['niche'])}</td>"
            f"<td><a class='mini-btn' href='{html.escape(r['contact_url'])}' target='_blank'>Open Contact Form</a></td></tr>"
        )

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Oracle Systems LLC // Revenue &amp; B2B Lead Command Center</title>
<style>
  body{{background:#030712;color:#e2e8f0;font-family:"Segoe UI",system-ui,sans-serif;margin:0;padding:28px;}}
  .wrap{{max-width:1280px;margin:0 auto;}}
  h1{{font-size:28px;margin:0 0 6px;background:linear-gradient(90deg,#facc15,#38bdf8,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
  .sub{{color:#94a3b8;font-size:13px;margin-bottom:22px;}}
  .kpi-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:26px;}}
  .kpi{{background:#0f172a;border:1px solid rgba(56,189,248,0.3);border-radius:12px;padding:16px;}}
  .kpi .v{{font-size:26px;font-weight:900;color:#facc15;}}
  .kpi .l{{font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:1.2px;}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px;margin-bottom:30px;}}
  .card{{background:#0b1224;border:1px solid rgba(250,204,21,0.28);border-radius:12px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;}}
  .kicker{{font-size:10px;color:#38bdf8;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;}}
  .price{{font-size:24px;font-weight:900;color:#facc15;margin:4px 0;}}
  .name{{font-weight:700;color:#f8fafc;margin-bottom:6px;}}
  .card p{{font-size:12.5px;color:#94a3b8;line-height:1.45;margin:0 0 14px;}}
  .btn{{display:block;text-align:center;padding:9px 12px;border-radius:8px;background:linear-gradient(90deg,#facc15,#38bdf8);color:#020617;font-weight:800;font-size:12px;text-decoration:none;}}
  h2{{font-size:18px;color:#f8fafc;margin:26px 0 10px;border-left:4px solid #facc15;padding-left:10px;}}
  table{{width:100%;border-collapse:collapse;background:#0b1224;border-radius:10px;overflow:hidden;font-size:13px;}}
  th,td{{padding:10px 12px;border-bottom:1px solid rgba(148,163,184,0.14);text-align:left;}}
  th{{background:#111c36;color:#38bdf8;font-size:11px;text-transform:uppercase;letter-spacing:1px;}}
  .pill{{display:inline-block;padding:2px 8px;border-radius:999px;background:rgba(16,185,129,0.2);color:#6ee7b7;font-weight:800;font-size:11px;}}
  .mini-btn{{display:inline-block;padding:5px 10px;border-radius:6px;background:#1e293b;border:1px solid #38bdf8;color:#e2e8f0;text-decoration:none;font-size:11px;font-weight:700;}}
  .mini-btn:hover{{background:#38bdf8;color:#020617;}}
  code{{color:#fde047;}}
</style></head><body><div class="wrap">
  <h1>ORACLE SYSTEMS LLC // REVENUE STREAMS &amp; B2B LEAD COMMAND CENTER</h1>
  <div class="sub">Generated {today_str} | Live Storefront: <a href="{html.escape(pub_url)}/store" style="color:#38bdf8;" target="_blank">{html.escape(pub_url)}/store</a></div>
  <div class="kpi-row">
    <div class="kpi"><div class="l">Agencies Audited</div><div class="v">{leads_data.get('total_agencies_audited', 0)}</div></div>
    <div class="kpi"><div class="l">MX-Verified Direct Emails</div><div class="v">{len(direct)}</div></div>
    <div class="kpi"><div class="l">Contact-Form Agencies</div><div class="v">{len(forms)}</div></div>
    <div class="kpi"><div class="l">Active Stripe Streams</div><div class="v">6 Tiers ($15-$49,999)</div></div>
    <div class="kpi"><div class="l">YT Promo Comments Posted</div><div class="v">{yt_comments_posted}</div></div>
  </div>
  <h2>6 Active Multi-Stream Revenue Funnels (Tracked UTM Links)</h2>
  <div class="grid">{stream_cards}</div>
  <h2>MX-Verified Public Business Email Leads (Loaded in pronode_crm.db)</h2>
  <table><thead><tr><th>ICP</th><th>Agency</th><th>Verified Email</th><th>Target Offer</th><th>Niche</th><th>Action</th></tr></thead>
  <tbody>{email_rows or '<tr><td colspan="6">Run b2b_public_lead_harvester.py to populate direct emails.</td></tr>'}</tbody></table>
  <h2>High-Value Contact-Form Agencies (Copy Pitch from Latest_Swarm_Promo_Pack.md)</h2>
  <table><thead><tr><th>ICP</th><th>Agency</th><th>Target Offer</th><th>Niche</th><th>Action</th></tr></thead>
  <tbody>{form_rows}</tbody></table>
</div></body></html>"""
    open(HUB_HTML, "w", encoding="utf-8", newline="").write(doc)
    return HUB_HTML


def main():
    pub = get_pub_url()
    env = load_env()
    today = dt.date.today().isoformat()

    streams = [
        {"key": "assetpack15", "name": "4D/5D Creator Asset Pack", "price": "$15", "role": "Impulse Entry + List Builder",
         "hook": "Instant commercial ZIP: 4D Tesseract & 5D Mobius loops + 2K QHD ray-traced thumbnails for OBS, YouTube & TikTok.",
         "url": f"{pub}/go/assetpack15?utm_source=promo_hub&utm_medium=multi&utm_campaign={today}"},
        {"key": "vaultsub15", "name": "Sovereign 5D Member Vault", "price": "$15/mo", "role": "Compounding MRR Subscription",
         "hook": "Unlimited full-length 1080p/30fps 7-chapter 4D/5D readings + ad-free 432Hz studio audio drops.",
         "url": f"{pub}/go/vaultsub15?utm_source=promo_hub&utm_medium=multi&utm_campaign={today}"},
        {"key": "tier29", "name": "5D Automation Blueprint", "price": "$29", "role": "Digital Creator Upsell",
         "hook": "Complete 52-week 4D/5D video automation, SEO chapter architecture & YouTube monetization playbook.",
         "url": f"{pub}/go/tier29?utm_source=promo_hub&utm_medium=multi&utm_campaign={today}"},
        {"key": "auravideo49", "name": "Custom 5D Aura Reading", "price": "$49", "role": "Flagship Consumer Cashflow",
         "hook": "Bespoke 1080p 4D Tesseract & 5D Mobius tarot cinema video rendered with your name, focus & Irish studio narration.",
         "url": f"{pub}/go/auravideo49?utm_source=promo_hub&utm_medium=multi&utm_campaign={today}"},
        {"key": "fullstorefront", "name": "Turnkey 4D/5D Creator Stack", "price": "$1,500", "role": "Fast B2B Agency Cash Engine",
         "hook": "Own your full WebGL 4D/5D storefront, Stripe fulfillment, YouTube API pipeline & local Ollama CRM outright.",
         "url": f"{pub}/go/fullstorefront?utm_source=promo_hub&utm_medium=b2b&utm_campaign={today}"},
        {"key": "pro_node", "name": "Enterprise Dedicated Pro_Node", "price": "$49,999", "role": "High-Ticket Enterprise Deal",
         "hook": "Private on-prem AI & autonomous 4D/5D video compute hardware + full stack (50% Stripe ACH Milestone 1).",
         "url": f"{pub}/go/pro_node?utm_source=promo_hub&utm_medium=b2b&utm_campaign={today}"},
    ]

    x_post = (
        f"Just pushed our live 4D Tesseract + 5D Mobius WebGL portal + 1080p/30fps autonomous YouTube & Stripe engine.\n"
        f"Try the live 3-card portal: {pub}/store?utm_source=x&utm_campaign={today}\n"
        f"$15 Creator Pack: {pub}/go/assetpack15?utm_source=x\n"
        f"$1,500 Turnkey Agency Stack: {pub}/go/fullstorefront?utm_source=x\n"
        "#AIAutomation #4DTesseract #CreatorEconomy"
    )
    li_post = (
        "Agencies are burning $3,000-$10,000/month renting fragmented video rendering, landing page, YouTube publishing, and CRM SaaS tools.\n\n"
        "At Oracle Systems LLC we deploy turnkey private 4D/5D media & local AI stacks you own outright:\n"
        "- Live interactive 4D Tesseract + 5D Mobius storefront with Stripe webhook fulfillment\n"
        "- Automated 1080p/30fps cinema & Shorts rendering + pure-HTTP YouTube API publishing\n"
        "- Private local LLM lead enrichment, Proposal PDF generation & CRM follow-ups\n\n"
        f"Live Demo: {pub}/store?utm_source=linkedin&utm_campaign={today}\n"
        f"Turnkey Stack ($1,500): {pub}/go/fullstorefront?utm_source=linkedin\n"
        f"Enterprise Pro_Node ($49,999): {pub}/go/pro_node?utm_source=linkedin\n"
        "#AgencyGrowth #MarTech #VideoAutomation #PrivateAI"
    )
    yt_community = (
        "NEW 10-MINUTE 4D TESSERACT & 5D MOBIUS FULL READING IS LIVE!\n"
        "Watch 'Sudden Breakthrough & Financial Shift' here: https://youtu.be/koFpuMKuN8Y\n\n"
        f"Draw your own interactive 3-card spread right now: {pub}/store?utm_source=yt_community&utm_campaign={today}\n"
        f"Order a Custom Personalized 5D Aura Reading ($49): {pub}/go/auravideo49?utm_source=yt_community\n"
        "Vote below: Which card has been following you this week? (The Magician / Wheel of Fortune / The Sun / The Star)"
    )

    yt_posted = post_youtube_conversion_comments(pub)
    live_socials = try_live_social_apis(env, x_post, li_post)

    md = [
        f"# Oracle Systems LLC - Multi-Stream Revenue Promo Broadcast ({today})",
        f"- **Live YouTube Conversion Comments Published Now:** {yt_posted}",
        f"- **Live Social API Dispatches:** {', '.join(live_socials) if live_socials else 'Staged (add X_USER_ACCESS_TOKEN / LINKEDIN_ACCESS_TOKEN to .env for auto-post)'}",
        "",
        "## 1. X / Twitter Ready-to-Post",
        f"```\n{x_post}\n```",
        "",
        "## 2. LinkedIn B2B Agency Authority Post ($1,500 & $49,999)",
        f"```\n{li_post}\n```",
        "",
        "## 3. YouTube Community Tab Post",
        f"```\n{yt_community}\n```",
        "",
        "## 4. All 6 Tracked Revenue Stream Links",
    ]
    for st in streams:
        md.append(f"- **{st['name']} ({st['price']}):** {st['url']}")
    open(BROADCAST_MD, "w", encoding="utf-8", newline="").write("\n".join(md) + "\n")

    leads_data = json.load(open(LEADS_JSON, "r", encoding="utf-8")) if os.path.exists(LEADS_JSON) else {}
    hub_path = build_command_hub_html(pub, leads_data, streams, yt_posted)
    print(f"[MULTI-STREAM PROMO PASS] Broadcast saved -> {BROADCAST_MD} | Live YT Comments: {yt_posted} | Command Center -> {hub_path}")


if __name__ == "__main__":
    main()
