import datetime as dt
import json
import os
import shutil
import urllib.error
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
os.chdir(PDIR)


def get_public_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "https://marsh-wonder-governments-solve.trycloudflare.com"


def get_next_video_meta():
    qpath = os.path.join(PDIR, "reports", "learning_curve_ranked_queue.json")
    if os.path.exists(qpath):
        try:
            q = json.load(open(qpath, "r", encoding="utf-8"))
            s = (q.get("meta") or {}).get("next_recommended_short") or {}
            if s:
                return {
                    "title": s.get("ab_recommended_title") or "4D Tesseract Quantum Alignment",
                    "theme": s.get("theme") or "Financial_Windfall",
                    "seq": str(s.get("sequence") or "09"),
                    "campaign": os.path.splitext(os.path.basename(s.get("upgraded_4d_mp4") or "Short_09"))[0],
                }
        except Exception:
            pass
    return {
        "title": "4D Tesseract Quantum Portal | Sudden Windfall Alignment",
        "theme": "Financial_Windfall",
        "seq": "09",
        "campaign": "Short_09_Sudden_Windfall",
    }


def detect_ollama_model():
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8"))
            names = [m.get("name", "") for m in data.get("models", [])]
            for pref in ("qwen2.5", "llama3.2", "llama3", "dolphin3", "tinyllama"):
                for n in names:
                    if n.lower().startswith(pref):
                        return n
            return names[0] if names else ""
    except Exception:
        return ""


def ollama_generate(model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 650},
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8")).get("response", "").strip()


def build_fallback_pack(vid, links):
    return (
        "## 1. YouTube Pinned Comment (Paste on Live Short https://youtu.be/Wxxxgco7AX4)\n"
        f"Step inside the full 4D Tesseract Portal:\n"
        f"- Grab the $15 4D Creator Asset Pack (loops + 3D templates): {links['pack15']}\n"
        f"- Join the $15/mo Sovereign 4D Member Vault (30-min transmissions + 432Hz audio): {links['vault15']}\n"
        f"- Order your Custom Personalized 4D Aura Reading ($49): {links['aura49']}\n\n"
        "## 2. X / Twitter Post\n"
        f"Most creators burn hours rendering visuals manually.\n\n"
        f"We built a 4D Tesseract & Mobius visual engine that outputs 104+ seamless loops and 3D assets on a single local GPU.\n\n"
        f"Download the commercial-use $15 Creator Asset Pack here:\n{links['pack15']}\n\n"
        "## 3. TikTok / Instagram Reels Caption\n"
        f"Pause for 3 seconds and let the rotating 4D hypercube reset your focus on {vid['theme'].replace('_', ' ')}.\n"
        f"Comment 'ALIGN' if this hit your feed at the exact right moment.\n"
        f"Custom 4D Aura Reading ($49) & $15 Creator Pack in bio -> {links['aura49']}\n"
        "#4DTesseract #MobiusStrip #QuantumAlignment #OracleSystems #AICreator\n\n"
        "## 4. LinkedIn B2B Authority Post (Agency / Pro_Node Pipeline)\n"
        "Agencies are still paying thousands per month in fragmented SaaS seats for content, CRM, and automation.\n\n"
        "Oracle Systems LLC deploys turnkey autonomous media + local AI pipelines (52-week 4D content engines, Stripe webhooks, and private local LLMs) with zero per-seat lock-in.\n\n"
        f"Preview the live architecture ($1,500 Creator Stack or $49,999 Dedicated Pro_Node):\n{links['pronode']}\n"
    )


def main():
    pub = get_public_url()
    vid = get_next_video_meta()
    camp = vid["campaign"]
    links = {
        "pack15":  f"{pub}/go/assetpack15?utm_source=social&utm_medium=repurpose&utm_campaign={camp}",
        "vault15": f"{pub}/go/vaultsub15?utm_source=yt_pin&utm_medium=comment&utm_campaign={camp}",
        "aura49":  f"{pub}/go/auravideo49?utm_source=tiktok&utm_medium=caption&utm_campaign={camp}",
        "pronode": f"{pub}/go/pro_node?utm_source=linkedin&utm_medium=post&utm_campaign={camp}",
        "store":   f"{pub}/store",
    }

    model = detect_ollama_model()
    body = ""
    engine_label = "Template Fallback (Ollama offline)"
    if model:
        print(f"[OLLAMA] Connected local model '{model}' (RTX 2050 / $0 API cost) -> generating multi-platform copy...")
        prompt = (
            f"You are the marketing director for Oracle Systems LLC. Write crisp, high-converting, ready-to-paste copy "
            f"promoting our 4D Tesseract & Mobius video '{vid['title']}' (Theme: {vid['theme']}).\n"
            f"Output EXACTLY these 4 markdown sections and include the EXACT URLs given:\n"
            f"1. YouTube Pinned Comment (include {links['pack15']}, {links['vault15']}, and {links['aura49']})\n"
            f"2. X / Twitter Post (under 270 chars, promote the $15 4D Creator Asset Pack at {links['pack15']})\n"
            f"3. TikTok / Reels Caption (with 5 hashtags, promote the $49 Custom 4D Aura Reading at {links['aura49']})\n"
            f"4. LinkedIn B2B Post (pitch agencies on turnkey local AI + autonomous media stacks, link {links['pronode']})\n"
            f"No fluff, no placeholders, pure ready-to-publish text."
        )
        try:
            body = ollama_generate(model, prompt)
            engine_label = f"Local Ollama ({model})"
        except Exception as ex:
            print(f"[WARN] Ollama generation note: {ex} -> using high-converting fallback.")

    if not body or len(body) < 120:
        body = build_fallback_pack(vid, links)

    today = dt.date.today().strftime("%Y%m%d")
    out_md = os.path.join(PDIR, "reports", f"Daily_Traffic_Pack_{today}.md")
    header = (
        f"# Oracle Systems LLC - Daily Multi-Platform Traffic Pack ({dt.date.today().isoformat()})\n"
        f"- **Engine:** {engine_label}\n"
        f"- **Target Campaign:** Short #{vid['seq']} (`{camp}`)\n"
        f"- **Live 6-Card Storefront:** {links['store']}\n\n"
    )
    full_md = header + body.strip() + "\n"
    open(out_md, "w", encoding="utf-8", newline="").write(full_md)
    shutil.copy2(out_md, os.path.join(PDIR, "Oracle_Audit_2026", os.path.basename(out_md)))
    print(f"\n[PASS] Generated Traffic Pack -> {out_md} (staged in Oracle_Audit_2026)\n")
    print(full_md)


if __name__ == "__main__":
    main()