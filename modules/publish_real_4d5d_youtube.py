import argparse
import glob
import io
import json
import os
import re
import time
from PIL import Image

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
TOK_P = os.path.join(PDIR, "config", "youtube_token.json")
PUB_P = os.path.join(PDIR, "config", "public_url.txt")
FULL_DIR = os.path.join(PDIR, "Content_Vault_4D_Full")
SHORTS_DIR = os.path.join(PDIR, "Content_Vault_4D_Shorts")
THUMB_DIR = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")
CH_MD = os.path.join(PDIR, "reports", "YouTube_Chapter_Timestamps.md")
STATE_P = os.path.join(PDIR, "data", "youtube_ultra_4d5d_uploads.json")
REP_OUT = os.path.join(PDIR, "reports", "YouTube_Live_Publish_Report.md")


def load_state():
    if os.path.exists(STATE_P):
        try:
            return json.load(open(STATE_P, "r", encoding="utf-8"))
        except Exception:
            pass
    return {"uploaded_files": {}, "unlisted_old_ids": []}


def save_state(st):
    os.makedirs(os.path.dirname(STATE_P), exist_ok=True)
    json.dump(st, open(STATE_P, "w", encoding="utf-8"), indent=2)


def get_pub_url():
    if os.path.exists(PUB_P):
        u = open(PUB_P, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "https://oraclesystemsllc.com"


def load_chapters_for(slug_hint):
    if os.path.exists(CH_MD):
        txt = open(CH_MD, "r", encoding="utf-8").read()
        blocks = re.split(r"(?m)^##\s+", txt)
        for blk in blocks[1:]:
            lines = blk.strip().splitlines()
            if lines and slug_hint.lower() in lines[0].lower():
                ts = [ln.strip() for ln in lines[1:] if re.match(r"^\d{2}:\d{2}\s+", ln.strip())]
                if ts:
                    return "\n".join(ts[:7])
    return (
        "00:00 Opening 4D Tesseract Portal & Collective Shift\n"
        "01:40 Card 1 - Past Catalyst\n"
        "03:07 Card 2 - Present Mobius Turning Point\n"
        "04:22 Card 3 - 5D Guiding Signal\n"
        "05:52 Card 4 - Radiant Breakthrough\n"
        "07:19 Card 5 - Sovereign Mastery\n"
        "08:42 Complete 5-Card 4D/5D Integration"
    )


def build_thumb_bytes(match_keywords):
    thumbs = sorted(glob.glob(os.path.join(THUMB_DIR, "*.jpg")))
    if not thumbs:
        return None, ""
    chosen = thumbs[0]
    for tp in thumbs:
        bn = os.path.basename(tp).lower()
        if all(k.lower() in bn for k in match_keywords):
            chosen = tp
            break
    else:
        for tp in thumbs:
            bn = os.path.basename(tp).lower()
            if any(k.lower() in bn for k in match_keywords):
                chosen = tp
                break
    with Image.open(chosen) as im:
        im = im.convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=90, optimize=True)
        return buf.getvalue(), os.path.basename(chosen)


def set_custom_thumbnail(yt, video_id, match_keywords):
    from googleapiclient.http import MediaIoBaseUpload
    data, tname = build_thumb_bytes(match_keywords)
    if not data:
        return False, "No thumbnail file found"
    try:
        media = MediaIoBaseUpload(io.BytesIO(data), mimetype="image/jpeg", resumable=False)
        yt.thumbnails().set(videoId=video_id, media_body=media).execute()
        return True, f"Uploaded {tname} ({len(data)//1024} KB)"
    except Exception as ex:
        msg = str(ex)
        if "forbidden" in msg.lower() or "403" in msg or "thumbnail" in msg.lower():
            return False, "NEEDS_PHONE_VERIFY (verify once at https://www.youtube.com/verify to unlock custom API thumbnails)"
        return False, msg[:160]


