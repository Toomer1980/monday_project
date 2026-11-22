import glob
import io
import json
import os
import re
from PIL import Image

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
TOK_P = os.path.join(PDIR, "config", "youtube_token.json")
PUB_P = os.path.join(PDIR, "config", "public_url.txt")
THUMB_DIR = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")
CH_MD = os.path.join(PDIR, "reports", "YouTube_Chapter_Timestamps.md")
REP_OUT = os.path.join(PDIR, "reports", "YouTube_SEO_Upgrade_Report.md")


def parse_iso_dur_seconds(iso_str):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_str or "")
    if not m:
        return 0
    return int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)


def clean_seo_title(raw_title, is_short):
    t = re.sub(r"(?i)^(week|short)[_\s]*\d+[_\s]*", "", raw_title or "").strip()
    t = re.sub(r"(?i)[_\s]*(4d[_\s]*max|real[_\s]*full|4d|5d)$", "", t).strip()
    t = t.replace("_", " ").strip(" -|:/")
    if not t:
        t = "Silent Abundance & Financial Breakthrough"
    t = " ".join(w.capitalize() if w.islower() else w for w in t.split())
    if is_short:
        out = f"{t} | 4D Tesseract Tarot Shift #Shorts"
    else:
        out = f"{t} | Full 4D/5D Living Tarot Reading (Timeless)"
    return out[:96]


def pick_thumbnail_bytes(raw_title):
    thumbs = sorted(glob.glob(os.path.join(THUMB_DIR, "*.jpg")))
    if not thumbs:
        return None, ""
    words = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", raw_title or "") if w.lower() not in ("week", "short", "full", "reading", "tarot")]
    chosen = thumbs[0]
    for tp in thumbs:
        bn = os.path.basename(tp).lower()
        if any(w in bn for w in words):
            chosen = tp
            break
    # YouTube custom thumbnail API requires <= 2 MB; resize 1920x1080 JPEG q=90 (~400-800 KB, razor sharp)
    with Image.open(chosen) as im:
        im = im.convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=90, optimize=True)
        return buf.getvalue(), os.path.basename(chosen)


def load_sample_chapters():
    if os.path.exists(CH_MD):
        txt = open(CH_MD, "r", encoding="utf-8").read()
        ts_lines = [ln.strip() for ln in txt.splitlines() if re.match(r"^\d{2}:\d{2}\s+", ln.strip())]
        if ts_lines:
            return "\n".join(ts_lines[:7])
    return (
        "00:00 Opening 4D Tesseract Portal & Collective Energy\n"
        "01:30 Card 1 - Past Catalyst\n"
        "03:00 Card 2 - Present Mobius Turning Point\n"
        "04:30 Card 3 - 5D Guiding Light\n"
        "06:00 Card 4 - Radiant Breakthrough\n"
        "07:30 Card 5 - Sovereign Mastery\n"
        "09:00 Complete 5-Card Living Integration"
    )


