import datetime as dt
import glob
import json
import os
import re
import sqlite3
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
QUEUE_DIR = os.path.join(PDIR, "deliverables", "social_queue")
DB_PATH = os.path.join(PDIR, "data", "distribution_log.db")
os.makedirs(QUEUE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def load_env(name):
    ep = os.path.join(PDIR, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8", errors="ignore"):
            if ln.strip().startswith(name + "="):
                return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "CREATE TABLE IF NOT EXISTS posts ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, platform TEXT, pack_file TEXT, "
        "status TEXT, response_note TEXT, created_utc TEXT)"
    )
    c.commit()
    c.close()


def parse_sections(md_text):
    out = {}
    parts = re.split(r"(?m)^##\s+", md_text)
    for part in parts[1:]:
        lines = part.strip().splitlines()
        if not lines:
            continue
        hdr = lines[0].lower()
        body = "\n".join(lines[1:]).strip()
        if "youtube" in hdr:
            out["youtube_pin"] = body
        elif "x /" in hdr or "twitter" in hdr:
            out["x_twitter"] = body
        elif "tiktok" in hdr or "reels" in hdr:
            out["tiktok_reels"] = body
        elif "linkedin" in hdr:
            out["linkedin"] = body
    return out


def main():
    init_db()
    packs = sorted(glob.glob(os.path.join(PDIR, "reports", "Daily_Traffic_Pack_*.md")))
    if not packs:
        print("[PHASE 47] No Daily_Traffic_Pack_*.md found yet.")
        return
    latest = packs[-1]
    secs = parse_sections(open(latest, "r", encoding="utf-8").read())

    today = dt.date.today().strftime("%Y%m%d")
    q_json = os.path.join(QUEUE_DIR, f"social_dispatch_{today}.json")
    json.dump({"source_pack": os.path.basename(latest), "generated_utc": dt.datetime.utcnow().isoformat() + "Z", "channels": secs},
              open(q_json, "w", encoding="utf-8"), indent=2)

    c = sqlite3.connect(DB_PATH)
    live_posted = 0
    for plat, text in secs.items():
        token_var = {"x_twitter": "X_USER_ACCESS_TOKEN", "linkedin": "LINKEDIN_ACCESS_TOKEN", "tiktok_reels": "TIKTOK_ACCESS_TOKEN"}.get(plat, "")
        tok = load_env(token_var) if token_var else ""
        status = "STAGED_READY"
        note = f"Staged in {os.path.basename(q_json)} (add {token_var} in .env for API autopost)" if token_var else "Ready to pin on YouTube"
        if tok and plat == "x_twitter":
            try:
                req = urllib.request.Request(
                    "https://api.twitter.com/2/tweets",
                    data=json.dumps({"text": text[:275]}).encode("utf-8"),
                    headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15) as r:
                    status = "POSTED_LIVE"
                    note = r.read().decode("utf-8", "ignore")[:160]
                    live_posted += 1
            except Exception as ex:
                status = "API_RETRY"
                note = str(ex)[:140]
        c.execute("INSERT INTO posts (platform, pack_file, status, response_note, created_utc) VALUES (?,?,?,?,?)",
                  (plat, os.path.basename(latest), status, note, dt.datetime.utcnow().isoformat() + "Z"))
    c.commit()
    c.close()
    print(f"[PHASE 47 PASS] Multi-platform distribution hub staged {len(secs)} channels -> {q_json} (live API posts: {live_posted})")


if __name__ == "__main__":
    main()
