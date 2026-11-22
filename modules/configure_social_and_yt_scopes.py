import argparse
import os

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
ENV_P = os.path.join(PDIR, ".env")
TOK_YT = os.path.join(PDIR, "config", "youtube_token.json")
CLIENT_SECRETS = os.path.join(PDIR, "config", "youtube_client_secret.json")


def load_env_lines():
    if not os.path.exists(ENV_P):
        return []
    return open(ENV_P, "r", encoding="utf-8", errors="ignore").read().splitlines()


def set_env_key(lines, key, val):
    if not val:
        return lines
    out = []
    found = False
    for ln in lines:
        if ln.strip().startswith(key + "="):
            out.append(f"{key}={val}")
            found = True
        else:
            out.append(ln)
    if not found:
        out.append(f"{key}={val}")
    return out


def check_status():
    env = {}
    for ln in load_env_lines():
        s = ln.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")

    x_ok = bool(env.get("X_USER_ACCESS_TOKEN") or env.get("TWITTER_BEARER_USER_TOKEN"))
    li_ok = bool(env.get("LINKEDIN_ACCESS_TOKEN") and env.get("LINKEDIN_AUTHOR_URN"))
    print(f"[SOCIAL API STATUS] X/Twitter Auto-Post: {'ARMED' if x_ok else 'NOT SET'} | LinkedIn Auto-Post: {'ARMED' if li_ok else 'NOT SET'}")
    if not x_ok or not li_ok:
        print("  To arm hands-free social posting anytime without touching code, run:")
        print('  python .\\Modules\\configure_social_and_yt_scopes.py --x-token "YOUR_X_TOKEN" --li-token "YOUR_LI_TOKEN" --li-urn "urn:li:person:YOUR_ID"')


def upgrade_youtube_comment_scope():
    if not os.path.exists(CLIENT_SECRETS):
        # Fallback search for Google OAuth client secret JSON in config/
        for fn in os.listdir(os.path.join(PDIR, "config")):
            if "client_secret" in fn.lower() and fn.endswith(".json"):
                cs = os.path.join(PDIR, "config", fn)
                break
        else:
            print("[YT-SCOPE] Client secret JSON not found in config\\. Skipping browser OAuth.")
            return
    else:
        cs = CLIENT_SECRETS

    from google_auth_oauthlib.flow import InstalledAppFlow
    scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtube.readonly",
    ]
    print("[YT-SCOPE] Opening browser to authorize YouTube Comment + Upload scope (sign in as toomer1027@gmail.com)...")
    flow = InstalledAppFlow.from_client_secrets_file(cs, scopes)
    creds = flow.run_local_server(port=0)
    open(TOK_YT, "w", encoding="utf-8").write(creds.to_json())
    print(f"[YT-SCOPE PASS] Updated {TOK_YT} with youtube.force-ssl! Live YouTube conversion comments are now unlocked.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x-token", type=str, default="")
    ap.add_argument("--li-token", type=str, default="")
    ap.add_argument("--li-urn", type=str, default="")
    ap.add_argument("--upgrade-yt-scope", action="store_true")
    args = ap.parse_args()

    changed = False
    lines = load_env_lines()
    for k, v in [
        ("X_USER_ACCESS_TOKEN", args.x_token.strip()),
        ("LINKEDIN_ACCESS_TOKEN", args.li_token.strip()),
        ("LINKEDIN_AUTHOR_URN", args.li_urn.strip()),
    ]:
        if v:
            lines = set_env_key(lines, k, v)
            changed = True
    if changed:
        open(ENV_P, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
        print("[ENV PASS] Updated .env with social API credentials (remains strictly gitignored).")

    if args.upgrade_yt_scope:
        upgrade_youtube_comment_scope()

    check_status()


if __name__ == "__main__":
    main()
