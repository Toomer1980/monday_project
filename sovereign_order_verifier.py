import os, json, glob, secrets, stripe
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
CACHE_P = BASE + "/data/verified_sessions.json"
os.makedirs(BASE + "/data", exist_ok=True)

def _plain(obj):
    if obj is None: return {}
    if isinstance(obj, dict): return obj
    if hasattr(obj, "to_dict_recursive"): return obj.to_dict_recursive()
    if hasattr(obj, "to_dict"): return obj.to_dict()
    return {}

def _load():
    return json.load(open(CACHE_P, "r", encoding="utf-8")) if os.path.exists(CACHE_P) else {}

def _save(d):
    json.dump(d, open(CACHE_P, "w", encoding="utf-8"), indent=2)

def _stripe_key():
    ek = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if ek: return ek
    ef = BASE + "/.stripe_env.json"
    return json.load(open(ef, "r", encoding="utf-8")).get("STRIPE_SECRET_KEY", "").strip() if os.path.exists(ef) else ""

def lookup_cached(q):
    q = (q or "").strip().lower()
    if not q: return None
    for sid, v in _load().items():
        vals = [sid, v.get("download_token",""), v.get("license_key",""), v.get("invoice_number",""), v.get("receipt_number","")]
        if q in [str(x).lower() for x in vals if x]:
            return v
    return None

def unlock_session(sid, invoice_hint="", receipt_hint=""):
    sid = (sid or "").strip()
    hit = lookup_cached(sid)
    if hit:
        changed = False
        if invoice_hint and not hit.get("invoice_number"): hit["invoice_number"] = invoice_hint; changed = True
        if receipt_hint and not hit.get("receipt_number"): hit["receipt_number"] = receipt_hint; changed = True
        if changed:
            c = _load(); c[hit["session_id"]] = hit; _save(c)
        return hit
    stripe.api_key = _stripe_key()
    sd = _plain(stripe.checkout.Session.retrieve(sid, expand=["invoice"]))
    pstat, sstat = sd.get("payment_status", ""), sd.get("status", "")
    if pstat not in ("paid", "no_payment_required") and sstat != "complete":
        return None
    meta = _plain(sd.get("metadata"))
    amt = int(sd.get("amount_total") or 4900)
    cd = _plain(sd.get("customer_details"))
    em = cd.get("email") or sd.get("customer_email") or meta.get("email") or "Toomer1980@gmail.com"
    sku = meta.get("sku") or ("personal_3d_video" if amt == 4900 else "pro_node")
    inv = _plain(sd.get("invoice")) if not isinstance(sd.get("invoice"), str) else {}
    inv_num = inv.get("number") or invoice_hint
    if not meta.get("portrait_url"):
        ps = [x for x in sorted(glob.glob(BASE + "/static/portraits/p_*.png"), key=os.path.getmtime, reverse=True) if "_depth" not in x]
        if ps: meta["portrait_url"] = "/static/portraits/" + os.path.basename(ps[0])
    info = {
        "session_id": sid, "sku": sku, "email": em, "amount_cents": amt,
        "payment_intent": sd.get("payment_intent") or "",
        "product_name": "Oracle 3D/4K Personalized Aura Reading Video" if sku == "personal_3d_video" else sku,
        "license_key": "ORACLE-" + secrets.token_hex(4).upper() + "-" + secrets.token_hex(4).upper(),
        "download_token": "tok_" + secrets.token_hex(16),
        "invoice_number": inv_num, "receipt_number": receipt_hint, "stripe_payment_status": pstat,
        "verified_at": datetime.now().isoformat()
    }
    c = _load(); c[sid] = info; _save(c)
    try:
        import sovereign_revenue_fulfillment as srf
        srf.enqueue_paid_order(sid, sku, em, amt / 100.0, meta)
    except Exception as e:
        print("[*] Fulfillment queue note:", e)
    return info

def sync_recent_stripe_sales():
    stripe.api_key = _stripe_key()
    if not stripe.api_key: return 0
    synced = 0
    try:
        for s in stripe.checkout.Session.list(limit=15).data:
            sd = _plain(s)
            if sd.get("payment_status") == "paid" and not lookup_cached(sd.get("id")):
                if unlock_session(sd["id"]): synced += 1
    except Exception: pass
    return synced

if __name__ == "__main__":
    stripe.api_key = _stripe_key()
    try:
        bal = _plain(stripe.Balance.retrieve())
        avail = sum(x.get("amount", 0) for x in bal.get("available", [])) / 100.0
        pend = sum(x.get("amount", 0) for x in bal.get("pending", [])) / 100.0
        print(f"[+] YOUR STRIPE MERCHANT BALANCE -> Available: ${avail:.2f} | Pending Settlement: ${pend:.2f}")
    except Exception as e:
        print("[*] Stripe Balance check (restricted key scope):", e)
    sid = "cs_live_a0yFX2Nr82AqmapmpYKVnFXCjd7OEy8iyxvMWiaq77fHd3HZubqhQ4p8Kc"
    res = unlock_session(sid, invoice_hint="CPHAMCTV-0001", receipt_hint="2352-8553")
    sync_recent_stripe_sales()
    print("[+] UNLOCKED LICENSE & ORDER RECORD:")
    print(json.dumps(res, indent=2))
