import os, sys, time, subprocess, urllib.request
CORE = "C:/Users/toome/Desktop/SovereignCore"
PROJ = "C:/Users/toome/monday_project"

PART2 = r'''
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
'''

for b in [CORE, PROJ]:
    dp = os.path.join(b, "sovereign_daemon.py")
    base_txt = open(dp, "r", encoding="utf-8").read().split('@app.route("/store")')[0]
    with open(dp, "w", encoding="utf-8", newline="\n") as f:
        f.write(base_txt.rstrip() + "\n\n" + PART2.strip() + "\n")

subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe"], capture_output=True)
pyw = sys.executable.replace("python.exe", "pythonw.exe")
run = pyw if os.path.exists(pyw) else sys.executable
subprocess.Popen([run, os.path.join(CORE, "sovereign_daemon.py")], cwd=CORE, creationflags=0x08000000)

for _ in range(10):
    time.sleep(1)
    try:
        if urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=2).status == 200:
            print("[+] Server LIVE at http://127.0.0.1:8000")
            break
    except Exception:
        pass

subprocess.run(["git", "add", "-A"], cwd=PROJ)
subprocess.run(["git", "commit", "-m", "Deploy Oracle Systems Storefront, Portal & Executive Matrix"], cwd=PROJ)
subprocess.run(["git", "push", "origin", "main"], cwd=PROJ)
os.startfile("http://127.0.0.1:8000/store")
os.startfile("http://127.0.0.1:8000/dashboard")
print("[+] COMPLETE! Storefront and Matrix opened!")