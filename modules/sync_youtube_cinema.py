import os

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
TOK_P = os.path.join(PDIR, "config", "youtube_token.json")
PUB_P = os.path.join(PDIR, "config", "public_url.txt")

def main():
    if not os.path.exists(TOK_P):
        print("[PHASE 27] Skipped: youtube_token.json not found.")
        return
    pub = open(PUB_P, "r", encoding="utf-8").read().strip().rstrip("/") if os.path.exists(PUB_P) else "http://127.0.0.1:8000"
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(TOK_P)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds)

        ch = yt.channels().list(part="contentDetails", mine=True).execute()
        items = ch.get("items") or []
        if not items:
            return
        pl_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        vids = yt.playlistItems().list(part="snippet", playlistId=pl_id, maxResults=15).execute().get("items") or []

        updated = 0
        for it in vids:
            vid = it["snippet"]["resourceId"]["videoId"]
            vinfo = (yt.videos().list(part="snippet", id=vid).execute().get("items") or [])
            if not vinfo:
                continue
            snip = vinfo[0]["snippet"]
            snip["description"] = (
                "ORACLE SYSTEMS LLC // LIVE 3D RAY-LIT TAROT PORTAL\n"
                "Step into the live interactive 3D Tarot Portal, draw your own spread with studio neural narration, and unlock instant Stripe-verified delivery:\n\n"
                f"-> LIVE 3D TAROT PORTAL & STOREFRONT:\n{pub}/store\n\n"
                f"-> $15 CREATOR ASSET PACK (4D Loops + 3D Templates):\n{pub}/go/assetpack15?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                f"-> $15/MO SOVEREIGN MEMBER VAULT (Full Multi-Chapter Readings + 432Hz):\n{pub}/go/vaultsub15?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                f"-> $49 CUSTOM PERSONALIZED 4D AURA READING:\n{pub}/go/auravideo49?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                f"-> $1,500 TURNKEY CREATOR STACK & $49,999 PRO_NODE:\n{pub}/go/fullstorefront?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                "Comment 'I CLAIM THIS ALIGNMENT' below to lock in the shift.\n"
                "#TarotReading #3DTarot #OracleSystems #QuantumAlignment #Shorts"
            )
            yt.videos().update(part="snippet", body={"id": vid, "snippet": snip}).execute()
            updated += 1
        print(f"[PHASE 27 PASS] Synced live YouTube descriptions across {updated} channel video(s) -> {pub}/store")
    except Exception as ex:
        print(f"[PHASE 27 WARN] YouTube description sync note: {ex}")


if __name__ == "__main__":
    main()