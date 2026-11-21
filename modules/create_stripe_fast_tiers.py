import base64, json, os, sys, urllib.error, urllib.parse, urllib.request

pdir = sys.argv[1]
tpath = os.path.join(pdir, "config", "stripe_new_tiers.json")
tiers = {"assetpack15": "", "vaultsub15": ""}
if os.path.exists(tpath):
    try:
        tiers.update(json.load(open(tpath, "r", encoding="utf-8")))
    except Exception:
        pass

key = ""
for ln in open(os.path.join(pdir, ".env"), "r", encoding="utf-8"):
    if ln.strip().startswith("STRIPE_SECRET_KEY="):
        key = ln.split("=", 1)[1].strip().strip('"').strip("'")
        break

auth = "Basic " + base64.b64encode((key + ":").encode("ascii")).decode("ascii")

def stripe_post(path, params):
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        "https://api.stripe.com" + path,
        data=data,
        headers={"Authorization": auth, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as he:
        raise RuntimeError(f"HTTP {he.code} on {path}: {he.read().decode('utf-8', 'ignore')}")

def create_link(price_id):
    base = {"line_items[0][price]": price_id, "line_items[0][quantity]": "1"}
    try:
        return stripe_post("/v1/payment_links", base)["url"]
    except RuntimeError as ex:
        if "managed_payments" in str(ex).lower() or "tax_code" in str(ex).lower():
            base["managed_payments[enabled]"] = "false"
            return stripe_post("/v1/payment_links", base)["url"]
        raise

# txcd_10000000 = General - Electronically Supplied Services (Stripe Managed Payments eligible)
if not tiers.get("assetpack15"):
    p1 = stripe_post("/v1/products", {
        "name": "Oracle 4D Tesseract Creator Asset Pack",
        "description": "Seamless 4D Tesseract + Mobius video loops and 3D thumbnail templates",
        "tax_code": "txcd_10000000",
    })
    pr1 = stripe_post("/v1/prices", {"unit_amount": "1500", "currency": "usd", "product": p1["id"]})
    tiers["assetpack15"] = create_link(pr1["id"])
    print(f"[STRIPE LIVE] Created $15 Asset Pack Link -> {tiers['assetpack15']}")
else:
    print(f"[STRIPE LIVE] $15 Asset Pack Link active -> {tiers['assetpack15']}")

if not tiers.get("vaultsub15"):
    p2 = stripe_post("/v1/products", {
        "name": "Oracle Sovereign 4D Member Vault (Monthly)",
        "description": "Monthly unlimited access to 30-min 4D transmissions and 432Hz downloads",
        "tax_code": "txcd_10000000",
    })
    pr2 = stripe_post("/v1/prices", {"unit_amount": "1500", "currency": "usd", "recurring[interval]": "month", "product": p2["id"]})
    tiers["vaultsub15"] = create_link(pr2["id"])
    print(f"[STRIPE LIVE] Created $15/mo Vault Subscription Link -> {tiers['vaultsub15']}")
else:
    print(f"[STRIPE LIVE] $15/mo Vault Subscription Link active -> {tiers['vaultsub15']}")

json.dump(tiers, open(tpath, "w", encoding="utf-8"), indent=2)