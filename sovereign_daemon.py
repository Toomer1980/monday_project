import os, sys, json, time, logging, threading
import psutil, stripe
from flask import Flask, request, jsonify, Response

BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "modules"))
import db, export_report, plugins, vault, stripe_sync
from task_engine import swarm

LOG_PATH = os.path.join(BASE_DIR, "logs", "daemon.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask("SovereignGateway")

def build_snapshot():
    vmem = psutil.virtual_memory()
    root_p = "C:\\" if os.name == "nt" else "/"
    disk = psutil.disk_usage(root_p)
    logs = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                logs = [l.strip() for l in f if l.strip()][-6:]
        except Exception:
            pass
    return {
        "cpu_pct": psutil.cpu_percent(interval=None),
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_pct": vmem.percent,
        "ram_used_gb": round(vmem.used / (1024**3), 2),
        "disk_pct": disk.percent,
        "queue_depth": swarm.task_queue.qsize(),
        "vault_keys": vault.list_secret_keys(),
        "revenue": db.get_revenue_summary(),
        "tasks": db.get_recent_tasks(6),
        "logs": logs
    }

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "HEALTHY", "workers": 4}), 200

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({"status": "ONLINE", "subsystem": "SovereignCore", "revenue": db.get_revenue_summary()}), 200

@app.route("/api/stream", methods=["GET"])
def api_stream():
    def gen():
        while True:
            yield f"data: {json.dumps(build_snapshot())}\n\n"
            time.sleep(1.5)
    return Response(gen(), mimetype="text/event-stream")

@app.route("/api/task/submit", methods=["POST"])
def api_submit():
    d = request.get_json(force=True, silent=True) or {}
    tid = swarm.enqueue_task(d.get("task_name", "WebUI-Job"), lambda *a: time.sleep(0.4))
    return jsonify({"status": "QUEUED", "task_id": tid}), 202

@app.route("/api/tasks/purge", methods=["POST"])
def api_purge():
    return jsonify({"status": "PURGED", "purged_count": swarm.purge_queue()}), 200

@app.route("/api/tasks/export-csv", methods=["POST"])
def api_export():
    return jsonify({"status": "EXPORTED", "report_path": export_report.generate_csv_report()}), 200

@app.route("/api/plugins/audit", methods=["POST"])
def api_audits():
    ids = [
        swarm.enqueue_task("Plugin-DiskCleanup", plugins.audit_disk_cleanup),
        swarm.enqueue_task("Plugin-LogRotation", plugins.audit_log_rotation),
        swarm.enqueue_task("Plugin-NetLatency", plugins.audit_network_latency),
        swarm.enqueue_task("Plugin-GitSync", plugins.audit_git_sync)
    ]
    return jsonify({"status": "QUEUED", "queued_plugins": ids}), 202

@app.route("/api/vault/set", methods=["POST"])
def api_vault_set():
    d = request.get_json(force=True, silent=True) or {}
    vault.set_secret(d.get("key"), d.get("value"))
    return jsonify({"status": "ENCRYPTED", "vault_keys": vault.list_secret_keys()}), 200