def get_yt_client():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(TOK_P)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def cleanup_old_wireframe_uploads(yt, st, keep_ids):
    """Unlist legacy 0-5 view black-wireframe uploads so visitors ONLY see the new Ultra-HD 4D/5D ray-traced videos."""
    ch = yt.channels().list(part="contentDetails", mine=True).execute()
    items = ch.get("items") or []
    if not items:
        return 0
    pl_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl_items = yt.playlistItems().list(part="snippet", playlistId=pl_id, maxResults=35).execute().get("items") or []
    vids = [it["snippet"]["resourceId"]["videoId"] for it in pl_items]
    if not vids:
        return 0

    details = yt.videos().list(part="snippet,status,statistics", id=",".join(vids)).execute().get("items") or []
    unlisted_now = 0
    for v in details:
        vid = v["id"]
        if vid in keep_ids:
            continue
        views = int((v.get("statistics") or {}).get("viewCount", 0))
        priv = (v.get("status") or {}).get("privacyStatus", "")
        title = (v.get("snippet") or {}).get("title", "")
        # Unlist legacy 0-5 view wireframe clips (preserves the 3 older Shorts with 79-102 views!)
        if priv == "public" and views <= 5:
            try:
                yt.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": "unlisted"}}).execute()
                if vid not in st["unlisted_old_ids"]:
                    st["unlisted_old_ids"].append(vid)
                unlisted_now += 1
                print(f"  [CLEANED OLD WIREFRAME] Unlisted {vid} ({views} views) -> {title[:55]}")
            except Exception as ex:
                print(f"  [CLEANUP NOTE] Could not unlist {vid}: {str(ex)[:110]}")
    save_state(st)
    return unlisted_now


