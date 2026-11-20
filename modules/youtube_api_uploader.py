import base64
import csv
import datetime as dt
import json
import os
import subprocess
import sys

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]
DAILY_UPLOAD_CAP = 3  # ~4,800 API units max (safely under 10,000/day YouTube quota)


def ensure_google_libs():
    try:
        import googleapiclient  # noqa
        import google_auth_oauthlib  # noqa
        return True
    except ImportError:
        print("[INSTALL] Installing google-api-python-client & google-auth-oauthlib...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--quiet",
            "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2"
        ])
        return True


def get_youtube_service(secret_path, token_path):
    ensure_google_libs()
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def load_public_url(pdir):
    for p in (os.path.join(pdir, "config", "public_url.txt"), os.path.join(pdir, ".env")):
        if not os.path.exists(p):
            continue
        if p.endswith(".txt"):
            u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
            if u.startswith("http"):
                return u
        else:
            for ln in open(p, "r", encoding="utf-8"):
                t = ln.strip()
                if t.startswith("PUBLIC_BASE_URL="):
                    return t.split("=", 1)[1].strip().strip('"').strip("'").rstrip("/")
    return ""


def inject_utm(desc, base_url, kind, slug):
    if not base_url or ("127.0.0.1" in base_url) or ("localhost" in base_url):
        return desc
    med = kind.lower()
    desc = desc.replace("https://buy.stripe.com/6oU28rb29evn8di7UxcQU00", f"{base_url}/go/auravideo49?utm_source=youtube&utm_medium={med}&utm_campaign={slug}")
    desc = desc.replace("https://buy.stripe.com/bJefZheeldrj1OU8YBcQU01", f"{base_url}/go/tier29?utm_source=youtube&utm_medium={med}&utm_campaign={slug}")
    desc = desc.replace("https://buy.stripe.com/28E9AT6LT0Ex79e7UxcQU03", f"{base_url}/go/fullstorefront?utm_source=youtube&utm_medium={med}&utm_campaign={slug}")
    return desc


def check_quota(quota_path):
    today = dt.date.today().isoformat()
    q = {"date": today, "uploads_today": 0}
    if os.path.exists(quota_path):
        try:
            loaded = json.load(open(quota_path, "r", encoding="utf-8"))
            if loaded.get("date") == today:
                q = loaded
        except Exception:
            pass
    return q


