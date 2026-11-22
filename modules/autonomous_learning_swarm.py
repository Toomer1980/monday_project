import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import datetime as dt
import json
import math
import sqlite3
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DATA_DIR = os.path.join(PDIR, "data")
REPORTS_DIR = os.path.join(PDIR, "reports")
PROMO_DIR = os.path.join(PDIR, "deliverables", "promo_campaigns")
for _d in (DATA_DIR, REPORTS_DIR, PROMO_DIR):
    os.makedirs(_d, exist_ok=True)

WEIGHTS_PATH = os.path.join(DATA_DIR, "bandit_strategy_weights.json")

TIERS = {
    "assetpack15": {"price": 15.0, "label": "$15 4D/5D Creator Asset Pack", "path": "/go/assetpack15"},
    "vaultsub15": {"price": 15.0, "label": "$15/mo Sovereign 5D Vault", "path": "/go/vaultsub15"},
    "tier29": {"price": 29.0, "label": "$29 5D Automation Blueprint", "path": "/go/tier29"},
    "auravideo49": {"price": 49.0, "label": "$49 Custom 5D Aura Reading", "path": "/go/auravideo49"},
    "fullstorefront": {"price": 1500.0, "label": "$1,500 Turnkey 4D/5D Creator Stack", "path": "/go/fullstorefront"},
    "pro_node": {"price": 49999.0, "label": "$49,999 Enterprise Dedicated Pro_Node", "path": "/go/pro_node"},
}

HOOK_ANGLES = [
    "PROOF_DEMO",      # Live 4D Tesseract + 5D Mobius visual demonstration
    "ROI_SPEED",       # Eliminate SaaS lock-in / deploy turnkey AI media stack
    "PERSONAL_SHIFT",  # Custom 5D reading rendered with listener's name & focus
    "CREATOR_PACK",    # Instant commercial 4D/5D loops + 2K thumbnails for OBS/YouTube
]


def get_pub_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "https://oraclesystemsllc.com"


def read_live_telemetry():
    clicks_by_tier = {k: 0 for k in TIERS}
    total_clicks = 0
    udb = os.path.join(DATA_DIR, "utm_analytics.db")
    if os.path.exists(udb):
        try:
            c = sqlite3.connect(udb)
            for tk, cnt in c.execute("SELECT tier, COUNT(*) FROM utm_clicks GROUP BY tier").fetchall():
                if tk in clicks_by_tier:
                    clicks_by_tier[tk] = int(cnt)
                total_clicks += int(cnt)
            c.close()
        except Exception:
            pass

    yt_views = 0
    yp = os.path.join(DATA_DIR, "youtube_analytics.json")
    if os.path.exists(yp):
        try:
            yt_views = int((json.load(open(yp, "r", encoding="utf-8")).get("totals") or {}).get("views", 0))
        except Exception:
            pass

    stripe_net = 0.0
    sp = os.path.join(PDIR, "audit_inbox", "stripe_live_api_snapshot.json")
    if os.path.exists(sp):
        try:
            stripe_net = float(json.load(open(sp, "r", encoding="utf-8")).get("charges_net_usd", 0.0))
        except Exception:
            pass

    return {
        "clicks_by_tier": clicks_by_tier,
        "total_clicks": total_clicks,
        "yt_views": yt_views,
        "stripe_net_usd": stripe_net,
    }


