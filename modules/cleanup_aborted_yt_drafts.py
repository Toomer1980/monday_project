import json
import os
import requests

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
TOK_P = os.path.join(PDIR, "config", "youtube_token.json")
STATE_P = os.path.join(PDIR, "data", "youtube_ultra_4d5d_uploads.json")


def get_token():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(TOK_P)
    if not creds.valid or creds.expired or not creds.token:
        creds.refresh(Request())
    return creds.token


def main():
    if not os.path.exists(TOK_P):
        print("[YT-CLEAN] Missing config\\youtube_token.json")
        return

    token = get_token()
    hdrs = {"Authorization": f"Bearer {token}"}
    st = json.load(open(STATE_P, "r", encoding="utf-8")) if os.path.exists(STATE_P) else {}
    protected_ids = set((st.get("uploaded_files") or {}).values()) | {
        "koFpuMKuN8Y", "rYqNeXOpAWw", "fup8wv10BUY", "pmvlbk78ioc"
    }

    ch = requests.get("https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true", headers=hdrs, timeout=20).json()
    items = ch.get("items") or []
    if not items:
        print("[YT-CLEAN] No channel found.")
        return

    pl_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={pl_id}&maxResults=40", headers=hdrs, timeout=20).json()
    vids = [it["snippet"]["resourceId"]["videoId"] for it in (pl.get("items") or [])]
    if not vids:
        print("[YT-CLEAN] No uploads found.")
        return

    det = requests.get(
        f"https://www.googleapis.com/youtube/v3/videos?part=snippet,status,statistics,contentDetails&id={','.join(vids)}",
        headers=hdrs, timeout=20,
    ).json()

    deleted = 0
    for v in det.get("items") or []:
        vid = v["id"]
        if vid in protected_ids:
            continue
        up_status = (v.get("status") or {}).get("uploadStatus", "")
        views = int((v.get("statistics") or {}).get("viewCount", 0))
        dur = (v.get("contentDetails") or {}).get("duration", "")
        title = (v.get("snippet") or {}).get("title", "")
        # Only delete aborted/failed/unprocessed 0-view shells ("Processing will begin shortly")
        is_aborted_shell = (up_status in ("failed", "rejected", "deleted", "uploaded")) and (views == 0) and (dur in ("", "P0D", "PT0S"))
        if is_aborted_shell:
            r = requests.delete(f"https://www.googleapis.com/youtube/v3/videos?id={vid}", headers=hdrs, timeout=20)
            if r.status_code in (200, 204):
                deleted += 1
                print(f"  [DELETED ABORTED SHELL] {vid} (status={up_status}) -> {title[:55]}")
            else:
                print(f"  [DELETE NOTE] {vid}: HTTP {r.status_code} {r.text[:100]}")

    print(f"[YT-CLEAN PASS] Removed {deleted} aborted 'Processing will begin shortly' draft shell(s). Protected live IDs untouched.")


if __name__ == "__main__":
    main()