def main():
    pdir = sys.argv[1]
    cfg = json.loads(base64.b64decode(sys.argv[2]).decode("utf-8"))

    qpath  = os.path.join(pdir, "reports", "learning_curve_ranked_queue.json")
    spath  = os.path.join(pdir, "data", "youtube_publish_state.json")
    hcsv   = os.path.join(pdir, "reports", "youtube_upload_history.csv")
    quota_p = os.path.join(pdir, "logs", "youtube_quota_state.json")
    secret = os.path.join(pdir, "config", "youtube_client_secret.json")
    token  = os.path.join(pdir, "config", "youtube_token.json")

    if not os.path.exists(qpath):
        print("[ERROR] Ranked queue missing. Run run_learning_curve.ps1 first.")
        sys.exit(1)

    qdata = json.load(open(qpath, "r", encoding="utf-8"))
    target_type = cfg.get("upload_type", "Short")
    privacy     = cfg.get("privacy", "public")
    max_up      = int(cfg.get("max_uploads", 1))
    dry_run     = bool(cfg.get("dry_run", True))

    quota = check_quota(quota_p)
    remaining_cap = max(0, DAILY_UPLOAD_CAP - int(quota.get("uploads_today", 0)))
    if (not dry_run) and remaining_cap <= 0:
        print(f"[QUOTA GUARD] Daily upload cap ({DAILY_UPLOAD_CAP}/day) reached for {quota['date']}. Skipping to protect YouTube API quota.")
        return

    effective_max = min(max_up, remaining_cap) if (not dry_run) else max_up
    candidates = []
    if target_type in ("Short", "Both") and qdata.get("shorts_queue"):
        candidates.extend(qdata["shorts_queue"][:effective_max])
    if target_type in ("FullVideo", "Both") and qdata.get("full_queue"):
        candidates.extend(qdata["full_queue"][:effective_max])
    candidates = candidates[:effective_max]

    if not candidates:
        print("[INFO] No unpublished 4D videos remaining in the selected queue.")
        return

    pub_url = load_public_url(pdir)
    print(f"=== YOUTUBE DATA API v3 4D AUTO-UPLOADER ({'DRY-RUN' if dry_run else 'LIVE UPLOAD'}) ===")
    print(f"Queue: {len(candidates)} video(s) | Privacy: {privacy} | Quota Used Today: {quota['uploads_today']}/{DAILY_UPLOAD_CAP} | UTM Base: {pub_url or 'Direct Stripe'}")

    for item in candidates:
        vp = item["upgraded_4d_mp4"]
        tp = item["thumb_3d_jpg"]
        sz = (os.path.getsize(vp) / (1024 ** 2)) if os.path.exists(vp) else 0.0
        print(f"  -> [{item['type']} #{item['sequence']}] {os.path.basename(vp)} ({sz:.1f} MB) | Theme: {item.get('theme')}")
        print(f"     Title: {item['ab_recommended_title'][:98]}")
        print(f"     Thumb: {os.path.basename(tp)} (Ready: {os.path.exists(tp)})")

    if dry_run:
        if not os.path.exists(secret):
            print("\n[ONE-TIME OAUTH SETUP TO ACTIVATE AUTO-UPLOADS]")
            print("  1. Google Cloud Console -> APIs & Services -> Library -> enable 'YouTube Data API v3'.")
            print("  2. Credentials -> Desktop app OAuth Client -> Download JSON.")
            print(f"  3. Save JSON as: {secret}")
            print("  4. Run: .\\upload_youtube_4d.ps1 -UploadType Short -Privacy unlisted -UploadNow")
        else:
            print(f"\n[READY] OAuth secret found at {secret}. Pass -UploadNow to upload live!")
        return

    if not os.path.exists(secret):
        print(f"[ACTION NEEDED] Missing {secret}. Scheduled upload skipped safely until OAuth JSON is saved.")
        sys.exit(3)

    youtube = get_youtube_service(secret, token)
    from googleapiclient.http import MediaFileUpload

    state = {"published_full": [], "published_shorts": [], "uploaded_ids": {}, "last_updated": ""}
    if os.path.exists(spath):
        try:
            state.update(json.load(open(spath, "r", encoding="utf-8")))
        except Exception:
            pass

    new_hist = []
    for item in candidates:
        vp = item["upgraded_4d_mp4"]
        tp = item["thumb_3d_jpg"]
        if not os.path.exists(vp):
            print(f"[SKIP] Video file missing: {vp}")
            continue

        title = item["ab_recommended_title"][:98]
        desc  = inject_utm(item["description"], pub_url, item["type"], item["slug"])[:4900]
        tags  = ["4D Tesseract", "Mobius Strip", "Quantum Portal", "Oracle Systems", item["topic"], "Tarot Reading", "Shorts"]
        body = {
            "snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "22"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        }

        print(f"\n[UPLOADING] {os.path.basename(vp)} ({privacy})...")
        media = MediaFileUpload(vp, chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
        req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status:
                print(f"  Progress: {int(status.progress() * 100)}%")

        vid_id = resp["id"]
        vid_url = f"https://youtu.be/{vid_id}"
        print(f"[PASS] Live on YouTube -> {vid_url}")

        if os.path.exists(tp):
            try:
                youtube.thumbnails().set(videoId=vid_id, media_body=MediaFileUpload(tp, mimetype="image/jpeg")).execute()
                print(f"[PASS] Applied 3D JPEG thumbnail -> {os.path.basename(tp)}")
            except Exception as te:
                print(f"[WARN] Thumbnail set skipped: {te}")

        klist = "published_shorts" if item["type"] == "Short" else "published_full"
        fmark = item["slug"] + ".mp4"
        if fmark not in state[klist]:
            state[klist].append(fmark)
        now_z = dt.datetime.utcnow().isoformat() + "Z"
        state.setdefault("uploaded_ids", {})[item["slug"]] = {
            "video_id": vid_id, "url": vid_url, "type": item["type"],
            "theme": item.get("theme", ""), "ab_variant": item.get("ab_variant", ""),
            "privacy": privacy, "uploaded_utc": now_z,
        }
        state["last_updated"] = now_z
        quota["uploads_today"] = int(quota.get("uploads_today", 0)) + 1
        new_hist.append([now_z, item["type"], item["sequence"], item["slug"], vid_id, vid_url, privacy, item.get("ab_variant", "")])

    json.dump(state, open(spath, "w", encoding="utf-8"), indent=2)
    json.dump(quota, open(quota_p, "w", encoding="utf-8"), indent=2)
    write_hdr = not os.path.exists(hcsv)
    with open(hcsv, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if write_hdr:
            w.writerow(["uploaded_utc", "type", "sequence", "slug", "video_id", "url", "privacy", "ab_variant"])
        w.writerows(new_hist)
    print(f"\n[COMPLETE] Logged {len(new_hist)} upload(s) | Quota today: {quota['uploads_today']}/{DAILY_UPLOAD_CAP}")


if __name__ == "__main__":
    main()