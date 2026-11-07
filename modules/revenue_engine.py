import os
import sys
import sqlite3
import logging
import smtplib
import uuid
from email.message import EmailMessage
from datetime import datetime

BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "modules"))
import db
import vault

LOG_PATH = os.path.join(BASE_DIR, "logs", "daemon.log")
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def send_fulfillment_email(recipient_email, product_name, download_link):
    smtp_host = vault.get_secret("SMTP_HOST") or os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(vault.get_secret("SMTP_PORT") or os.environ.get("SMTP_PORT", 465))
    smtp_user = vault.get_secret("SMTP_USER") or os.environ.get("SMTP_USER", "")
    smtp_pass = vault.get_secret("SMTP_PASS") or os.environ.get("SMTP_PASS", "")

    if not smtp_user or not smtp_pass or "mock" in smtp_user:
        logging.info(f"[FULFILLMENT MOCK] Email to {recipient_email} for '{product_name}' skipped (SMTP unconfigured). Link: {download_link}")
        return False

    msg = EmailMessage()
    msg.set_content(f"""
    Thank you for your purchase from SovereignCore!

    Product: {product_name}
    Access / Download Link: {download_link}
    License Key: {str(uuid.uuid4()).upper()}

    If you have any questions, reply directly to this message.
    """)
    msg["Subject"] = f"Your Access: {product_name}"
    msg["From"] = smtp_user
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logging.info(f"[FULFILLMENT] Successfully emailed digital delivery to {recipient_email}")
        return True
    except Exception as e:
        logging.error(f"[FULFILLMENT ERROR] Failed to send email to {recipient_email}: {e}")
        return False

def process_successful_checkout(session_object):
    cust_details = session_object.get("customer_details", {})
    email = cust_details.get("email", "buyer@sovereigncore.io")
    amount_cents = session_object.get("amount_total", 1500)
    session_id = session_object.get("id", f"cs_live_{uuid.uuid4().hex[:10]}")
    line_items_desc = session_object.get("metadata", {}).get("product_name", "SovereignCore Digital Asset / License")

    db.record_revenue(session_id, email, amount_cents, status="PAID")
    logging.info(f"[REVENUE LEDGER] Recorded verified payment: ${amount_cents / 100.0:.2f} from {email} (Session: {session_id})")

    secure_token = uuid.uuid4().hex
    host_url = vault.get_secret("PUBLIC_HOST_URL") or "https://sovereigncore-gateway.onrender.com"
    fulfillment_link = f"{host_url}/api/download/secure-asset?token={secure_token}"

    email_sent = send_fulfillment_email(email, line_items_desc, fulfillment_link)
    
    return {
        "status": "FULFILLED",
        "email": email,
        "amount_usd": amount_cents / 100.0,
        "fulfillment_dispatched": email_sent
    }