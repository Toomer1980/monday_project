import datetime as dt
import json
import os
import shutil
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
    """Prefer 3B-8B models that fit RTX 2050 4GB VRAM; skip sub-2B models that loop on URLs."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8"))
            names = [m.get("name", "") for m in data.get("models", [])]
            bad_tags = (":0.5b", ":1b", ":1.5b", "tinyllama")
            usable = [n for n in names if not any(b in n.lower() for b in bad_tags)]
            for pref in ("qwen2.5:7b", "qwen2.5:3b", "llama3.2", "llama3", "dolphin3", "qwen2.5"):
                for n in usable:
                    if n.lower().startswith(pref):
                        return n
            return usable[0] if usable else ""
    except Exception:
        return ""


def ollama_generate(model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.65, "repeat_penalty": 1.25, "num_predict": 650},
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8")).get("response", "").strip()


def is_valid_copy(text, links):
    if not text or len(text) < 200:
        return False
    if not all(links[k] in text for k in ("pack15", "aura49", "pronode")):
        return False
    non_empty = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(non_empty) >= 8 and (len(set(non_empty)) / float(len(non_empty))) < 0.65:
        return False
    return True


def build_verified_pack(vid, links):
    theme_clean = vid["theme"].replace("_", " ")
    return (
        "## 1. YouTube Pinned Comment (Pin on Live Short https://youtu.be/Wxxxgco7AX4)\n"
        "Step inside the full 4D Tesseract Portal:\n"
        f"- Grab the $15 4D Creator Asset Pack (seamless loops + 3D thumbnails): {links['pack15']}\n"
        f"- Join the $15/mo Sovereign 4D Member Vault (30-min transmissions + 432Hz audio): {links['vault15']}\n"
        f"- Order your Custom Personalized 4D Aura Reading ($49): {links['aura49']}\n\n"
        "## 2. X / Twitter Post\n"
        "Most creators burn hours rendering motion backgrounds manually.\n\n"
        "We built a 4D Tesseract & Mobius visual engine outputting 104+ seamless loops and 3D assets on a single local GPU.\n\n"
        f"Download the commercial-use $15 Creator Asset Pack:\n{links['pack15']}\n\n"
        "## 3. TikTok / Instagram Reels Caption\n"
        f"Pause for 3 seconds and let the rotating 4D hypercube reset your focus on {theme_clean}.\n"
        "Comment 'ALIGN' if this hit your feed at the exact right moment.\n"
        f"Custom 4D Aura Reading ($49) & $15 Creator Pack -> {links['aura49']}\n"
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
    engine_label = "Verified High-Converting Template (skipped sub-2B loop model)"
    if model:
        print(f"[OLLAMA] Using '{model}' (RTX 2050 / $0 API cost) -> generating multi-platform copy...")
        prompt = (
            f"You are the marketing director for Oracle Systems LLC. Write crisp, ready-to-paste copy "
            f"promoting our 4D Tesseract & Mobius video '{vid['title']}' (Theme: {vid['theme']}).\n"
            f"Output EXACTLY these 4 markdown sections and include the EXACT URLs verbatim:\n"
            f"1. YouTube Pinned Comment (include {links['pack15']}, {links['vault15']}, and {links['aura49']})\n"
            f"2. X / Twitter Post (under 270 chars, link {links['pack15']})\n"
            f"3. TikTok / Reels Caption (5 hashtags, link {links['aura49']})\n"
            f"4. LinkedIn B2B Post (pitch agencies on local AI + autonomous media stacks, link {links['pronode']})\n"
            f"Do not repeat lines. No placeholders."
        )
        try:
            cand = ollama_generate(model, prompt)
            if is_valid_copy(cand, links):
                body = cand
                engine_label = f"Local Ollama ({model} - URL & Loop Verified)"
            else:
                print(f"[GUARD] '{model}' dropped URLs or looped -> switching to verified high-converting template.")
        except Exception as ex:
            print(f"[WARN] Ollama note: {ex} -> using verified template.")

    if not body:
        body = build_verified_pack(vid, links)

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
    print(f"\n[PASS] Generated Verified Traffic Pack -> {out_md}\n")
    print(full_md)


if __name__ == "__main__":
    main()