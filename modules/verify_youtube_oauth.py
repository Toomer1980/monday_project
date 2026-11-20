import json
import os
import sys

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]


def main():
    pdir = sys.argv[1]
    do_live = (len(sys.argv) > 2 and sys.argv[2] == "LIVE")
    secret = os.path.join(pdir, "config", "youtube_client_secret.json")
    token  = os.path.join(pdir, "config", "youtube_token.json")

    if not os.path.exists(secret):
        print(f"[MISSING] {secret} not found.")
        print("  -> Download Desktop app OAuth JSON from Google Cloud Console and save it there")
        print("  -> OR re-run with: .\\verify_google_oauth.ps1 -AutoImportFromDownloads")
        sys.exit(2)

    try:
        raw = json.load(open(secret, "r", encoding="utf-8"))
    except Exception as ex:
        print(f"[FAIL] Invalid JSON in {secret}: {ex}")
        sys.exit(1)

    if "web" in raw and "installed" not in raw:
        print("[FAIL] Wrong Google OAuth client type: JSON contains 'web' instead of 'installed' (Desktop app).")
        print("  -> In Google Cloud Console -> Clients -> Create Client -> choose 'Desktop app' and re-download.")
        sys.exit(1)

    inst = raw.get("installed")
    if not isinstance(inst, dict):
        print("[FAIL] Missing top-level 'installed' object in youtube_client_secret.json.")
        sys.exit(1)

    cid = (inst.get("client_id") or "").strip()
    csec = (inst.get("client_secret") or "").strip()
    proj = (inst.get("project_id") or "unknown").strip()
    redirs = inst.get("redirect_uris") or []

    cid_ok = cid.endswith(".apps.googleusercontent.com")
    sec_ok = len(csec) >= 10
    print(f"[JSON PASS] Project: {proj} | Client ID Format OK: {cid_ok} | Secret Present: {sec_ok} | Redirects: {len(redirs)}")
    if not (cid_ok and sec_ok):
        print("[FAIL] Client ID or Client Secret appears incomplete inside JSON.")
        sys.exit(1)

    if not do_live:
        print(f"[INFO] Token cached: {os.path.exists(token)} (Re-run with -TestLiveYouTube to verify live YouTube channel API)")
        return

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        import subprocess
        print("[INSTALL] Installing Google YouTube API client libraries...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2"])
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

    creds = None
    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secret, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    yt = build("youtube", "v3", credentials=creds)
    ch = yt.channels().list(part="snippet,statistics", mine=True).execute()
    items = ch.get("items") or []
    if not items:
        print("[WARN] OAuth succeeded, but no YouTube channel was found on this Google account.")
        return
    sn = items[0].get("snippet", {})
    st = items[0].get("statistics", {})
    print(f"[LIVE PASS] Connected YouTube Channel: '{sn.get('title')}' | Subscribers: {st.get('subscriberCount', '0')} | Videos: {st.get('videoCount', '0')}")


if __name__ == "__main__":
    main()