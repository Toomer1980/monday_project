import csv
import datetime as dt
import json
import os
import shutil
import subprocess
import sys

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def ensure_libs():
    try:
        import googleapiclient  # noqa
        import google_auth_oauthlib  # noqa
    except ImportError:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--quiet",
            "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2"
        ])


def get_service(secret_path, token_path):
    ensure_libs()
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


def main():
    pdir = sys.argv[1]
    spath  = os.path.join(pdir, "data", "youtube_publish_state.json")
    apath  = os.path.join(pdir, "data", "youtube_analytics.json")
    acsv   = os.path.join(pdir, "reports", "youtube_analytics_snapshot.csv")
    sdir   = os.path.join(pdir, "Oracle_Audit_2026")
    secret = os.path.join(pdir, "config", "youtube_client_secret.json")
    token  = os.path.join(pdir, "config", "youtube_token.json")
    os.makedirs(sdir, exist_ok=True)

    if not os.path.exists(secret) and not os.path.exists(token):
        print("[INFO] YouTube OAuth not configured yet (save Google Cloud Desktop JSON to config\\youtube_client_secret.json to pull live views).")
        snap = {"polled_utc": dt.datetime.utcnow().isoformat() + "Z", "api_connected": False, "videos": {}, "totals": {"videos": 0, "views": 0, "likes": 0, "comments": 0}}
        json.dump(snap, open(apath, "w", encoding="utf-8"), indent=2)
        return

    youtube = get_service(secret, token)

    # Collect video IDs tracked in youtube_publish_state.json
    id_to_slug = {}
    if os.path.exists(spath):
        try:
            st = json.load(open(spath, "r", encoding="utf-8"))
            for slug, info in (st.get("uploaded_ids") or {}).items():
                vid = info.get("video_id")
                if vid:
                    id_to_slug[vid] = slug
        except Exception:
            pass

    # Also auto-discover the channel's recent uploads so manually uploaded videos count too
    try:
        ch = youtube.channels().list(part="contentDetails", mine=True).execute()
        if ch.get("items"):
            uploads_pl = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            pl_items = youtube.playlistItems().list(part="snippet", playlistId=uploads_pl, maxResults=50).execute()
            for it in pl_items.get("items", []):
                vid = it["snippet"]["resourceId"]["videoId"]
                if vid not in id_to_slug:
                    id_to_slug[vid] = it["snippet"].get("title", vid)
    except Exception as e:
        print(f"[WARN] Channel auto-discovery skipped: {e}")

    video_ids = list(id_to_slug.keys())
    if not video_ids:
        print("[INFO] Connected to YouTube API, but 0 uploaded videos found on channel yet.")
        snap = {"polled_utc": dt.datetime.utcnow().isoformat() + "Z", "api_connected": True, "videos": {}, "totals": {"videos": 0, "views": 0, "likes": 0, "comments": 0}}
        json.dump(snap, open(apath, "w", encoding="utf-8"), indent=2)
        return

    videos_out = {}
    tot_views = 0; tot_likes = 0; tot_comments = 0
    rows_csv = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        res = youtube.videos().list(part="snippet,statistics", id=",".join(batch)).execute()
        for item in res.get("items", []):
            vid = item["id"]
            st  = item.get("statistics", {})
            sn  = item.get("snippet", {})
            views = int(st.get("viewCount", 0))
            likes = int(st.get("likeCount", 0))
            comms = int(st.get("commentCount", 0))
            eng_score = round((views * 0.02) + (likes * 0.5) + (comms * 1.5), 3)
            slug = id_to_slug.get(vid, vid)
            videos_out[slug] = {
                "video_id": vid,
                "title": sn.get("title", ""),
                "published_at": sn.get("publishedAt", ""),
                "views": views,
                "likes": likes,
                "comments": comms,
                "engagement_score": eng_score,
            }
            tot_views += views; tot_likes += likes; tot_comments += comms
            rows_csv.append([vid, slug, sn.get("title", ""), views, likes, comms, eng_score])

    snap = {
        "polled_utc": dt.datetime.utcnow().isoformat() + "Z",
        "api_connected": True,
        "videos": videos_out,
        "totals": {"videos": len(videos_out), "views": tot_views, "likes": tot_likes, "comments": tot_comments},
    }
    json.dump(snap, open(apath, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    with open(acsv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["video_id", "slug_or_key", "title", "views", "likes", "comments", "engagement_score"])
        w.writerows(sorted(rows_csv, key=lambda r: -r[3]))
    shutil.copy2(acsv, os.path.join(sdir, os.path.basename(acsv)))

    print(f"[PASS] Pulled live YouTube Analytics -> {len(videos_out)} video(s) | Views: {tot_views:,} | Likes: {tot_likes:,} | Comments: {tot_comments:,}")


if __name__ == "__main__":
    main()