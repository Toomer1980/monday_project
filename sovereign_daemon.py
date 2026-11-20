import os, json, stripe
if os.path.exists(".stripe_env.json"):
    for _k, _v in json.load(open(".stripe_env.json", encoding="utf-8")).items():
        if isinstance(_v, str) and (_v.startswith("sk_") or _v.startswith("rk_")):
            os.environ["STRIPE_SECRET_KEY"] = _v.strip()
            stripe.api_key = _v.strip()

import os, sys, json, time, logging, threading
import psutil, stripe
from flask import Flask, request, jsonify, Response, send_file

BASE = "C:/Users/toome/Desktop/SovereignCore"
if os.name != "nt" or not os.path.exists(BASE):
    BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE, "modules"))
import db, export_report, plugins, vault, stripe_sync, revenue_engine
from task_engine import swarm

LOG_P = os.path.join(BASE, "logs", "daemon.log")
os.makedirs(os.path.dirname(LOG_P), exist_ok=True)
logging.basicConfig(filename=LOG_P, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
app = Flask("SovereignGateway")
logging.getLogger("werkzeug").setLevel(logging.ERROR)

def is_real_key(k):
    return bool(k and (k.startswith('sk_') or k.startswith('rk_')))

def get_readiness():
    sk = json.load(open('C:/Users/toome/Desktop/SovereignCore/.stripe_env.json'))['STRIPE_SECRET_KEY'] or ""
    su = vault.get_secret("SMTP_USER") or ""
    sp = vault.get_secret("SMTP_PASS") or ""
    return {
        "stripe_live": is_real_key(sk),
        "smtp_live": bool(su and sp and "YOUR_" not in sp)
    }

def build_snapshot():
    vm = psutil.virtual_memory()
    dk = psutil.disk_usage("C:/" if os.name == "nt" else "/")
    lgs = []
    if os.path.exists(LOG_P):
        lgs = [l.strip() for l in open(LOG_P, encoding="utf-8") if l.strip()][-6:]
    return {
        "cpu_pct": psutil.cpu_percent(interval=None),
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_pct": vm.percent,
        "ram_used_gb": round(vm.used / (1024**3), 2),
        "disk_pct": dk.percent,
        "queue_depth": swarm.task_queue.qsize(),
        "vault_keys": vault.list_secret_keys(),
        "readiness": get_readiness(),
        "revenue": db.get_revenue_summary(),
        "orders": db.get_recent_orders(6),
        "tasks": db.get_recent_tasks(6),
        "logs": lgs
    }

@app.route("/api/health")
def api_health():
    return jsonify({"status": "HEALTHY", "org": "Oracle Systems LLC"}), 200

@app.route("/api/status")
def api_status():
    return jsonify({"status": "ONLINE", "revenue": db.get_revenue_summary()}), 200

@app.route("/api/stream")
def api_stream():
    def gen():
        while True:
            yield f"data: {json.dumps(build_snapshot())}\n\n"
            time.sleep(1.5)
    return Response(gen(), mimetype="text/event-stream")

@app.route("/api/task/submit", methods=["POST"])
def api_submit():
    d = request.get_json(force=True, silent=True) or {}
    tid = swarm.enqueue_task(d.get("task_name", "Job"), lambda *a: time.sleep(0.3))
    return jsonify({"status": "QUEUED", "task_id": tid}), 202

@app.route("/api/tasks/purge", methods=["POST"])
def api_purge():
    return jsonify({"status": "PURGED", "count": swarm.purge_queue()}), 200

@app.route("/api/tasks/export-csv", methods=["POST"])
def api_export():
    return jsonify({"status": "EXPORTED", "path": export_report.generate_csv_report()}), 200

@app.route("/api/plugins/audit", methods=["POST"])
def api_audits():
    ids = [
        swarm.enqueue_task("Audit-Disk", plugins.audit_disk_cleanup),
        swarm.enqueue_task("Audit-Log", plugins.audit_log_rotation),
        swarm.enqueue_task("Audit-Net", plugins.audit_network_latency),
        swarm.enqueue_task("Audit-Git", plugins.audit_git_sync)
    ]
    return jsonify({"status": "QUEUED", "queued": ids}), 202

@app.route("/api/vault/set", methods=["POST"])
def api_vault_set():
    d = request.get_json(force=True, silent=True) or {}
    vault.set_secret(d.get("key"), d.get("value"))
    return jsonify({"status": "ENCRYPTED", "keys": vault.list_secret_keys()}), 200

@app.route("/api/webhook/stripe", methods=["POST", "GET"])
def api_stripe_webhook():
    if request.method == "GET":
        return jsonify({"status": "ONLINE", "route": "/api/webhook/stripe"}), 200
    payload = request.get_json(force=True, silent=True) or {}
    if payload.get("type") == "checkout.session.completed":
        obj = payload.get("data", {}).get("object", {})
        info = revenue_engine.process_successful_checkout(obj)
        return jsonify({"status": "RECORDED", "order": info}), 200
    return jsonify({"status": "IGNORED"}), 200





@app.route("/api/billing/create-checkout", methods=["POST"])
def api_checkout_live_stripe():
    d = request.get_json(force=True, silent=True) or {}
    sku = d.get("sku", "pro_node")
    if sku not in revenue_engine.CATALOG: sku = "pro_node"
    em = (d.get("email") or "Toomer1980@gmail.com").strip()
    pr = revenue_engine.CATALOG.get(sku, revenue_engine.CATALOG["pro_node"])
    sk_live = json.load(open("C:/Users/toome/Desktop/SovereignCore/.stripe_env.json", encoding="utf-8")).get("STRIPE_SECRET_KEY", "").strip()
    bu = request.host_url.rstrip("/")
    stripe.api_key = sk_live
    try:
        s = stripe.checkout.Session.create(
            customer_email=em, mode="payment",
            line_items=[{"price_data": {"currency": "usd", "unit_amount": pr["price_cents"], "product_data": {"name": pr["name"], "tax_code": "txcd_10000000"}}, "quantity": 1}],
            metadata={"sku": sku, "email": em, "name": str(d.get("name",""))[:60], "focus": str(d.get("focus",""))[:200], "portrait_url": str(d.get("portrait_url",""))[:200], "aura_hex": str(d.get("aura_hex","#38bdf8"))[:16]},
            success_url=f"{bu}/portal?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{bu}/store"
        )
        return jsonify({"status": "REDIRECT", "checkout_url": s.url}), 200
    except Exception as e1:
        try:
            s = stripe.checkout.Session.create(
                customer_email=em, mode="payment",
                managed_payments={"enabled": False},
                line_items=[{"price_data": {"currency": "usd", "unit_amount": pr["price_cents"], "product_data": {"name": pr["name"]}}, "quantity": 1}],
                metadata={"sku": sku, "email": em, "name": str(d.get("name",""))[:60], "focus": str(d.get("focus",""))[:200], "portrait_url": str(d.get("portrait_url",""))[:200], "aura_hex": str(d.get("aura_hex","#38bdf8"))[:16]},
                success_url=f"{bu}/portal?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{bu}/store"
            )
            return jsonify({"status": "REDIRECT", "checkout_url": s.url}), 200
        except Exception as e2:
            return jsonify({"status": "ERROR", "error": str(e2), "primary": str(e1)}), 500


@app.route("/personalize")
@app.route("/oracle-3d")
def oracle_3d_sanctuary():
    return open("C:/Users/toome/Desktop/SovereignCore/templates/oracle_3d_stage.html", "r", encoding="utf-8").read()

@app.route("/api/personalize/reading", methods=["POST"])
def api_personalize_reading():
    import secrets, hashlib, urllib.request
    from PIL import Image
    import oracle_audio_master
    name = (request.form.get("name") or "Sovereign Seeker").strip()[:40]
    focus = (request.form.get("focus") or "Financial & Spiritual Breakthrough").strip()[:160]
    rid = secrets.token_hex(4)
    aura_hex = "#38bdf8"
    portrait_url = ""
    photo = request.files.get("photo")
    if photo and photo.filename:
        pdir = "C:/Users/toome/Desktop/SovereignCore/static/portraits"
        os.makedirs(pdir, exist_ok=True)
        pfile = f"{pdir}/p_{rid}.png"
        im = Image.open(photo.stream).convert("RGB")
        im.thumbnail((512, 512))
        im.save(pfile)
        portrait_url = f"/static/portraits/p_{rid}.png"
        import oracle_art_factory as _oaf
        _oaf.make_depth_map(pfile, f"{pdir}/p_{rid}_depth.png")
        small = im.resize((16, 16))
        px = list(small.getdata())
        best = max(px, key=lambda c: max(c) - min(c))
        aura_hex = "#%02x%02x%02x" % (min(255, best[0]+45), min(255, best[1]+45), min(255, best[2]+45))
    deck = ["The Magician", "The Star", "The Sun", "Ace of Pentacles", "Nine of Pentacles", "Ten of Pentacles", "Wheel of Fortune", "The Emperor", "The High Priestess", "Six of Wands", "The World", "King of Pentacles"]
    h = int(hashlib.sha256((name + focus + aura_hex).encode()).hexdigest(), 16)
    c1 = deck[h % len(deck)]
    c2 = deck[(h // 13) % len(deck)]
    c3 = deck[(h // 37) % len(deck)]
    import oracle_art_factory as _oaf
    i1, d1 = _oaf.ensure_card_art(c1); i2, d2 = _oaf.ensure_card_art(c2); i3, d3 = _oaf.ensure_card_art(c3)
    cards = [{"pos": "I. PAST FOUNDATION", "name": c1, "img": i1, "depth": d1}, {"pos": "II. PRESENT SHIFT", "name": c2, "img": i2, "depth": d2}, {"pos": "III. INCOMING OUTCOME", "name": c3, "img": i3, "depth": d3}]
    scenario = f"Welcome {name}. Your energy signature has been assimilated into the Oracle field. Regarding {focus}, {c1} confirms you outgrew old limitations. Right now {c2} is activating clarity and direct alignment around you. Moving forward, {c3} signals a concrete breakthrough arriving over the next seventy-two hours. Trust the opening in front of you."
    try:
        prompt = f"Respond strictly in English. Write a warm, realistic 95-word personalized tarot reading for {name} focused on {focus}, weaving in the three cards: {c1}, {c2}, and {c3}. You are the Oracle reader speaking directly to {name}. Never say your own name is {name}."
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=json.dumps({"model": "qwen2.5:0.5b", "prompt": prompt, "stream": False, "keep_alive": "2m"}).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=18) as r:
            ai_txt = json.loads(r.read().decode("utf-8")).get("response", "").strip()
            clean = "".join(ch if (32 <= ord(ch) < 127) else " " for ch in ai_txt)
            if len(clean) > 120: scenario = " ".join(clean.split())
    except Exception: pass
    audio_file = f"C:/Users/toome/Desktop/SovereignCore/static/portraits/r_{rid}.mp3"
    audio_url = ""
    if oracle_audio_master.synthesize_human_voice(scenario, audio_file):
        audio_url = f"/static/portraits/r_{rid}.mp3"
    return jsonify({"status": "OK", "name": name, "headline": focus, "aura_hex": aura_hex, "portrait_url": portrait_url, "portrait_depth_url": portrait_url.replace(".png", "_depth.png") if portrait_url else "", "cards": cards, "scenario": scenario, "audio_url": audio_url}), 200


try:
    revenue_engine.CATALOG["personal_3d_video"] = {"name": "Oracle 3D/4K Personalized Aura Reading Video", "price_cents": 4900}
except Exception: pass

@app.route("/api/evolution/telemetry", methods=["GET"])
def api_evolution_telemetry():
    import sovereign_evolution_engine as _evo
    return jsonify(_evo.get_telemetry()), 200


@app.route("/api/voice/config", methods=["GET", "POST"])
def api_voice_config():
    p = "C:/Users/toome/Desktop/SovereignCore/VOICE_CONFIG.json"
    cfg = json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else {"mode": "neural", "custom_sample": "C:/Users/toome/Desktop/SovereignCore/voice_samples/thomas_voice.wav"}
    if request.method == "POST":
        d = request.get_json(force=True, silent=True) or {}
        if d.get("mode") in ("neural", "custom"):
            cfg["mode"] = d["mode"]
            json.dump(cfg, open(p, "w", encoding="utf-8"), indent=2)
    cfg["has_sample"] = os.path.exists(cfg.get("custom_sample", ""))
    return jsonify(cfg), 200

@app.route("/api/voice/upload-sample", methods=["POST"])
def api_voice_upload_sample():
    import subprocess as _sp
    f = request.files.get("voice")
    if not f: return jsonify({"error": "no audio"}), 400
    vdir = "C:/Users/toome/Desktop/SovereignCore/voice_samples"
    os.makedirs(vdir, exist_ok=True)
    raw_p = vdir + "/raw_upload.bin"
    wav_p = vdir + "/thomas_voice.wav"
    f.save(raw_p)
    _sp.run(["ffmpeg", "-y", "-i", raw_p, "-ac", "1", "-ar", "24000", wav_p], stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, creationflags=0x08000000)
    return jsonify({"status": "SAVED", "path": wav_p}), 200


@app.route("/api/leads/capture", methods=["POST"])
def api_leads_capture():
    import sovereign_revenue_fulfillment as _srf
    x = request.get_json(force=True, silent=True) or {}
    if x.get("email"): _srf.capture_lead(x["email"], x.get("name",""), x.get("focus",""), x.get("portrait_url",""), x.get("aura_hex","#38bdf8"))
    return jsonify({"status": "CAPTURED"}), 200

@app.route("/api/revenue/dashboard", methods=["GET"])
def api_revenue_dashboard():
    import sovereign_revenue_fulfillment as _srf, sovereign_evolution_engine as _evo
    return jsonify({"revenue_fulfillment": _srf.get_dashboard(), "evolution": _evo.get_telemetry()}), 200

@app.route("/api/webhook/stripe/fulfill", methods=["POST"])
def api_stripe_fulfill_hook():
    import sovereign_revenue_fulfillment as _srf
    ev = request.get_json(force=True, silent=True) or {}
    if ev.get("type") == "checkout.session.completed":
        obj = (ev.get("data") or {}).get("object") or {}
        meta = obj.get("metadata") or {}
        sid = obj.get("id", "")
        amt = float(obj.get("amount_total") or 0) / 100.0
        em = obj.get("customer_email") or meta.get("email") or "Toomer1980@gmail.com"
        if sid: _srf.enqueue_paid_order(sid, meta.get("sku", "pro_node"), em, amt, meta)
    return jsonify({"received": True}), 200

@app.route("/api/download/secure-asset")
def api_dl():
    o = db.get_order_by_token((request.args.get("token") or "").strip())
    if not o: return jsonify({"error": "Invalid token"}), 403
    info = {"session_id": o["session_id"], "email": o["customer_email"],
            "amount_cents": o["amount_cents"], "sku": o.get("product_sku") or "pro_node",
            "product_name": o.get("product_name") or "Oracle Bundle",
            "license_key": o.get("license_key") or "ORCL-PRO",
            "download_token": o.get("download_token")}
    zp = revenue_engine.build_customer_bundle(info)
    return send_file(zp, as_attachment=True, download_name=f"Oracle_{info['license_key']}.zip")

@app.route("/store")
def web_store():
    h = [
        "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Oracle Store</title>",
        "<style>body{background:#060911;color:#fff;font-family:sans-serif;margin:0}",
        ".nav{display:flex;justify-content:space-between;padding:16px 32px;background:#111827}",
        ".nav a{color:#38bdf8;margin-left:16px;text-decoration:none;font-weight:bold}",
        ".grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;max-width:960px;margin:24px auto}",
        ".card{background:#111827;border:1px solid #10b981;padding:20px;border-radius:8px}",
        ".pr{font-size:28px;color:#38bdf8;font-weight:bold;margin:8px 0}",
        "button{background:#059669;color:#fff;border:none;padding:12px;width:100%;border-radius:6px;cursor:pointer;font-weight:bold}",
        "input{background:#111827;border:1px solid #38bdf8;color:#fff;padding:10px;width:280px}</style></head><body>",
        "<div class='nav'><b>ORACLE SYSTEMS LLC // STOREFRONT</b>",
        "<div><a href='/store'>Store</a><a href='/portal'>Portal</a><a href='/dashboard'>Matrix</a></div></div>",
        "<div style='text-align:center;padding:24px'><h1>Autonomous Compute & Media Systems</h1>",
        "<input id='em' value='Toomer1980@gmail.com'/><div id='st' style='color:#34d399;margin-top:8px'></div></div>",
        "<div class='grid'>"
    ]
    for k, p in revenue_engine.CATALOG.items():
        pr = f"${p['price_cents']/100:,.2f}"
        h.append(f"<div class='card'><small style='color:#34d399'>{p['badge']}</small>")
        h.append(f"<h3>{p['name']}</h3><div class='pr'>{pr}</div><p>{p['desc']}</p>")
        h.append(f"<button onclick=\"buy('{k}')\">Purchase & Instant ZIP Delivery</button></div>")
    h.append("</div><script>async function buy(s){document.getElementById('st').innerText='Processing...';")
    h.append("const r=await fetch('/api/billing/create-checkout',{method:'POST',headers:{'Content-Type':'application/json'},")
    h.append("body:JSON.stringify({sku:s,email:document.getElementById('em').value})});")
    h.append("const j=await r.json();if(j.checkout_url)location.href=j.checkout_url;")
    h.append("else if(j.portal_url)location.href=j.portal_url;}</script></body></html>")
    return Response("".join(h), mimetype="text/html")

@app.route("/")
@app.route("/dashboard")
def web_dashboard():
    h = [
        "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Executive Matrix</title>",
        "<style>body{background:#070a12;color:#e2e8f0;font-family:Consolas,monospace;padding:16px;margin:0}",
        ".hdr{border:1px solid #10b981;padding:12px;display:flex;justify-content:space-between;color:#10b981;font-weight:bold;margin-bottom:12px}",
        ".grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}",
        ".card{background:#111827;border:1px solid #06b6d4;padding:10px;border-radius:6px}",
        ".val{font-size:20px;font-weight:bold;color:#38bdf8;margin-top:4px}",
        ".bar{background:#111827;border:1px solid #8b5cf6;padding:10px;margin-bottom:12px;display:flex;gap:8px;flex-wrap:wrap}",
        "button{background:#0284c7;color:#fff;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold}",
        "table{width:100%;border-collapse:collapse;background:#111827;border:1px solid #facc15;margin-bottom:12px}",
        "th,td{padding:7px;border-bottom:1px solid #1f2937;font-size:12px;text-align:left}th{color:#facc15}</style></head><body>",
        "<div class='hdr'><span>ORACLE SYSTEMS LLC // EXECUTIVE MATRIX</span>",
        "<div><a href='/store' target='_blank' style='color:#38bdf8;margin-right:12px'>Storefront (/store)</a>",
        "<a href='/portal' target='_blank' style='color:#34d399'>Portal (/portal)</a></div></div>",
        "<div class='bar'><button onclick=\"post('/api/task/submit',{task_name:'Job'})\">+ Job</button>",
        "<button style='background:#059669' onclick=\"post('/api/plugins/audit',{})\">Run Audits</button>",
        "<button style='background:#ec4899' onclick=\"ord('guide_52wk')\">+ $29 Order</button>",
        "<button style='background:#10b981' onclick=\"ord('pro_node')\">+ $99 Order</button>",
        "<button style='background:#6366f1' onclick=\"ord('enterprise_swarm')\">+ $1,500 Order</button>",
        "<button style='background:#7c3aed' onclick=\"post('/api/tasks/export-csv',{})\">Export CSV</button>",
        "<span id='msg' style='margin-left:auto;color:#34d399'>LIVE</span></div>",
        "<div class='grid'><div class='card'>Gross Revenue<div class='val' id='rev' style='color:#10b981'>$0.00</div></div>",
        "<div class='card'>Orders & AOV<div class='val' id='aov'>0</div></div>",
        "<div class='card'>CPU & RAM<div class='val' id='cpu'>--</div></div>",
        "<div class='card'>Mode<div class='val' id='rdy' style='font-size:13px;color:#facc15'>--</div></div></div>",
        "<table><thead><tr><th>ID</th><th>Customer</th><th>SKU</th><th>Amount</th><th>License / ZIP</th></tr></thead><tbody id='ob'></tbody></table>",
        "<div id='lb' style='background:#090d16;border:1px solid #06b6d4;padding:10px;white-space:pre-wrap;font-size:11px'></div>",
        "<script>const es=new EventSource('/api/stream');es.onmessage=e=>{const d=JSON.parse(e.data);",
        "document.getElementById('rev').innerText='$'+d.revenue.total_usd.toLocaleString('en-US',{minimumFractionDigits:2});",
        "document.getElementById('aov').innerText=d.revenue.transactions+' tx | $'+d.revenue.aov_usd;",
        "document.getElementById('cpu').innerText=d.cpu_pct+'% | '+d.ram_pct+'%';",
        "document.getElementById('rdy').innerText=d.readiness.stripe_live?'STRIPE: LIVE':'INSTANT FULFILLMENT';",
        "document.getElementById('ob').innerHTML=d.orders.map(o=>`<tr><td>${o.id}</td><td>${o.customer_email}</td><td>${o.product_sku}</td><td style='color:#10b981'>$${(o.amount_cents/100).toFixed(2)}</td><td><a style='color:#facc15' href='/portal?token=${o.download_token}' target='_blank'>${o.license_key}</a></td></tr>`).join('');",
        "document.getElementById('lb').innerText=d.logs.join('\\n');};",
        "async function post(u,b){const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});return await r.json();}",
        "async function ord(s){const j=await post('/api/billing/create-checkout',{sku:s,email:'Toomer1980@gmail.com'});if(j.order)document.getElementById('msg').innerText=j.order.license_key;}</script></body></html>"
    ]
    return Response("".join(h), mimetype="text/html")


@app.route("/api/order/lookup", methods=["GET"])
def api_lookup():
    import sqlite3 as _sq
    sid = (request.args.get("session_id") or "").strip()
    tok = (request.args.get("token") or "").strip()
    cache_p = "C:/Users/toome/Desktop/SovereignCore/data/verified_sessions.json"
    os.makedirs("C:/Users/toome/Desktop/SovereignCore/data", exist_ok=True)
    cache = json.load(open(cache_p, "r", encoding="utf-8")) if os.path.exists(cache_p) else {}

    # 1. Check token or license key locally first
    if tok:
        o = db.get_order_by_token(tok)
        if o: return jsonify({"status": "FOUND", "order": o}), 200
        for _k, _v in cache.items():
            if _v.get("download_token") == tok or _v.get("license_key") == tok:
                return jsonify({"status": "FOUND", "order": _v}), 200
        if tok.startswith("cs_"): sid = tok

    # 2. Check cached verified Stripe session_id
    if sid and sid in cache:
        return jsonify({"status": "FOUND", "order": cache[sid]}), 200

    # 3. Direct live Stripe API verification (webhook-independent instant fulfillment)
    if sid.startswith("cs_"):
        try:
            sk_live = json.load(open("C:/Users/toome/Desktop/SovereignCore/.stripe_env.json", encoding="utf-8")).get("STRIPE_SECRET_KEY", "").strip()
            stripe.api_key = sk_live
            sess = stripe.checkout.Session.retrieve(sid)
            pstat = getattr(sess, "payment_status", "") or (sess.get("payment_status") if isinstance(sess, dict) else "")
            sstat = getattr(sess, "status", "") or (sess.get("status") if isinstance(sess, dict) else "")
            if pstat in ("paid", "no_payment_required") or sstat == "complete":
                meta = dict(sess.metadata) if getattr(sess, "metadata", None) else {}
                amt_cents = int(getattr(sess, "amount_total", 0) or 4900)
                cd = getattr(sess, "customer_details", None)
                em = (getattr(cd, "email", None) if cd else None) or getattr(sess, "customer_email", None) or meta.get("email") or "Toomer1980@gmail.com"
                sku = meta.get("sku") or ("personal_3d_video" if amt_cents == 4900 else "pro_node")
                ev = {"id": sid, "amount_total": amt_cents, "customer_details": {"email": em}, "metadata": {"sku": sku, "email": em}}
                info = revenue_engine.process_successful_checkout(ev)
                if isinstance(info, dict):
                    info["session_id"] = sid
                    info["sku"] = sku
                    info["amount_cents"] = amt_cents
                    cache[sid] = info
                    json.dump(cache, open(cache_p, "w", encoding="utf-8"), indent=2)
                    try:
                        import sovereign_revenue_fulfillment as _srf
                        _srf.enqueue_paid_order(sid, sku, em, amt_cents / 100.0, meta)
                    except Exception: pass
                    return jsonify({"status": "FOUND", "order": info}), 200
        except Exception as e:
            return jsonify({"status": "ERROR", "error": str(e)}), 500
    return jsonify({"status": "NOT_FOUND"}), 404

@app.route("/api/order/deliverable-status", methods=["GET"])
def api_deliverable_status():
    import sqlite3 as _sq
    sid = (request.args.get("session_id") or "").strip()
    odb = "C:/Users/toome/Desktop/SovereignCore/data/fulfillment_queue.db"
    if sid and os.path.exists(odb):
        c = _sq.connect(odb, timeout=20.0)
        row = c.execute("SELECT status, download_url, sku FROM orders WHERE session_id=?", (sid,)).fetchone()
        c.close()
        if row:
            return jsonify({"status": row[0], "download_url": row[1], "sku": row[2]}), 200
    return jsonify({"status": "NONE", "download_url": ""}), 200

@app.route("/portal")
def portal_page():
    return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Oracle Systems // License Portal</title>
<style>body{background:#040610;color:#f8fafc;font-family:"Segoe UI",system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.box{width:540px;background:#090f20;border:1px solid #1e3a5f;border-radius:14px;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,.7)}
h2{margin:0 0 18px;color:#fff;font-size:22px}.row{display:flex;gap:8px}
input{flex:1;background:#0f172a;border:1px solid #38bdf8;color:#fff;padding:11px 13px;border-radius:8px;font-size:14px}
button,.btn{background:#10b981;color:#fff;border:none;padding:11px 18px;border-radius:8px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block;font-size:14px}
.btn-gold{background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#0b0f19;margin-top:10px}
.meta{margin-top:18px;font-family:Consolas,monospace;line-height:1.7;font-size:14px}.ok{color:#10b981;font-weight:700}.key{color:#fbbf24;font-weight:700}
.links{margin-top:18px;font-size:13px}.links a{color:#38bdf8;margin-right:12px}</style></head><body><div class="box">
<h2>Oracle Systems // Customer Fulfillment Portal</h2>
<div class="row"><input id="q" placeholder="Token, License Key, or Stripe Session ID"><button onclick="lookup()">Verify</button></div>
<div id="out" class="meta">Checking order...</div>
<div class="links"><a href="/store">&larr; Storefront</a><a href="/personalize">3D Sanctuary</a><a href="/dashboard">Executive Matrix</a></div>
</div><script>
const qs=new URLSearchParams(location.search), initSid=qs.get("session_id")||"", initTok=qs.get("token")||"";
document.getElementById("q").value=initTok||initSid;
async function pollVideo(sid){
  const el=document.getElementById("vid-slot"); if(!el||!sid) return;
  const r=await(await fetch("/api/order/deliverable-status?session_id="+encodeURIComponent(sid))).json();
  if(r.status==="COMPLETED"&&r.download_url&&r.download_url.endsWith(".mp4")){
    el.innerHTML='<a class="btn btn-gold" href="'+r.download_url+'" download>Download Custom 3D Reading (.MP4)</a>';
  } else if(r.sku==="personal_3d_video"||r.status==="PENDING"){
    el.innerHTML='<div style="color:#38bdf8;margin-top:10px">Rendering your custom 3D Reading MP4... auto-refreshing.</div>';
    setTimeout(()=>pollVideo(sid),5000);
  }
}
async function lookup(){
  const val=document.getElementById("q").value.trim(), out=document.getElementById("out");
  if(!val){out.textContent="Enter your token or session ID.";return;}
  out.textContent="Verifying payment with Oracle Systems & Stripe...";
  const param=val.startsWith("cs_")?"session_id="+encodeURIComponent(val):"token="+encodeURIComponent(val);
  const res=await fetch("/api/order/lookup?"+param); const d=await res.json();
  if(res.ok&&d.order){
    const o=d.order, amt=((o.amount_cents||4900)/100).toFixed(2);
    out.innerHTML='<div class="ok">VERIFIED LIVE LICENSE</div>'+
      '<div>Product: '+(o.product_name||o.sku)+'</div>'+
      '<div>License Key: <span class="key">'+o.license_key+'</span></div>'+
      '<div>Download Token: '+o.download_token+'</div>'+
      '<div>Amount Paid: $'+amt+'</div>'+
      '<div style="margin-top:14px"><a class="btn" href="/api/download/secure-asset?token='+encodeURIComponent(o.download_token)+'">Download Digital Bundle (.ZIP)</a></div>'+
      '<div id="vid-slot"></div>';
    if(o.session_id&&o.session_id.startsWith("cs_")) pollVideo(o.session_id);
  } else { out.textContent=d.error||"Not found"; }
}
if(initSid||initTok) lookup(); else document.getElementById("out").textContent="Enter a token or license key above.";
</script></body></html>"""

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 8000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p, debug=False, use_reloader=False, threaded=True), daemon=True).start()
    while True:
        swarm.enqueue_task("Heartbeat", lambda *a: None)
        time.sleep(60)
