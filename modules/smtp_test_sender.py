import datetime as dt
import os
import smtplib
import sys
from email.message import EmailMessage


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


def main():
    pdir = sys.argv[1]
    recip = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else ""
    env = load_env(pdir)
    user = env.get("GMAIL_USER", "Toomer1980@gmail.com").strip()
    pwd  = (env.get("GMAIL_APP_PASSWORD", "") or "").replace(" ", "").strip()
    if not recip:
        recip = user

    if not user or "@" not in user:
        print(f"[FAIL] GMAIL_USER in .env is invalid ('{user}'). Run .\\setup_gmail_smtp.ps1 and press Enter on Gmail Address.")
        sys.exit(2)
    if len(pwd) != 16:
        print(f"[WARN] GMAIL_APP_PASSWORD length is {len(pwd)} chars (Google App Passwords are 16 letters without spaces).")

    pub_url = env.get("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = recip
    msg["Subject"] = "[SMTP TEST] Oracle Systems Pro_Node ($49,999) Outreach Pipeline Live"
    msg.set_content(
        f"Hi Thomas,\n\n"
        f"Your Oracle Systems LLC Gmail SMTP pipeline is LIVE and verified.\n"
        f"Live 4D Storefront: {pub_url}/store\n"
        f"Live Member Portal: {pub_url}/portal\n"
        f"Timestamp: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST\n"
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as s:
            s.login(user, pwd)
            s.send_message(msg)
        print(f"[LIVE PASS] Delivered test email via Gmail SSL (465) to {recip}! Check your inbox.")
    except smtplib.SMTPAuthenticationError as ae:
        print(f"[AUTH FAIL] Google rejected login for {user}: {ae.smtp_error.decode('utf-8', 'ignore') if isinstance(ae.smtp_error, bytes) else ae.smtp_error}")
        print("  -> Generate a NEW 16-letter App Password at https://myaccount.google.com/apppasswords and run .\\setup_gmail_smtp.ps1")
        sys.exit(3)
    except Exception as ex:
        print(f"[FAIL] SMTP error: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()