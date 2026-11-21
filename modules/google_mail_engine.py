import base64
import datetime as dt
import os
import smtplib
import ssl
import subprocess
import sys
from email.message import EmailMessage

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def load_env(pdir):
    out = {}
    ep = os.path.join(pdir, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8"):
            t = ln.strip()
            if t and not t.startswith("#") and "=" in t:
                k, v = t.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def ensure_google_libs():
    try:
        import googleapiclient  # noqa
        import google_auth_oauthlib  # noqa
    except ImportError:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--quiet",
            "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2"
        ])


def send_via_gmail_api(pdir, to_addr, subject, body_text, sender_email):
    secret = os.path.join(pdir, "config", "youtube_client_secret.json")
    token  = os.path.join(pdir, "config", "gmail_token.json")
    if not os.path.exists(secret):
        raise FileNotFoundError(f"Missing OAuth client JSON at {secret}")

    ensure_google_libs()
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secret, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    msg = EmailMessage()
    msg["To"] = to_addr
    msg["From"] = sender_email
    msg["Subject"] = subject
    msg.set_content(body_text)
    raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    res = service.users().messages().send(userId="me", body={"raw": raw_b64}).execute()
    return f"Gmail API HTTPS/443 (id={res.get('id', 'ok')})"


def send_via_smtp(user, pwd, to_addr, subject, body_text):
    ctx = ssl.create_default_context()
    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body_text)
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as s:
        s.ehlo()
        s.starttls(context=ctx)
        s.ehlo()
        s.login(user, pwd)
        s.send_message(msg)
    return "SMTP Port 587 (STARTTLS)"


def send_oracle_email(pdir, to_addr, subject, body_text):
    env = load_env(pdir)
    user = env.get("GMAIL_USER", "Toomer1980@gmail.com").strip()
    pwd  = (env.get("GMAIL_APP_PASSWORD", "") or "").replace(" ", "").strip()
    if not to_addr:
        to_addr = user

    api_err = ""
    try:
        return send_via_gmail_api(pdir, to_addr, subject, body_text, user)
    except Exception as ex:
        api_err = str(ex)

    if pwd and "PASTE_16_CHAR" not in pwd and len(pwd) >= 12:
        try:
            return send_via_smtp(user, pwd, to_addr, subject, body_text)
        except Exception as ex2:
            raise RuntimeError(f"Gmail API failed ({api_err}) | SMTP fallback failed ({ex2})")

    raise RuntimeError(f"Gmail API failed: {api_err}")


if __name__ == "__main__":
    pdir = sys.argv[1]
    to_addr = sys.argv[2] if len(sys.argv) > 2 else ""
    subj = sys.argv[3] if len(sys.argv) > 3 else "[ORACLE SYSTEMS] Live HTTPS Gmail API Test"
    body = sys.argv[4] if len(sys.argv) > 4 else (
        f"Hi Thomas,\n\nYour Oracle Systems LLC Gmail API (HTTPS Port 443) delivery engine is LIVE.\n"
        f"This bypasses ISP SMTP 587/465 blocks for automated $49 AuraVideo49 fulfillment and Pro_Node B2B sprints.\n"
        f"Timestamp: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST\n"
    )
    try:
        via = send_oracle_email(pdir, to_addr, subj, body)
        print(f"[EMAIL PASS] Sent via {via} -> {to_addr or 'Toomer1980@gmail.com'}")
    except Exception as e:
        print(f"[EMAIL ACTION NEEDED] {e}")
        if "accessNotConfigured" in str(e) or "Gmail API has not been used" in str(e):
            print("  -> Enable 'Gmail API' in Google Cloud Library (1 click): https://console.cloud.google.com/apis/library/gmail.googleapis.com")
        sys.exit(2)