def upload_video(yt, file_path, title, description, tags):
    from googleapiclient.http import MediaFileUpload
    body = {
        "snippet": {
            "title": title[:98],
            "description": description[:4900],
            "tags": tags,
            "categoryId": "24",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(file_path, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"    -> Uploading {os.path.basename(file_path)}: {int(status.progress() * 100)}%", flush=True)
    return resp["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thumbs-only", action="store_true", help="Retry pushing custom thumbnails onto already uploaded Ultra-HD full videos")
    ap.add_argument("--skip-cleanup", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(TOK_P):
        print("[ERROR] config\\youtube_token.json not found!")
        return

    yt = get_yt_client()
    st = load_state()
    pub = get_pub_url()

    # Exact Ultra-HD 4D/5D videos already rendered on disk (staying within 10,000 daily YouTube API quota units = max 4 uploads)
    release_queue = [
        {
            "key": "Week_01_Sudden_Breakthrough_4D_MAX.mp4",
            "path": os.path.join(FULL_DIR, "Week_01_Sudden_Breakthrough_4D_MAX.mp4"),
            "is_short": False,
            "title": "Sudden Breakthrough & Financial Shift | Full 10-Min 4D Tesseract & 5D Mobius Tarot Reading",
            "thumb_keys": ["week_01", "sudden_breakthrough"],
            "chapter_hint": "Week_01",
            "tags": ["tarot reading", "timeless tarot", "4D tesseract", "5D mobius", "financial breakthrough", "Oracle Systems", "collective tarot"],
        },
        {
            "key": "Week_02_Silent_Abundance_Financial_Breakthrough_REAL_FULL.mp4",
            "path": os.path.join(FULL_DIR, "Week_02_Silent_Abundance_Financial_Breakthrough_REAL_FULL.mp4"),
            "is_short": False,
            "title": "Silent Abundance & Financial Breakthrough | Full 4D/5D Living Tarot Reading (Timeless)",
            "thumb_keys": ["week_02", "silent_abundance"],
            "chapter_hint": "Week_02",
            "tags": ["tarot reading", "silent abundance", "financial breakthrough", "4D tesseract", "5D mobius", "Oracle Systems", "timeless tarot"],
        },
        {
            "key": "Short_01_Sudden_Breakthrough_4D_MAX.mp4",
            "path": os.path.join(SHORTS_DIR, "Short_01_Sudden_Breakthrough_4D_MAX.mp4"),
            "is_short": True,
            "title": "Sudden Breakthrough Unlocked | Live 4D Tesseract & 5D Mobius Tarot #Shorts",
            "thumb_keys": ["short_01", "sudden_breakthrough"],
            "chapter_hint": "",
            "tags": ["Shorts", "TarotShorts", "4D tesseract", "5D mobius", "tarot reading", "Oracle Systems"],
        },
        {
            "key": "Short_13_Abundance_Magnet_4D_MAX.mp4",
            "path": os.path.join(SHORTS_DIR, "Short_13_Abundance_Magnet_4D_MAX.mp4"),
            "is_short": True,
            "title": "Abundance Magnet Activated | Living 3D Ray-Traced Tarot Reading #Shorts",
            "thumb_keys": ["short_13", "abundance_magnet"],
            "chapter_hint": "",
            "tags": ["Shorts", "TarotShorts", "abundance tarot", "4D tesseract", "Oracle Systems"],
        },
    ]

    if args.thumbs_only:
        print("[THUMBS-ONLY] Retrying custom 2K->1080p thumbnails on uploaded Full Episodes...")
        for item in release_queue:
            if not item["is_short"] and item["key"] in st["uploaded_files"]:
                vid = st["uploaded_files"][item["key"]]
                ok, note = set_custom_thumbnail(yt, vid, item["thumb_keys"])
                print(f"  [{'PASS' if ok else 'NOTE'}] https://youtu.be/{vid} -> {note}")
        return

    lines = ["# Oracle Systems LLC - Live Ultra-HD 4D/5D YouTube Publish Report", ""]
    flagship_url = f"{pub}/store"
    uploaded_now = []
    needs_verify = False

    # 1. Upload Full 16:9 Episodes first so Shorts can link straight to the brand-new 10-minute 4D/5D episode!
    for item in release_queue:
        if not os.path.exists(item["path"]):
            print(f"[SKIP] Missing local render: {item['path']}")
            continue

        if item["key"] in st["uploaded_files"]:
            vid = st["uploaded_files"][item["key"]]
            print(f"[ALREADY LIVE] {item['key']} -> https://youtu.be/{vid}")
            if not item["is_short"] and flagship_url == f"{pub}/store":
                flagship_url = f"https://youtu.be/{vid}"
            continue

        if item["is_short"]:
            desc = (
                f"WATCH THE FULL 10-MINUTE 1080p 4D TESSERACT & 5D MOBIUS READING:\n{flagship_url}\n\n"
                f"-- LIVE INTERACTIVE 4D TESSERACT & 5D MOBIUS TAROT PORTAL:\n{pub}/store\n\n"
                f"-- ORDER YOUR CUSTOM PERSONALIZED 5D AURA READING ($49):\n{pub}/go/auravideo49?utm_source=yt_ultra_short&utm_medium=desc&utm_campaign={item['key']}\n\n"
                f"-- $15 4D/5D CREATOR ASSET PACK (Tesseract + Mobius Loops & 2K Templates):\n{pub}/go/assetpack15?utm_source=yt_ultra_short&utm_medium=desc&utm_campaign={item['key']}\n\n"
                f"-- $15/MO SOVEREIGN 5D MEMBER VAULT:\n{pub}/go/vaultsub15?utm_source=yt_ultra_short&utm_medium=desc&utm_campaign={item['key']}\n\n"
                "Comment I CLAIM THIS 5D SHIFT below.\n"
                "#Shorts #TarotReading #4DTesseract #5DMobius #OracleSystems"
            )
        else:
            chaps = load_chapters_for(item["chapter_hint"])
            desc = (
                f"{item['title']}\n"
                "Full-length 1080p/30fps living 4D Tesseract and 5D Mobius ray-traced tarot reading with warm Irish studio narration.\n\n"
                "CHAPTERS:\n"
                f"{chaps}\n\n"
                f"-- STEP INTO THE LIVE 4D TESSERACT & 5D MOBIUS TAROT PORTAL:\n{pub}/store\n\n"
                f"-- ORDER YOUR CUSTOM PERSONALIZED 5D AURA READING ($49):\n{pub}/go/auravideo49?utm_source=yt_ultra_full&utm_medium=desc&utm_campaign={item['key']}\n\n"
                f"-- $15 4D/5D CREATOR ASSET PACK (Loops + 2K QHD Templates):\n{pub}/go/assetpack15?utm_source=yt_ultra_full&utm_medium=desc&utm_campaign={item['key']}\n\n"
                f"-- $15/MO SOVEREIGN 5D MEMBER VAULT:\n{pub}/go/vaultsub15?utm_source=yt_ultra_full&utm_medium=desc&utm_campaign={item['key']}\n\n"
                f"-- $1,500 TURNKEY 4D/5D CREATOR STACK & $49,999 PRO_NODE:\n{pub}/go/fullstorefront?utm_source=yt_ultra_full&utm_medium=desc&utm_campaign={item['key']}\n\n"
                "Comment I CLAIM THIS 5D ALIGNMENT below.\n"
                "#TarotReading #TimelessTarot #4DTesseract #5DMobius #OracleSystems #Abundance"
            )

        print(f"\n>>> [UPLOADING REAL ULTRA-HD 4D/5D VIDEO] {item['key']} ({os.path.getsize(item['path'])/(1024**2):.1f} MB)...")
        try:
            vid = upload_video(yt, item["path"], item["title"], desc, item["tags"])
            st["uploaded_files"][item["key"]] = vid
            save_state(st)
            url = f"https://youtu.be/{vid}"
            uploaded_now.append((item["key"], url, item["is_short"]))
            if not item["is_short"] and flagship_url == f"{pub}/store":
                flagship_url = url
            print(f"  [LIVE ON YOUTUBE] {url}")

            thumb_note = "Short auto-frame (real 4D/5D ray-traced card)"
            if not item["is_short"]:
                time.sleep(2)
                ok_t, thumb_note = set_custom_thumbnail(yt, vid, item["thumb_keys"])
                if "NEEDS_PHONE_VERIFY" in thumb_note:
                    needs_verify = True
                print(f"  [THUMBNAIL {'PASS' if ok_t else 'ACTION NEEDED'}] {thumb_note}")

            lines.append(f"- **LIVE `{item['key']}`** -> {url} | Thumbnail: {thumb_note}")
        except Exception as ex:
            print(f"  [UPLOAD ERROR] {item['key']}: {str(ex)[:220]}")
            lines.append(f"- **FAILED `{item['key']}`**: {str(ex)[:220]}")

    # 2. Clean up old 0-5 view black-wireframe uploads so channel page ONLY showcases the new Ultra-HD 4D/5D videos!
    keep_ids = set(st["uploaded_files"].values())
    unlisted_cnt = 0
    if not args.skip_cleanup:
        print("\n>>> [CHANNEL CLEANUP] Unlisting old 0-5 view black wireframe uploads...")
        unlisted_cnt = cleanup_old_wireframe_uploads(yt, st, keep_ids)

    lines.append(f"\n- **Newly Published Ultra-HD 4D/5D Videos:** {len(uploaded_now)}")
    lines.append(f"- **Old Black-Wireframe Videos Unlisted:** {unlisted_cnt}")
    if needs_verify:
        lines.append("- **ACTION FOR CUSTOM LONG-FORM THUMBNAILS:** Complete 15-second phone verification at https://www.youtube.com/verify then run `python .\\Modules\\publish_real_4d5d_youtube.py --thumbs-only`")

    open(REP_OUT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print(f"\n[PUBLISH COMPLETE] Live Ultra-HD uploads: {len(uploaded_now)} | Old wireframes unlisted: {unlisted_cnt} | Report: {REP_OUT}")
    if needs_verify:
        print("[THUMBNAIL ACTION] Verify your YouTube account once at https://www.youtube.com/verify then run:")
        print("  python .\\Modules\\publish_real_4d5d_youtube.py --thumbs-only")


if __name__ == "__main__":
    main()