def compute_ucb1_weights(telem):
    """Upper Confidence Bound (UCB1) bandit that balances proven click/revenue winners with exploration."""
    prev = json.load(open(WEIGHTS_PATH, "r", encoding="utf-8")) if os.path.exists(WEIGHTS_PATH) else {"cycles": 0, "history": []}
    cycles = int(prev.get("cycles", 0)) + 1
    total_c = max(1, telem["total_clicks"])

    scores = {}
    for tk, meta in TIERS.items():
        n_i = telem["clicks_by_tier"].get(tk, 0)
        # Expected value signal: click share weighted by log(price) so high-ticket B2B + high-volume consumer both compete
        click_rate = n_i / float(total_c)
        ev_weight = click_rate * math.log10(max(10.0, meta["price"]))
        explore = math.sqrt(2.0 * math.log(total_c + cycles + 1.0) / float(n_i + 1.0))
        scores[tk] = round(ev_weight + 0.35 * explore, 4)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_consumer = max(["assetpack15", "vaultsub15", "auravideo49", "tier29"], key=lambda k: scores[k])
    top_b2b = max(["fullstorefront", "pro_node"], key=lambda k: scores[k])
    winning_angle = HOOK_ANGLES[(cycles - 1) % len(HOOK_ANGLES)]

    state = {
        "updated_utc": dt.datetime.utcnow().isoformat() + "Z",
        "cycles": cycles,
        "telemetry_snapshot": telem,
        "ucb1_scores": scores,
        "ranked_tiers": [k for k, _ in ranked],
        "priority_consumer_tier": top_consumer,
        "priority_b2b_tier": top_b2b,
        "active_hook_angle": winning_angle,
        "history": (prev.get("history") or [])[-29:] + [{
            "ts": dt.datetime.utcnow().isoformat() + "Z",
            "total_clicks": telem["total_clicks"],
            "yt_views": telem["yt_views"],
            "stripe_net_usd": telem["stripe_net_usd"],
            "top_consumer": top_consumer,
            "top_b2b": top_b2b,
        }],
    }
    json.dump(state, open(WEIGHTS_PATH, "w", encoding="utf-8"), indent=2)
    return state


def try_ollama_refine(prompt, fallback_text):
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as r:
            models = [m.get("name", "") for m in json.loads(r.read().decode("utf-8")).get("models", [])]
        usable = [m for m in models if not any(b in m.lower() for b in (":0.5b", ":1b", ":1.5b", "tinyllama"))]
        if usable:
            payload = json.dumps({
                "model": usable[0], "prompt": prompt, "stream": False,
                "options": {"temperature": 0.7, "repeat_penalty": 1.25, "num_predict": 240},
            }).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=45) as resp:
                txt = json.loads(resp.read().decode("utf-8")).get("response", "").strip()
                if len(txt) > 80 and "http" in txt:
                    return txt
    except Exception:
        pass
    return fallback_text


