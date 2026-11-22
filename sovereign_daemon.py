import re
import sovereign_order_verifier
import os as _os_path_mod
_BASE_DIR = _os_path_mod.path.dirname(_os_path_mod.path.abspath(__file__)).replace("\\", "/")
import os, json, stripe
if os.path.exists(".stripe_env.json"):
    for _k, _v in json.load(open(".stripe_env.json", encoding="utf-8")).items():
        if isinstance(_v, str) and (_v.startswith("sk_") or _v.startswith("rk_")):
            os.environ["STRIPE_SECRET_KEY"] = _v.strip()
            stripe.api_key = _v.strip()

import os, sys, json, time, logging, threading
import psutil, stripe
from flask import Flask, request, jsonify, Response, send_file

BASE = _BASE_DIR
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
    sk_live = (os.environ.get("STRIPE_SECRET_KEY") or (json.load(open(_BASE_DIR + "/.stripe_env.json", encoding="utf-8")).get("STRIPE_SECRET_KEY", "") if os.path.exists(_BASE_DIR + "/.stripe_env.json") else "")).strip()
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
    return open((_BASE_DIR + "/templates/oracle_3d_stage.html"), "r", encoding="utf-8").read()

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
        pdir = (_BASE_DIR + "/static/portraits")
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
    audio_file = f(_BASE_DIR + "/static/portraits/r_{rid}.mp3")
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
    p = (_BASE_DIR + "/VOICE_CONFIG.json")
    cfg = json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else {"mode": "neural", "custom_sample": (_BASE_DIR + "/voice_samples/thomas_voice.wav")}
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
    vdir = (_BASE_DIR + "/voice_samples")
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
    import logging, traceback
    t = (request.args.get("token") or "").strip()
    if not t:
        return jsonify({"error": "Missing token"}), 400
    o = None
    try:
        o = db.get_order_by_token(t)
    except Exception as e:
        logging.error(f"[api_dl] db lookup failed: {e}")
    if not o:
        try:
            o = sovereign_order_verifier.lookup_cached(t)
        except Exception as e:
            logging.error(f"[api_dl] verifier lookup failed: {e}")
    if not o:
        return jsonify({"error": "Invalid token"}), 403
    try:
        info = {
            "session_id": o.get("session_id") or "",
            "email": o.get("customer_email") or "",
            "amount_cents": o.get("amount_cents") or 0,
            "sku": o.get("product_sku") or "pro_node",
            "product_name": o.get("product_name") or "Oracle Bundle",
            "license_key": o.get("license_key") or "ORCL-PRO",
            "download_token": o.get("download_token") or t,
        }
        zp = revenue_engine.build_customer_bundle(info)
        return send_file(zp, as_attachment=True, download_name=f"Oracle_{info['license_key']}.zip")
    except Exception as e:
        logging.error(f"[api_dl] bundle build failed: {e} | {traceback.format_exc()}")
        return jsonify({"error": f"Bundle generation failed: {str(e)}"}), 500

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
        pr = f"${p.get('price_cents', 0)/100:,.2f}"
        h.append(f"<div class='card'><small style='color:#34d399'>{p.get('badge', 'ORACLE SYSTEMS')}</small>")
        h.append(f"<h3>{p.get('name', k.upper())}</h3><div class='pr'>{pr}</div><p>{p.get('desc', 'Instant automated fulfillment.')}</p>")
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
        "<button style='background:#10b981' onclick=\"ord('pro_node')\">+ $49,999 Order</button>",
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
    q = (request.args.get("session_id") or request.args.get("token") or "").strip()
    if not q: return jsonify({"status": "NOT_FOUND"}), 404
    o = sovereign_order_verifier.lookup_cached(q)
    if not o and q.startswith("cs_"):
        try: o = sovereign_order_verifier.unlock_session(q)
        except Exception as e: return jsonify({"status": "ERROR", "error": str(e)}), 500
    if not o:
        sovereign_order_verifier.sync_recent_stripe_sales()
        o = sovereign_order_verifier.lookup_cached(q)
    return (jsonify({"status": "FOUND", "order": o}), 200) if o else (jsonify({"status": "NOT_FOUND"}), 404)