def main():
    if not os.path.exists(TOK_P):
        print("[YT-SEO] youtube_token.json not found; skipping.")
        return

    pub = open(PUB_P, "r", encoding="utf-8").read().strip().rstrip("/") if os.path.exists(PUB_P) else "https://oraclesystemsllc.com"
    chapters_block = load_sample_chapters()

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload

    creds = Credentials.from_authorized_user_file(TOK_P)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    yt = build("youtube", "v3", credentials=creds)

    ch = yt.channels().list(part="contentDetails", mine=True).execute()
    items = ch.get("items") or []
    if not items:
        print("[YT-SEO] No YouTube channel found on token.")
        return

    pl_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl_items = yt.playlistItems().list(part="snippet", playlistId=pl_id, maxResults=30).execute().get("items") or []
    vid_ids = [it["snippet"]["resourceId"]["videoId"] for it in pl_items]
    if not vid_ids:
        print("[YT-SEO] No uploaded videos found.")
        return

    v_resp = yt.videos().list(part="snippet,contentDetails,status,statistics", id=",".join(vid_ids)).execute().get("items") or []

    full_vids, short_vids = [], []
    for v in v_resp:
        dur = parse_iso_dur_seconds(v["contentDetails"].get("duration", ""))
        is_s = dur <= 65 or "#shorts" in (v["snippet"].get("title", "")).lower()
        (short_vids if is_s else full_vids).append((v, dur))

    flagship_full_id = full_vids[0][0]["id"] if full_vids else ""
    flagship_full_url = f"https://youtu.be/{flagship_full_id}" if flagship_full_id else f"{pub}/store"

    seo_tags = [
        "tarot reading", "timeless tarot reading", "collective tarot reading",
        "financial breakthrough tarot", "abundance tarot", "4D tesseract",
        "5D mobius", "pick a card tarot", "Oracle Systems", "manifestation tarot",
    ]

    log_lines = [
        "# Oracle Systems LLC - YouTube Full-Episode 0-View Fix & SEO Report",
        f"- **Channel Videos Audited:** {len(v_resp)} ({len(full_vids)} Full Episodes, {len(short_vids)} Shorts)",
        f"- **Flagship Full Episode Linked From All Shorts:** {flagship_full_url}",
        "",
    ]

    updated_full, updated_shorts, thumbs_set = 0, 0, 0

    for v, dur in full_vids:
        vid = v["id"]
        snip = v["snippet"]
        stat = v.get("statistics", {})
        priv = v.get("status", {}).get("privacyStatus", "unknown")
        old_title = snip.get("title", "")
        new_title = clean_seo_title(old_title, is_short=False)

        snip["title"] = new_title
        snip["tags"] = seo_tags
        snip["categoryId"] = snip.get("categoryId") or "24"
        snip["description"] = (
            f"{new_title}\n"
            "Timeless 4D Tesseract and 5D Mobius living tarot transmission narrated with warm studio voice.\n\n"
            "CHAPTERS:\n"
            f"{chapters_block}\n\n"
            f"-- INTERACTIVE LIVE 4D/5D TAROT PORTAL (DRAW YOUR OWN SPREAD):\n{pub}/store\n\n"
            f"-- ORDER YOUR CUSTOM PERSONALIZED 5D AURA READING ($49):\n{pub}/go/auravideo49?utm_source=youtube_full&utm_medium=desc&utm_campaign={vid}\n\n"
            f"-- $15 4D/5D CREATOR ASSET PACK (Tesseract + Mobius Loops & 2K Templates):\n{pub}/go/assetpack15?utm_source=youtube_full&utm_medium=desc&utm_campaign={vid}\n\n"
            f"-- $15/MO SOVEREIGN 5D MEMBER VAULT:\n{pub}/go/vaultsub15?utm_source=youtube_full&utm_medium=desc&utm_campaign={vid}\n\n"
            "Comment I CLAIM THIS 5D SHIFT below if this reading resonated with your exact timeline.\n"
            "#TarotReading #TimelessTarot #AbundanceTarot #4DTesseract #5DMobius #OracleSystems"
        )
        try:
            body = {"id": vid, "snippet": snip}
            if priv in ("unlisted", "private"):
                body["status"] = {"privacyStatus": "public"}
                yt.videos().update(part="snippet,status", body=body).execute()
            else:
                yt.videos().update(part="snippet", body=body).execute()
            updated_full += 1
        except Exception as ex:
            log_lines.append(f"- [WARN FULL {vid}] Metadata update note: {str(ex)[:140]}")

        # Upload crisp 1920x1080 2K-derived thumbnail (requires verified YouTube account; degrades gracefully if not)
        t_bytes, t_name = pick_thumbnail_bytes(old_title)
        if t_bytes:
            try:
                media = MediaIoBaseUpload(io.BytesIO(t_bytes), mimetype="image/jpeg", resumable=False)
                yt.thumbnails().set(videoId=vid, media_body=media).execute()
                thumbs_set += 1
            except Exception as ex:
                log_lines.append(f"- [THUMB NOTE {vid}] Verify phone at youtube.com/verify to unlock API thumbnails ({str(ex)[:90]})")

        log_lines.append(f"- **FULL `{vid}`** ({dur}s | was `{priv}` | {stat.get('viewCount','0')} views) -> `{new_title}`")

    for v, dur in short_vids:
        vid = v["id"]
        snip = v["snippet"]
        old_title = snip.get("title", "")
        new_title = clean_seo_title(old_title, is_short=True)
        snip["title"] = new_title
        snip["tags"] = seo_tags + ["Shorts", "TarotShorts"]
        snip["description"] = (
            f"WATCH THE FULL 10-MINUTE 4D/5D READING HERE:\n{flagship_full_url}\n\n"
            f"-- STEP INTO THE LIVE 4D TESSERACT & 5D MOBIUS PORTAL:\n{pub}/store\n\n"
            f"-- $49 CUSTOM PERSONALIZED 5D AURA READING:\n{pub}/go/auravideo49?utm_source=youtube_short&utm_medium=desc&utm_campaign={vid}\n\n"
            f"-- $15 4D/5D CREATOR ASSET PACK:\n{pub}/go/assetpack15?utm_source=youtube_short&utm_medium=desc&utm_campaign={vid}\n\n"
            "Comment I CLAIM THIS ALIGNMENT below.\n"
            "#Shorts #TarotReading #4DTesseract #5DMobius #OracleSystems"
        )
        try:
            yt.videos().update(part="snippet", body={"id": vid, "snippet": snip}).execute()
            updated_shorts += 1
        except Exception as ex:
            log_lines.append(f"- [WARN SHORT {vid}] {str(ex)[:120]}")

    log_lines.append(f"\n## Summary\n- Full Episodes SEO Upgraded: **{updated_full}/{len(full_vids)}**\n- Custom Thumbnails Pushed: **{thumbs_set}/{len(full_vids)}**\n- Shorts Cross-Linked to Flagship Full Episode: **{updated_shorts}/{len(short_vids)}**")
    rep = "\n".join(log_lines) + "\n"
    open(REP_OUT, "w", encoding="utf-8", newline="").write(rep)
    print(f"[YT-SEO PASS] Upgraded {updated_full} Full Episodes (thumbnails pushed: {thumbs_set}) + Cross-linked {updated_shorts} Shorts -> {flagship_full_url}")


if __name__ == "__main__":
    main()