def build_promo_campaign(state):
    pub = get_pub_url()
    today = dt.date.today().strftime("%Y%m%d")
    c_key = state["priority_consumer_tier"]
    b_key = state["priority_b2b_tier"]
    c_meta = TIERS[c_key]
    b_meta = TIERS[b_key]
    angle = state["active_hook_angle"]

    c_url = f"{pub}{c_meta['path']}?utm_source=swarm_v2&utm_medium=promo&utm_campaign=cycle{state['cycles']}_{angle}"
    b_url = f"{pub}{b_meta['path']}?utm_source=swarm_b2b&utm_medium=outreach&utm_campaign=cycle{state['cycles']}_{angle}"
    store_url = f"{pub}/store?utm_source=swarm_v2&utm_medium=bio&utm_campaign=cycle{state['cycles']}"

    x_post = (
        f"Built a live 4D Tesseract + 5D Mobius WebGL portal running real-time GLSL shaders, "
        f"1080p/30fps autonomous video rendering & Stripe instant fulfillment on local + cloud infrastructure.\n\n"
        f"Try the live 4D/5D stage: {store_url}\n"
        f"Grab the {c_meta['label']}: {c_url}\n"
        f"#4DTesseract #5DMobius #AIAutomation #CreatorEconomy"
    )

    linkedin_post = (
        f"Most media agencies burn $3,000-$10,000/month on fragmented SaaS seats for video rendering, CRM follow-ups, "
        f"landing pages, and publishing automation.\n\n"
        f"Oracle Systems LLC builds turnkey private AI & 4D/5D media stacks you own outright:\n"
        f"- Live interactive WebGL 4D/5D storefront + Stripe webhook fulfillment\n"
        f"- Automated 1080p/30fps video & YouTube API v3 publishing pipeline\n"
        f"- Private local LLM + Gmail API outreach & analytics telemetry\n\n"
        f"Live demo: {store_url}\n"
        f"Deployment options ({b_meta['label']}): {b_url}\n"
        f"#AgencyAutomation #PrivateAI #MarTech #DigitalMedia"
    )

    tiktok_script = (
        f"[0-3s HOOK] Stop scrolling - watch this live 4D Tesseract rotate through a 5D Mobius strip in real time.\n"
        f"[3-12s VALUE] Every card in our 10-card ray-traced obsidian deck unlocks a studio reading with warm neural voice and 432Hz ambience.\n"
        f"[12-20s CTA] Comment '5D' to claim this shift, then tap the bio link for the live interactive portal ({store_url}) or claim your {c_meta['label']} ({c_url})."
    )

    b2b_cold_email = (
        f"Subject: Cut agency media & AI SaaS overhead with a private 4D/5D automation stack\n\n"
        f"Hi {{FirstName}},\n\n"
        f"I noticed {{Company}} produces high-volume digital media and client campaigns. We built a private turnkey stack at Oracle Systems LLC "
        f"that automates 1080p/30fps motion video rendering, interactive WebGL storefronts, YouTube publishing, and Stripe fulfillment with zero monthly per-seat SaaS lock-in.\n\n"
        f"You can test our live 4D Tesseract & 5D Mobius interactive portal right now here:\n{store_url}\n\n"
        f"We deploy this two ways for partner agencies:\n"
        f"1. Turnkey Software Stack ($1,500 one-time): {pub}/go/fullstorefront?utm_source=b2b_email&utm_campaign=cycle{state['cycles']}\n"
        f"2. Dedicated Enterprise Pro_Node Hardware + Full Stack ($49,999, 50% milestone deposit): {b_url}\n\n"
        f"Open to a quick 10-minute walkthrough this week?\n\n"
        f"Best,\nThomas Toomer\nFounder, Oracle Systems LLC\nReply UNSUBSCRIBE to opt out."
    )

    md = (
        f"# Oracle Systems LLC - Autonomous Swarm Promotion Pack (Cycle #{state['cycles']} | {today})\n"
        f"- **Learning Engine Mode:** UCB1 Closed-Loop Bandit | **Active Hook Angle:** `{angle}`\n"
        f"- **Winning Consumer Focus:** `{c_key}` ({c_meta['label']}) | **Winning B2B Focus:** `{b_key}` ({b_meta['label']})\n"
        f"- **Live Telemetry:** {state['telemetry_snapshot']['yt_views']} YT Views | {state['telemetry_snapshot']['total_clicks']} Verified /go Clicks | ${state['telemetry_snapshot']['stripe_net_usd']:,.2f} Net Stripe\n\n"
        f"## 1. X / Twitter High-CTR Post\n```\n{x_post}\n```\n\n"
        f"## 2. LinkedIn B2B Authority Post (High-Ticket Pipeline)\n```\n{linkedin_post}\n```\n\n"
        f"## 3. TikTok / Reels / YouTube Shorts Voiceover Script\n```\n{tiktok_script}\n```\n\n"
        f"## 4. Compliant B2B Cold Outreach Email ($1,500 & $49,999 Tiers)\n```\n{b2b_cold_email}\n```\n"
    )
    out_md = os.path.join(PROMO_DIR, f"Swarm_Promo_Pack_{today}_C{state['cycles']}.md")
    open(out_md, "w", encoding="utf-8", newline="").write(md)
    open(os.path.join(REPORTS_DIR, "Latest_Swarm_Promo_Pack.md"), "w", encoding="utf-8", newline="").write(md)
    return out_md


def main():
    telem = read_live_telemetry()
    state = compute_ucb1_weights(telem)
    out_md = build_promo_campaign(state)
    print(f"[SWARM LEARN PASS] Cycle #{state['cycles']} | Top Consumer: {state['priority_consumer_tier']} | Top B2B: {state['priority_b2b_tier']} | Angle: {state['active_hook_angle']}")
    print(f"[SWARM PROMO PASS] Generated fresh multi-channel promo & B2B outreach pack -> {out_md}")


if __name__ == "__main__":
    main()
