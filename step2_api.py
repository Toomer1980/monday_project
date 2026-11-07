import os
CORE = "C:/Users/toome/Desktop/SovereignCore"
PROJ = "C:/Users/toome/monday_project"

PART1 = r'''import os, sys, json, time, logging, threading
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
'''

for b in [CORE, PROJ]:
    open(os.path.join(b, "sovereign_daemon.py"), "w", encoding="utf-8").write(PART1)
print("[+] Step 2 API Routes Written!")