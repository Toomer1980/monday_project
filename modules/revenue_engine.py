import os, sys, uuid, json, zipfile, logging
from datetime import datetime
BASE = "C:/Users/toome/Desktop/SovereignCore"
if os.name != "nt" or not os.path.exists(BASE):
    BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE, "modules"))
import db

ASSET_DIR = os.path.join(BASE, "data", "assets")
os.makedirs(ASSET_DIR, exist_ok=True)

CATALOG = {
    "guide_52wk": {"sku": "guide_52wk", "name": "Oracle 52-Week Collective Reading & Media Blueprint", "price_cents": 2900, "badge": "DIGITAL BUNDLE", "desc": "52-week 30-min collective reading scripts, viral hooks, daily schedule & monetization guide."},
    "pro_node": {"sku": "pro_node", "name": "SovereignCore Pro Automation Node License", "price_cents": 9900, "badge": "PRO SOFTWARE", "desc": "4-worker thread swarm engine, DPAPI encryption vault, telemetry exporter & lifetime Pro license key."},
    "creator_suite": {"sku": "creator_suite", "name": "Oracle Studio & Merchandising Automation Suite", "price_cents": 24900, "badge": "CREATOR ENGINE", "desc": "Automated studio batch workflows, high-margin merchandise launch templates (apparel & mugs) & funnels."},
    "enterprise_swarm": {"sku": "enterprise_swarm", "name": "Oracle Systems Enterprise Custom Swarm Deployment", "price_cents": 150000, "badge": "ENTERPRISE TIER", "desc": "Full dual-cloud enterprise deployment, custom Stripe revenue engine, priority webhooks & commercial license."}
}

def build_customer_bundle(info):
    os.makedirs(ASSET_DIR, exist_ok=True)
    zp = os.path.join(ASSET_DIR, f"Oracle_Bundle_{info['download_token']}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("01_LICENSE_CERTIFICATE.txt", f"ORACLE SYSTEMS LLC // VERIFIED LICENSE\nProduct: {info['product_name']}\nCustomer: {info['email']}\nLicense Key: {info['license_key']}\nOrder ID: {info['session_id']}\nAmount: ${info['amount_cents']/100:.2f} USD\nIssued: {datetime.now().isoformat()}\n")
        zf.writestr("02_52_WEEK_MEDIA_BLUEPRINT.md", "# ORACLE SYSTEMS 52-WEEK MEDIA & $1,500/DAY REVENUE BLUEPRINT\n1. 00:00-02:30 Hook & Energy Theme\n2. 02:30-12:00 Past Foundation\n3. 12:00-22:00 Turning Point\n4. 22:00-30:00 Extended Reading & Storefront CTA (/store)\n")
        zf.writestr("03_SOVEREIGN_NODE_CONFIG.json", json.dumps({"org": "Oracle Systems LLC", "license_key": info["license_key"], "sku": info["sku"], "workers": 4, "verified": True}, indent=2))
    return zp

def process_successful_checkout(sess):
    cust, meta = sess.get("customer_details") or {}, sess.get("metadata") or {}
    sku = meta.get("sku", "pro_node")
    prod = CATALOG.get(sku, CATALOG["pro_node"])
    email = cust.get("email") or meta.get("email") or "client@oraclesystems.io"
    amt = int(sess.get("amount_total") or prod["price_cents"])
    sid = sess.get("id") or f"ord_{uuid.uuid4().hex[:8]}"
    lkey = "ORCL-" + "-".join(uuid.uuid4().hex[:4].upper() for _ in range(4))
    dtok = f"tok_{uuid.uuid4().hex}"
    info = {"session_id": sid, "email": email, "amount_cents": amt, "sku": sku, "product_name": prod["name"], "license_key": lkey, "download_token": dtok}
    db.record_revenue(sid, email, amt, "PAID", sku, prod["name"], lkey, dtok)
    build_customer_bundle(info)
    logging.info(f"[REVENUE ENGINE] Fulfilled {prod['name']} (${amt/100:.2f}) | Key: {lkey}")
    return info
