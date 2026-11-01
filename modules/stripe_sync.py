import os, sys, logging, stripe
BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "modules"))
import vault

def register_cloud_webhook(cloud_url, stripe_key=None):
    key = stripe_key or vault.get_secret("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_SECRET_KEY")
    if not key or "mock" in key:
        raise ValueError("Save your real STRIPE_SECRET_KEY in the Vault first.")
    stripe.api_key = key
    url = str(cloud_url).rstrip("/")
    if not url.endswith("/api/billing/stripe-webhook"):
        url += "/api/billing/stripe-webhook"
    ep = stripe.WebhookEndpoint.create(url=url, enabled_events=["checkout.session.completed"])
    if ep.get("secret"):
        vault.set_secret("STRIPE_WEBHOOK_SECRET", ep.get("secret"))
    vault.set_secret("CLOUD_WEBHOOK_URL", url)
    return {"id": ep.get("id"), "url": url}