@app.route("/api/billing/register-webhook", methods=["POST"])
def api_reg_wh():
    d = request.get_json(force=True, silent=True) or {}
    try:
        res = stripe_sync.register_cloud_webhook(d.get("cloud_url"), d.get("stripe_key"))
        return jsonify({"status": "REGISTERED", "details": res}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 400

@app.route("/api/billing/create-checkout", methods=["POST"])
def api_checkout():
    d = request.get_json(force=True, silent=True) or {}
    amt = int(d.get("amount", 1500))
    s_key = vault.get_secret("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock")
    if "mock" in s_key:
        fid = f"cs_sim_{int(time.time())}"
        db.record_revenue(fid, "buyer@sovereigncore.io", amt, "PAID")
        swarm.enqueue_task("Provision-License-Sim", lambda *a: logging.info(f"[REVENUE] Simulated ${amt/100} license activated."))
        return jsonify({"status": "SIMULATED", "session_id": fid}), 200
    try:
        stripe.api_key = s_key
        base_u = request.host_url.rstrip("/")
        sess = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "unit_amount": amt, "product_data": {"name": "SovereignCore Compute License"}}, "quantity": 1}],
            mode="payment",
            success_url=f"{base_u}/dashboard?payment=success",
            cancel_url=f"{base_u}/dashboard?payment=cancelled"
        )
        return jsonify({"status": "SUCCESS", "checkout_url": sess.url}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500

@app.route("/api/billing/stripe-webhook", methods=["POST"])
def api_stripe_wh():
    payload = request.data
    sig = request.headers.get("Stripe-Signature", "")
    wh_sec = vault.get_secret("STRIPE_WEBHOOK_SECRET") or os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    try:
        ev = stripe.Webhook.construct_event(payload, sig, wh_sec) if wh_sec and "mock" not in wh_sec else json.loads(payload)
    except Exception:
        return "Invalid signature", 400
    if ev.get("type") == "checkout.session.completed":
        obj = ev.get("data", {}).get("object", {})
        email = obj.get("customer_details", {}).get("email", "cloud@sovereigncore.io")
        total = obj.get("amount_total", 1500)
        db.record_revenue(obj.get("id", "evt"), email, total, "PAID")
        swarm.enqueue_task("Provision-Cloud-License", lambda *a: logging.info(f"[WEBHOOK] License provisioned for {email}"))
    return jsonify({"status": "RECEIVED"}), 200

@app.route("/", methods=["GET"])
@app.route("/dashboard", methods=["GET"])
def web_dashboard():
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>SovereignCore // Live Cloud Matrix</title>
<style>
body{background:#0b0f19;color:#e2e8f0;font-family:Consolas,monospace;margin:0;padding:20px;}
.header{border:1px solid #10b981;background:#064e3b33;padding:14px;display:flex;justify-content:space-between;color:#10b981;font-weight:bold;border-radius:6px;margin-bottom:14px;}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px;}
.card{background:#111827;border:1px solid #06b6d4;border-radius:6px;padding:12px;}
.card h3{margin:0 0 6px 0;color:#facc15;font-size:12px;text-transform:uppercase;}
.val{font-size:20px;font-weight:bold;color:#38bdf8;}
.bar{background:#111827;border:1px solid #8b5cf6;border-radius:6px;padding:10px 14px;margin-bottom:14px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;}
input{background:#090d16;border:1px solid #374151;color:#38bdf8;padding:7px 10px;border-radius:4px;font-family:inherit;}
button{background:#0284c7;color:#fff;border:none;padding:8px 14px;border-radius:4px;font-family:inherit;font-weight:bold;cursor:pointer;}
table{width:100%;border-collapse:collapse;background:#111827;border:1px solid #facc15;margin-bottom:14px;}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #1f2937;font-size:12px;}th{color:#facc15;background:#1e293b;}
.logs{background:#090d16;border:1px solid #06b6d4;padding:12px;border-radius:6px;font-size:12px;color:#a7f3d0;white-space:pre-wrap;}
.pill{background:#1e1b4b;border:1px solid #8b5cf6;color:#c4b5fd;padding:2px 8px;border-radius:4px;font-size:11px;}
</style></head><body>
<div class="header"><span>M.O.N.D.A.Y. SOVEREIGNCORE // DUAL-CLOUD & REVENUE MATRIX</span><span>SSE: LIVE | WATCHDOG: ARMED</span></div>
<div class="bar">
<button onclick="post(\"/api/task/submit\",{task_name:\"Compute-Job\"})">+ Dispatch Job</button>
<button style="background:#059669" onclick="post(\"/api/plugins/audit\",{})">Run 4 Audits</button>
<button style="background:#ec4899" onclick="pay()">Simulate/Run Stripe Checkout ($15)</button>
<button style="background:#d97706" onclick="post(\"/api/tasks/purge\",{})">Purge Queue</button>
<button style="background:#7c3aed" onclick="post(\"/api/tasks/export-csv\",{})">Export CSV</button>
<span id="msg" style="margin-left:auto;color:#38bdf8;font-size:12px;">Ready</span>
</div>
<div class="grid">
<div class="card"><h3>CPU Load</h3><div class="val" id="cpu">--%</div></div>
<div class="card"><h3>Memory</h3><div class="val" id="ram">--%</div></div>
<div class="card"><h3>Disk & Queue</h3><div class="val" id="dsk">--%</div></div>
<div class="card"><h3>Stripe Revenue</h3><div class="val" id="rev" style="color:#10b981;">$0.00</div></div>
</div>
<div class="bar">
<strong style="color:#c4b5fd;font-size:12px;">VAULT & WEBHOOK AUTO-LINKER:</strong>
<input id="vk" placeholder="Key (STRIPE_SECRET_KEY)" />
<input id="vv" type="password" placeholder="Secret Value" />
<button style="background:#7c3aed" onclick="saveSec()">Encrypt Secret</button>
<input id="whu" placeholder="https://your-cloud-url.onrender.com" style="width:240px;" />
<button style="background:#059669" onclick="regWh()">Auto-Link Stripe Webhook</button>
<div id="pills" style="display:flex;gap:5px;flex-wrap:wrap;"></div>
</div>
<table><thead><tr><th>ID</th><th>Task Name</th><th>Status</th><th>Runtime</th><th>Queued At</th></tr></thead><tbody id="tb"></tbody></table>
<div class="logs" id="lb">Connecting live telemetry stream...</div>
<script>
const es = new EventSource("/api/stream");
es.onmessage = e => {
  const d = JSON.parse(e.data);
  document.getElementById("cpu").innerText = d.cpu_pct + "% (" + d.cpu_cores + "C)";
  document.getElementById("ram").innerText = d.ram_pct + "% (" + d.ram_used_gb + "GB)";
  document.getElementById("dsk").innerText = d.disk_pct + "% | Q:" + d.queue_depth;
  document.getElementById("rev").innerText = "$" + d.revenue.total_usd + " (" + d.revenue.transactions + " tx)";
  document.getElementById("pills").innerHTML = d.vault_keys.map(k => `<span class="pill">${k}</span>`).join("");
  document.getElementById("tb").innerHTML = d.tasks.map(t => `<tr><td>${t.id}</td><td style="color:#38bdf8;font-weight:bold;">${t.task_name}</td><td>${t.status}</td><td>${t.duration_sec!==null?t.duration_sec+"s":"-"}</td><td>${t.queued_at.slice(11,19)}</td></tr>`).join("");
  document.getElementById("lb").innerText = d.logs.join("\n");
};
async function post(u, b){
  const r = await fetch(u, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(b)});
  const j = await r.json();
  document.getElementById("msg").innerText = "Status: " + (j.status || "OK");
}
async function saveSec(){
  const k = document.getElementById("vk").value.trim(), v = document.getElementById("vv").value.trim();
  if(!k||!v) return;
  await post("/api/vault/set", {key:k, value:v});
  document.getElementById("vk").value=""; document.getElementById("vv").value="";
}
async function pay(){
  const r = await fetch("/api/billing/create-checkout", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({amount:1500})});
  const j = await r.json();
  if(j.checkout_url) window.open(j.checkout_url, "_blank");
  else document.getElementById("msg").innerText = "Simulated $15.00 Checkout Recorded!";
}
async function regWh(){
  const u = document.getElementById("whu").value.trim();
  if(!u) return;
  const r = await fetch("/api/billing/register-webhook", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({cloud_url:u})});
  const j = await r.json();
  document.getElementById("msg").innerText = j.status === "REGISTERED" ? "Linked Webhook: " + j.details.id : "Err: " + j.error;
}
</script></body></html>"""
    return Response(html, mimetype="text/html")

def start_server():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    i = 0
    while True:
        i += 1
        swarm.enqueue_task(f"Heartbeat-#{i}", lambda *a: None)
        time.sleep(60)
