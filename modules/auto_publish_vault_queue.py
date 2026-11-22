import argparse
import json
import os
import re
import sys
import time

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
sys.path.insert(0, os.path.join(PDIR, "Modules"))

import publish_real_4d5d_youtube as pubmod

VAULT_STATE = os.path.join(PDIR, "data", "ultra_4d5d_vault_progress.json")
FULL_DIR = os.path.join(PDIR, "Content_Vault_4D_Full")
SHORTS_DIR = os.path.join(PDIR, "Content_Vault_4D_Shorts")


def clean_topic(fname):
    base = re.sub(r"(?i)^(week|short)_\d+_", "", fname)
    base = re.sub(r"(?i)(_4d_max|_real_full)?\.mp4$", "", base)
    return base.replace("_", " ").strip() or "Quantum Alignment"


def latest_live_full_url(st, pub_url):
    uploaded = st.get("uploaded_files") or {}
    for k in reversed(list(uploaded.keys())):
        if k.lower().startswith("week_"):
            return f"https://youtu.be/{uploaded[k]}"
    return f"{pub_url}/store"


def run_auto_publish(mode="short", max_uploads=1):
    if not os.path.exists(pubmod.TOK_P):
        print("[AUTO-YT] Missing config\\youtube_token.json")
        return

    vault = json.load(open(VAULT_STATE, "r", encoding="utf-8")) if os.path.exists(VAULT_STATE) else {}
    st = pubmod.load_state()
    uploaded = st.setdefault("uploaded_files", {})
    pub_url = pubmod.get_pub_url()

    p36_path = os.path.join(PDIR, "data", "living_shorts_rendered.json")
    p36_shorts = json.load(open(p36_path, "r", encoding="utf-8")) if os.path.exists(p36_path) else []

    if mode == "full":
        candidates = list(vault.get("full_done") or [])
        base_dir = FULL_DIR
    else:
        seen = set()
        candidates = []
        for s in list(vault.get("shorts_done") or []) + list(p36_shorts):
            if s not in seen:
                seen.add(s)
                candidates.append(s)
        base_dir = SHORTS_DIR

    pending = [f for f in candidates if f not in uploaded and os.path.exists(os.path.join(base_dir, f))]
    if not pending:
        print(f"[AUTO-YT] No new rendered Ultra-HD {mode}s waiting to publish (already uploaded: {len(uploaded)}).")
        return

    token = pubmod.get_fresh_access_token()
    flagship_url = latest_live_full_url(st, pub_url)
    count = 0

    for fname in pending[:max_uploads]:
        fpath = os.path.join(base_dir, fname)
        topic = clean_topic(fname)
        kw = [w.lower() for w in re.findall(r"[A-Za-z0-9]+", fname) if len(w) >= 3][:3]

        if mode == "full":
            title = f"{topic} | Full 10-Min 4D Tesseract & 5D Mobius Tarot Reading"
            wk_m = re.match(r"(Week_\d+)", fname, re.I)
            chaps = pubmod.load_chapters_for(wk_m.group(1) if wk_m else "Week_01")
            desc = (
                f"{title}\n"
                "Full-length 1080p/30fps living 4D Tesseract and 5D Mobius ray-traced tarot reading with warm studio narration.\n\n"
                f"CHAPTERS:\n{chaps}\n\n"
                f"-- LIVE INTERACTIVE 4D/5D TAROT PORTAL:\n{pub_url}/store\n\n"
                f"-- $49 CUSTOM PERSONALIZED 5D AURA READING:\n{pub_url}/go/auravideo49?utm_source=yt_auto_full&utm_medium=desc&utm_campaign={fname}\n\n"
                f"-- $15 4D/5D CREATOR ASSET PACK:\n{pub_url}/go/assetpack15?utm_source=yt_auto_full&utm_medium=desc&utm_campaign={fname}\n\n"
                f"-- $15/MO SOVEREIGN 5D MEMBER VAULT:\n{pub_url}/go/vaultsub15?utm_source=yt_auto_full&utm_medium=desc&utm_campaign={fname}\n\n"
                "Comment I CLAIM THIS 5D SHIFT below.\n"
                "#TarotReading #TimelessTarot #4DTesseract #5DMobius #OracleSystems"
            )
            tags = ["tarot reading", "timeless tarot", "4D tesseract", "5D mobius", "Oracle Systems", topic.lower()]
            up_path = pubmod.prepare_dsl_upload_file(fpath, max_mb=140.0)
        else:
            title = f"{topic} | Live 4D Tesseract & 5D Mobius Tarot #Shorts"
            desc = (
                f"WATCH THE FULL 10-MINUTE 4D/5D READING HERE:\n{flagship_url}\n\n"
                f"-- LIVE 4D TESSERACT & 5D MOBIUS TAROT PORTAL:\n{pub_url}/store\n\n"
                f"-- $49 CUSTOM PERSONALIZED 5D AURA READING:\n{pub_url}/go/auravideo49?utm_source=yt_auto_short&utm_medium=desc&utm_campaign={fname}\n\n"
                f"-- $15 4D/5D CREATOR ASSET PACK:\n{pub_url}/go/assetpack15?utm_source=yt_auto_short&utm_medium=desc&utm_campaign={fname}\n\n"
                "Comment I CLAIM THIS ALIGNMENT below.\n"
                "#Shorts #TarotShorts #4DTesseract #5DMobius #OracleSystems"
            )
            tags = ["Shorts", "TarotShorts", "4D tesseract", "5D mobius", "Oracle Systems", topic.lower()]
            up_path = fpath

        print(f"[AUTO-YT] Uploading {mode.upper()}: {fname} ({os.path.getsize(up_path)/(1024**2):.1f} MB)...")
        vid = pubmod.upload_video_requests_resumable(token, up_path, title, desc, tags)
        uploaded[fname] = vid
        pubmod.save_state(st)
        print(f"  [LIVE] https://youtu.be/{vid}")

        if mode == "full":
            time.sleep(2)
            ok, note = pubmod.set_custom_thumbnail_http(token, vid, kw)
            print(f"  [THUMB {'PASS' if ok else 'NOTE'}] {note}")
        count += 1

    print(f"[AUTO-YT COMPLETE] Published {count} new Ultra-HD {mode}(s) cleanly via pure HTTP 308 resumable engine.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["short", "full"], default="short")
    ap.add_argument("--count", type=int, default=1)
    args = ap.parse_args()
    run_auto_publish(mode=args.mode, max_uploads=args.count)