@app.route("/api/order/deliverable-status", methods=["GET"])
def api_deliverable_status():
    import sqlite3 as _sq
    base = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    sid = (request.args.get("session_id") or "").strip()
    odb = base + "/data/fulfillment_queue.db"
    if sid and os.path.exists(odb):
        c = _sq.connect(odb, timeout=20.0)
        row = c.execute("SELECT status, download_url, sku FROM orders WHERE session_id=?", (sid,)).fetchone()
        c.close()
        if row: return jsonify({"status": row[0], "download_url": row[1], "sku": row[2]}), 200
    return jsonify({"status": "NONE", "download_url": ""}), 200

@app.route("/portal")
def portal_page():
    return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Oracle Systems // License Portal</title>
<style>body{background:#040610;color:#f8fafc;font-family:"Segoe UI",system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.box{width:560px;background:#090f20;border:1px solid #1e3a5f;border-radius:14px;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,.7)}
h2{margin:0 0 16px;color:#fff;font-size:21px}.row{display:flex;gap:8px}
input{flex:1;background:#0f172a;border:1px solid #38bdf8;color:#fff;padding:11px;border-radius:8px;font-size:14px}
button,.btn{background:#10b981;color:#fff;border:none;padding:11px 18px;border-radius:8px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block;font-size:14px}
.btn-gold{background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#0b0f19;margin-top:10px}
.meta{margin-top:18px;font-family:Consolas,monospace;line-height:1.7;font-size:13.5px}.ok{color:#10b981;font-weight:700}.key{color:#fbbf24;font-weight:700}
.links{margin-top:18px;font-size:13px}.links a{color:#38bdf8;margin-right:12px}</style></head><body><div class="box">
<h2>Oracle Systems // Customer Fulfillment Portal</h2>
<div class="row"><input id="q" placeholder="Receipt (2352-8553), Invoice (CPHAMCTV-0001), Token, or Session ID"><button onclick="lookup()">Verify</button></div>
<div id="out" class="meta">Checking order...</div>
<div class="links"><a href="/store">&larr; Storefront</a><a href="/personalize">3D Sanctuary</a><a href="/dashboard">Executive Matrix</a></div>
</div><script>
const qs=new URLSearchParams(location.search), initQ=qs.get("session_id")||qs.get("token")||"";
document.getElementById("q").value=initQ;
async function pollVideo(sid){
  const el=document.getElementById("vid-slot"); if(!el||!sid) return;
  const r=await(await fetch("/api/order/deliverable-status?session_id="+encodeURIComponent(sid))).json();
  if(r.status==="COMPLETED"&&r.download_url&&r.download_url.endsWith(".mp4")){
    el.innerHTML='<a class="btn btn-gold" href="'+r.download_url+'" download>Download Custom 3D Reading (.MP4)</a>';
  } else if(r.sku==="personal_3d_video"||r.status==="PENDING"){
    el.innerHTML='<div style="color:#38bdf8;margin-top:10px">Rendering custom 3D Reading MP4... auto-refreshing.</div>';
    setTimeout(()=>pollVideo(sid),5000);
  }
}
async function lookup(){
  const val=document.getElementById("q").value.trim(), out=document.getElementById("out");
  if(!val){out.textContent="Enter a receipt, invoice, token, or session ID.";return;}
  const param=val.startsWith("cs_")?"session_id="+encodeURIComponent(val):"token="+encodeURIComponent(val);
  const res=await fetch("/api/order/lookup?"+param); const d=await res.json();
  if(res.ok&&d.order){
    const o=d.order, amt=((o.amount_cents||4900)/100).toFixed(2);
    out.innerHTML='<div class="ok">VERIFIED PAID ORDER // '+(o.invoice_number||'')+' '+(o.receipt_number?'(Receipt '+o.receipt_number+')':'')+'</div>'+
      '<div>Product: '+(o.product_name||o.sku)+'</div>'+
      '<div>License Key: <span class="key">'+o.license_key+'</span></div>'+
      '<div>Download Token: '+o.download_token+'</div>'+
      '<div>Amount Paid: $'+amt+'</div>'+
      '<div style="margin-top:14px"><a class="btn" href="/api/download/secure-asset?token='+encodeURIComponent(o.download_token)+'">Download Digital Bundle (.ZIP)</a></div>'+
      '<div id="vid-slot"></div>';
    if(o.session_id&&o.session_id.startsWith("cs_")) pollVideo(o.session_id);
  } else { out.textContent=d.error||"Not found"; }
}
if(initQ) lookup(); else document.getElementById("out").textContent="Enter a receipt, invoice, or license key above.";
</script></body></html>"""


# === ORACLE_UTM_AND_STRIPE_HOOK_START ===
def _oracle_init_utm_db():
    import os as _os, sqlite3 as _sq
    _dbp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "data", "utm_analytics.db")
    _os.makedirs(_os.path.dirname(_dbp), exist_ok=True)
    _c = _sq.connect(_dbp)
    _c.execute(
        "CREATE TABLE IF NOT EXISTS utm_clicks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "ts_utc TEXT, tier TEXT, utm_source TEXT, utm_medium TEXT, "
        "utm_campaign TEXT, utm_content TEXT, referrer TEXT, ip TEXT)"
    )
    _c.commit()
    _c.close()
    return _dbp

_ORACLE_STRIPE_LINKS = {
    "tier29": "https://buy.stripe.com/bJefZheeldrj1OU8YBcQU01",
    "auravideo49": "https://buy.stripe.com/6oU28rb29evn8di7UxcQU00",
    "tier1500": "https://buy.stripe.com/6oUeVdgmtcnf1OU7UxcQU02",
    "fullstorefront": "https://buy.stripe.com/28E9AT6LT0Ex79e7UxcQU03",
    "pro_node": "https://buy.stripe.com/aFa4gzgmt9b379efmZcQU04",
}

@app.route("/go/<tier>")
def oracle_utm_redirect(tier):
    import datetime as _dt, sqlite3 as _sq
    from flask import redirect as _redirect
    key = (tier or "").strip().lower()
    dest = _ORACLE_STRIPE_LINKS.get(key) or _ORACLE_STRIPE_LINKS["fullstorefront"]
    try:
        _dbp = _oracle_init_utm_db()
        _c = _sq.connect(_dbp)
        _c.execute(
            "INSERT INTO utm_clicks (ts_utc, tier, utm_source, utm_medium, utm_campaign, utm_content, referrer, ip) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                _dt.datetime.utcnow().isoformat() + "Z",
                key,
                (request.args.get("utm_source") or "direct").strip()[:80],
                (request.args.get("utm_medium") or "organic").strip()[:80],
                (request.args.get("utm_campaign") or "none").strip()[:120],
                (request.args.get("utm_content") or "none").strip()[:120],
                (request.referrer or "")[:200],
                (request.remote_addr or "")[:64],
            ),
        )
        _c.commit()
        _c.close()
    except Exception:
        pass
    return _redirect(dest, code=302)

@app.route("/api/analytics/utm")
def oracle_utm_analytics():
    import sqlite3 as _sq
    _dbp = _oracle_init_utm_db()
    _c = _sq.connect(_dbp)
    total = _c.execute("SELECT COUNT(*) FROM utm_clicks").fetchone()[0]
    by_tier = [{"tier": r[0], "clicks": r[1]} for r in _c.execute(
        "SELECT tier, COUNT(*) FROM utm_clicks GROUP BY tier ORDER BY COUNT(*) DESC"
    ).fetchall()]
    top_campaigns = [{"campaign": r[0], "source": r[1], "medium": r[2], "clicks": r[3]} for r in _c.execute(
        "SELECT utm_campaign, utm_source, utm_medium, COUNT(*) FROM utm_clicks "
        "GROUP BY utm_campaign, utm_source, utm_medium ORDER BY COUNT(*) DESC LIMIT 20"
    ).fetchall()]
    _c.close()
    return jsonify({"total_clicks": total, "by_tier": by_tier, "top_campaigns": top_campaigns}), 200

@app.after_request
def _oracle_inject_store_router(resp):
    try:
        if request.path == "/store" and resp.status_code == 200 and "text/html" in (resp.content_type or ""):
            body = resp.get_data(as_text=True)
            if "oracle-stripe-store-router" not in body and "</body>" in body.lower():
                js = (
                    '<script id="oracle-stripe-store-router">'
                    'document.addEventListener("click",function(e){'
                    'var b=e.target.closest("button,a");if(!b)return;'
                    'var t=(b.textContent||"").toUpperCase();var u=null;'
                    'if(t.indexOf("49,999")>=0||t.indexOf("49999")>=0||t.indexOf("PRO_NODE")>=0||t.indexOf("PRO NODE")>=0)u="/go/pro_node?utm_source=store&utm_medium=cta";'
                    'else if(t.indexOf("1,500")>=0||t.indexOf("1500")>=0)u="/go/tier1500?utm_source=store&utm_medium=cta";'
                    'else if(t.indexOf("FULL STOREFRONT")>=0)u="/go/fullstorefront?utm_source=store&utm_medium=cta";'
                    'else if(t.indexOf("$49")>=0||t.indexOf("AURA")>=0)u="/go/auravideo49?utm_source=store&utm_medium=cta";'
                    'else if(t.indexOf("$29")>=0)u="/go/tier29?utm_source=store&utm_medium=cta";'
                    'if(u){e.preventDefault();e.stopImmediatePropagation();window.open(u,"_blank","noopener,noreferrer");}'
                    '},true);</script></body>'
                )
                body = re.sub(r'</body>', js, body, count=1, flags=re.IGNORECASE)
                resp.set_data(body)
    except Exception:
        pass
    return resp
# === ORACLE_UTM_AND_STRIPE_HOOK_END ===





































# === ORACLE_4D_STOREFRONT_HOOK_START ===
@app.before_request
def _oracle_webgl_v19_router():
    try:
        from flask import request as _req, redirect as _redir, jsonify as _jfy, send_from_directory as _sfd, Response as _Resp
        import json as _j, os as _o, sqlite3 as _sq, datetime as _dt
        base_dir = _o.path.dirname(_o.path.abspath(__file__))
        if _req.path == "/store":
            html_p = _o.path.join(base_dir, "static", "oracle_webgl_store.html")
            if _o.path.exists(html_p):
                return _Resp(open(html_p, "r", encoding="utf-8").read(), mimetype="text/html")
        if _req.path.startswith("/assets/tarot_deck/"):
            return _sfd(_o.path.join(base_dir, "assets", "tarot_deck"), _req.path.rsplit("/", 1)[-1])
        if _req.path.startswith("/static/vendor/"):
            return _sfd(_o.path.join(base_dir, "static", "vendor"), _req.path.rsplit("/", 1)[-1], mimetype="application/javascript")
        if _req.path.startswith("/static/card_voices/"):
            return _sfd(_o.path.join(base_dir, "static", "card_voices"), _req.path.rsplit("/", 1)[-1], mimetype="audio/mpeg")
        if _req.path == "/api/deck-manifest":
            mp = _o.path.join(base_dir, "data", "verified_deck_manifest.json")
            return _jfy(_j.load(open(mp, "r", encoding="utf-8")) if _o.path.exists(mp) else [])
        if _req.path == "/api/live-pulse":
            clicks, views = 0, 0
            udb = _o.path.join(base_dir, "data", "utm_analytics.db")
            if _o.path.exists(udb):
                try:
                    c = _sq.connect(udb); clicks = int(c.execute("SELECT COUNT(*) FROM utm_clicks").fetchone()[0]); c.close()
                except Exception: pass
            ya = _o.path.join(base_dir, "data", "youtube_analytics.json")
            if _o.path.exists(ya):
                try: views = int((_j.load(open(ya, "r", encoding="utf-8")).get("totals") or {}).get("views", 0))
                except Exception: pass
            return _jfy({"vault_videos": 104, "utm_clicks": clicks, "yt_views": views, "status": "LIVE"})
        if _req.path in ("/go/assetpack15", "/go/vaultsub15"):
            tier_key = _req.path.rsplit("/", 1)[-1]
            tpath = _o.path.join(base_dir, "config", "stripe_new_tiers.json")
            target = "https://buy.stripe.com/eVq6oHgmt0Ex1OUfmZcQU05" if tier_key == "assetpack15" else "https://buy.stripe.com/aFa3cv3zH1IB65adeRcQU06"
            if _o.path.exists(tpath):
                td = _j.load(open(tpath, "r", encoding="utf-8"))
                if td.get(tier_key): target = td[tier_key]
            udb = _o.path.join(base_dir, "data", "utm_analytics.db")
            if _o.path.exists(udb):
                try:
                    c = _sq.connect(udb)
                    cols = [r[1] for r in c.execute("PRAGMA table_info(utm_clicks)").fetchall()]
                    vals_map = {
                        "tier": tier_key, "utm_source": _req.args.get("utm_source", "webgl_store"),
                        "utm_medium": _req.args.get("utm_medium", "card"), "utm_campaign": _req.args.get("utm_campaign", "v19"),
                        "target_url": target, "ip": _req.remote_addr or "",
                        "user_agent": (_req.headers.get("User-Agent") or "")[:200],
                        "timestamp_utc": _dt.datetime.utcnow().isoformat() + "Z",
                        "created_utc": _dt.datetime.utcnow().isoformat() + "Z",
                        "clicked_at": _dt.datetime.utcnow().isoformat() + "Z",
                    }
                    use_cols = [col for col in cols if col in vals_map]
                    if use_cols:
                        q = "INSERT INTO utm_clicks (" + ",".join(use_cols) + ") VALUES (" + ",".join(["?"] * len(use_cols)) + ")"
                        c.execute(q, [vals_map[col] for col in use_cols]); c.commit()
                    c.close()
                except Exception: pass
            return _redir(target, code=302)
    except Exception: pass


@app.after_request
def _oracle_portal_upsell_v19(resp):
    try:
        from flask import request as _req
        import re as _re
        if resp.status_code == 200 and "text/html" in (resp.content_type or "").lower() and _req.path == "/portal":
            body = resp.get_data(as_text=True)
            if "oracle-portal-upsell" not in body and "</body>" in body.lower():
                banner = (
                    '<div id="oracle-portal-upsell" style="max-width:820px;margin:24px auto;padding:24px;'
                    'background:linear-gradient(135deg,#070d1f,#111827);border:1.5px solid #f59e0b;border-radius:14px;'
                    'font-family:sans-serif;color:#f8fafc;text-align:center;">'
                    '<div style="color:#38bdf8;font-size:12px;letter-spacing:2px;font-weight:bold;">VERIFIED MEMBER ASCENSION // ORACLE SYSTEMS LLC</div>'
                    '<h3 style="margin:8px 0;color:#facc15;">Scale Your Stack: $15/mo Vault, $1,500 Full Bundle, or Dedicated Pro_Node</h3>'
                    '<a href="/go/vaultsub15?utm_source=portal_upsell&utm_medium=banner&utm_campaign=v19" target="_blank" style="display:inline-block;margin:6px;padding:10px 16px;background:#f59e0b;color:#050814;text-decoration:none;border-radius:7px;font-weight:bold;">Join 4D Vault ($15/mo)</a>'
                    '<a href="/go/fullstorefront?utm_source=portal_upsell&utm_medium=banner&utm_campaign=v19" target="_blank" style="display:inline-block;margin:6px;padding:10px 16px;background:#059669;color:#fff;text-decoration:none;border-radius:7px;font-weight:bold;">Full Storefront ($1,500)</a>'
                    '<a href="/go/pro_node?utm_source=portal_upsell&utm_medium=banner&utm_campaign=v19" target="_blank" style="display:inline-block;margin:6px;padding:10px 16px;background:#0284c7;color:#fff;text-decoration:none;border-radius:7px;font-weight:bold;">Pro_Node ($49,999)</a>'
                    '</div></body>'
                )
                resp.set_data(_re.sub(r'</body>', banner, body, count=1, flags=_re.IGNORECASE))
    except Exception: pass
    return resp
# === ORACLE_4D_STOREFRONT_HOOK_END ===

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 8000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p, debug=False, use_reloader=False, threaded=True), daemon=True).start()
    while True:
        swarm.enqueue_task("Heartbeat", lambda *a: None)
        time.sleep(60)
