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
    return bool(k and k.startswith("sk_live_") and "YOUR_" not in k)

def get_readiness():
    sk = vault.get_secret("STRIPE_SECRET_KEY") or ""
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

@app.route("/api/billing/create-checkout", methods=["POST"])
def api_checkout():
    d = request.get_json(force=True, silent=True) or {}
    sku = d.get("sku", "pro_node")
    em = (d.get("email") or "client@oraclesystems.io").strip()
    pr = revenue_engine.CATALOG.get(sku, revenue_engine.CATALOG["pro_node"])
    sk = vault.get_secret("STRIPE_SECRET_KEY") or ""
    if not is_real_key(sk):
        ev = {"id": f"ord_{int(time.time())}", "amount_total": pr["price_cents"],
              "customer_details": {"email": em}, "metadata": {"sku": sku, "email": em}}
        info = revenue_engine.process_successful_checkout(ev)
        return jsonify({"status": "FULFILLED", "order": info,
                        "portal_url": f"/portal?token={info['download_token']}"}), 200
    stripe.api_key = sk
    bu = request.host_url.rstrip("/")
    s = stripe.checkout.Session.create(
        payment_method_types=["card"], customer_email=em, mode="payment",
        line_items=[{"price_data": {"currency": "usd", "unit_amount": pr["price_cents"],
                     "product_data": {"name": pr["name"]}}, "quantity": 1}],
        metadata={"sku": sku, "email": em},
        success_url=f"{bu}/portal?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{bu}/store"
    )
    return jsonify({"status": "REDIRECT", "checkout_url": s.url}), 200

@app.route("/api/order/lookup")
def api_lookup():
    o = db.get_order_by_token((request.args.get("token") or "").strip())
    return (jsonify({"status": "FOUND", "order": o}), 200) if o else (jsonify({}), 404)

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

@app.route("/portal")
def web_portal():
    h = [
        "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>License Portal</title>",
        "<style>body{background:#060911;color:#fff;font-family:sans-serif;padding:40px}",
        ".box{max-width:600px;margin:0 auto;background:#111827;border:1px solid #10b981;padding:28px;border-radius:8px}",
        "input{background:#090d16;color:#fff;border:1px solid #38bdf8;padding:10px;width:68%}",
        "button,.btn{background:#059669;color:#fff;padding:10px 16px;border:none;border-radius:6px;text-decoration:none;display:inline-block;margin-top:12px;font-weight:bold}</style></head><body>",
        "<div class='box'><h2>Oracle Systems // Customer Fulfillment Portal</h2>",
        "<input id='t' placeholder='Token or License Key'/> <button onclick='lk()'>Verify</button>",
        "<div id='out' style='margin-top:18px;font-family:monospace;line-height:1.8'></div>",
        "<p><a href='/store' style='color:#38bdf8'>&larr; Storefront</a> | <a href='/dashboard' style='color:#38bdf8'>Executive Matrix</a></p></div>",
        "<script>async function lk(){const v=document.getElementById('t').value.trim();",
        "const r=await fetch('/api/order/lookup?token='+encodeURIComponent(v));",
        "if(r.status!==200){document.getElementById('out').innerText='Not found';return;}",
        "const o=(await r.json()).order;",
        "document.getElementById('out').innerHTML=`<b style='color:#34d399'>VERIFIED LICENSE</b><br>Product: ${o.product_name}<br>Key: <b style='color:#facc15'>${o.license_key}</b><br>Amount: $${(o.amount_cents/100).toFixed(2)}<br><a class='btn' href='/api/download/secure-asset?token=${o.download_token}'>Download Digital Bundle (.ZIP)</a>`;}",
        "const q=new URLSearchParams(location.search).get('token');if(q){document.getElementById('t').value=q;lk();}</script></body></html>"
    ]
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

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 8000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p, debug=False, use_reloader=False, threaded=True), daemon=True).start()
    while True:
        swarm.enqueue_task("Heartbeat", lambda *a: None)
        time.sleep(60)
