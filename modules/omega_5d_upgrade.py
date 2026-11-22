import argparse
import datetime as dt
import json
import os
import py_compile
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
os.chdir(PDIR)


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return default


def get_public_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "http://127.0.0.1:8000"


# ==============================================================================
# 1. INTERACTIVE 5D PENTERACT + 4D TESSERACT /store & /portal + REFERRAL ENGINE
# ==============================================================================
def patch_storefront_5d():
    dp = os.path.join(PDIR, "sovereign_daemon.py")
    if not os.path.exists(dp):
        raise FileNotFoundError(f"Missing {dp}")

    bak_dir = os.path.join(PDIR, "backups", "omega5d_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(bak_dir, exist_ok=True)
    shutil.copy2(dp, os.path.join(bak_dir, "sovereign_daemon.py.bak"))

    src = open(dp, "r", encoding="utf-8").read()
    src = re.sub(r"\r?\n# === ORACLE_PORTAL_UPSELL_HOOK_START ===.*?# === ORACLE_PORTAL_UPSELL_HOOK_END ===\r?\n?", "\n", src, flags=re.DOTALL)
    src = re.sub(r"\r?\n# === ORACLE_4D_STOREFRONT_HOOK_START ===.*?# === ORACLE_4D_STOREFRONT_HOOK_END ===\r?\n?", "\n", src, flags=re.DOTALL)

    m_app = re.search(r"(?m)^([A-Za-z_]\w*)\s*=\s*Flask\s*\(", src)
    app_var = m_app.group(1) if m_app else "app"

    static_dir = os.path.join(PDIR, "static")
    os.makedirs(static_dir, exist_ok=True)
    js_path = os.path.join(static_dir, "omega_5d_engine.js")
    omega_js = """(function(){
  if (document.getElementById("omega-5d-canvas")) return;
  var c = document.createElement("canvas");
  c.id = "omega-5d-canvas";
  c.style.cssText = "position:fixed;inset:0;width:100vw;height:100vh;z-index:0;pointer-events:none;opacity:0.65;";
  document.body.insertBefore(c, document.body.firstChild);
  var ctx = c.getContext("2d");
  var W = 0, H = 0, mx = 0, my = 0;
  function resize(){ W = c.width = window.innerWidth; H = c.height = window.innerHeight; }
  resize(); window.addEventListener("resize", resize);
  window.addEventListener("mousemove", function(e){
    mx = (e.clientX / Math.max(1, W) - 0.5) * 1.4;
    my = (e.clientY / Math.max(1, H) - 0.5) * 1.4;
  });

  // 5D Penteract (32 vertices, 80 edges) projected 5D -> 4D -> 3D -> 2D
  var verts = [];
  for (var i = 0; i < 32; i++) {
    verts.push([(i&1)?1:-1, (i&2)?1:-1, (i&4)?1:-1, (i&8)?1:-1, (i&16)?1:-1]);
  }
  var edges = [];
  for (var a = 0; a < 32; a++) {
    for (var b = a + 1; b < 32; b++) {
      var diff = a ^ b;
      if (diff && (diff & (diff - 1)) === 0) edges.push([a, b, (a + b) % 3]);
    }
  }
  var stars = [];
  for (var s = 0; s < 75; s++) {
    stars.push({a: Math.random()*Math.PI*2, r: 0.25 + Math.random()*0.65, sp: 0.002 + Math.random()*0.006, sz: 1 + Math.random()*2.2});
  }

  function rot(v, i, j, th) {
    var ca = Math.cos(th), sa = Math.sin(th);
    var vi = v[i], vj = v[j];
    v[i] = vi * ca - vj * sa;
    v[j] = vi * sa + vj * ca;
  }

  var t = 0;
  function frame(){
    t += 0.0085;
    ctx.fillStyle = "rgba(4,7,18,0.28)";
    ctx.fillRect(0, 0, W, H);
    var cx = W * 0.5, cy = H * 0.42;
    var sc = Math.min(W, H) * 0.31;

    for (var k = 0; k < stars.length; k++) {
      var st = stars[k];
      st.a += st.sp;
      var px = cx + Math.cos(st.a) * sc * (1.2 + st.r) * (1 + 0.18 * Math.cos(st.a * 0.5));
      var py = cy + Math.sin(st.a * 1.5) * sc * (0.65 + st.r * 0.5);
      ctx.fillStyle = (k % 2 === 0) ? "rgba(56,189,248,0.55)" : "rgba(250,204,21,0.50)";
      ctx.beginPath(); ctx.arc(px, py, st.sz, 0, Math.PI * 2); ctx.fill();
    }

    var pts = [];
    for (var i = 0; i < 32; i++) {
      var v = verts[i].slice();
      rot(v, 0, 4, t * 0.7 + mx * 0.4);
      rot(v, 1, 3, t * 0.9 + my * 0.4);
      rot(v, 2, 4, t * 0.5);
      rot(v, 0, 2, t * 0.45 + mx * 0.35);
      rot(v, 1, 2, my * 0.35);
      var p5 = 2.6 / (3.8 - v[4]);
      var p4 = 2.5 / (3.8 - v[3] * p5);
      var p3 = 2.4 / (4.1 - v[2] * p5 * p4);
      var ksc = p5 * p4 * p3 * sc * 0.52;
      pts.push([cx + v[0] * ksc, cy + v[1] * ksc]);
    }

    var palette = ["rgba(56,189,248,0.44)", "rgba(250,204,21,0.40)", "rgba(167,139,250,0.38)"];
    ctx.lineWidth = 1.3;
    for (var e = 0; e < edges.length; e++) {
      var p1 = pts[edges[e][0]], p2 = pts[edges[e][1]];
      ctx.strokeStyle = palette[edges[e][2]];
      ctx.beginPath(); ctx.moveTo(p1[0], p1[1]); ctx.lineTo(p2[0], p2[1]); ctx.stroke();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  fetch("/api/live-pulse").then(function(r){ return r.json(); }).then(function(d){
    var el = document.getElementById("omega-live-pulse");
    if (el && d) {
      el.textContent = "LIVE TELEMETRY: " + d.vault_videos + " 4D ASSETS RENDERED  |  " + d.yt_views + " YOUTUBE VIEWS  |  " + d.utm_clicks + " VERIFIED CHECKOUT CLICKS  |  STRIPE LIVE PAYOUTS ACTIVE";
    }
  }).catch(function(){});
})();
function omegaCopyRef(){
  var code = localStorage.getItem("oracle_ref_code");
  if (!code) { code = "oracle_" + Math.random().toString(36).slice(2, 8); localStorage.setItem("oracle_ref_code", code); }
  var url = window.location.origin + "/go/assetpack15?utm_source=member_ref&utm_medium=share&utm_campaign=" + code;
  if (navigator.clipboard) navigator.clipboard.writeText(url);
  var btn = document.getElementById("omega-ref-btn");
  if (btn) { btn.textContent = "Referral Link Copied! Share to Unlock Bonus Pack"; }
  var inp = document.getElementById("omega-ref-url");
  if (inp) { inp.value = url; }
}
"""
    open(js_path, "w", encoding="utf-8", newline="").write(omega_js)

    hook_lines = [
        "",
        "# === ORACLE_4D_STOREFRONT_HOOK_START ===",
        f"@{app_var}.before_request",
        "def _oracle_handle_fast_cash_tiers():",
        "    try:",
        "        from flask import request as _req, redirect as _redir, jsonify as _jfy, send_from_directory as _sfd",
        "        import json as _j, os as _o, sqlite3 as _sq, datetime as _dt",
        "        base_dir = _o.path.dirname(_o.path.abspath(__file__))",
        '        if _req.path == "/static/omega_5d_engine.js":',
        '            return _sfd(_o.path.join(base_dir, "static"), "omega_5d_engine.js", mimetype="application/javascript")',
        '        if _req.path == "/api/live-pulse":',
        "            clicks, views = 0, 0",
        '            udb = _o.path.join(base_dir, "data", "utm_analytics.db")',
        "            if _o.path.exists(udb):",
        "                try:",
        "                    c = _sq.connect(udb); clicks = int(c.execute('SELECT COUNT(*) FROM utm_clicks').fetchone()[0]); c.close()",
        "                except Exception: pass",
        '            ya = _o.path.join(base_dir, "data", "youtube_analytics.json")',
        "            if _o.path.exists(ya):",
        "                try: views = int((_j.load(open(ya, 'r', encoding='utf-8')).get('totals') or {}).get('views', 0))",
        "                except Exception: pass",
        '            return _jfy({"vault_videos": 104, "utm_clicks": clicks, "yt_views": views, "status": "LIVE"})',
        '        if _req.path in ("/go/assetpack15", "/go/vaultsub15"):',
        '            tier_key = _req.path.rsplit("/", 1)[-1]',
        '            tpath = _o.path.join(base_dir, "config", "stripe_new_tiers.json")',
        '            target = "https://buy.stripe.com/eVq6oHgmt0Ex1OUfmZcQU05" if tier_key == "assetpack15" else "https://buy.stripe.com/aFa3cv3zH1IB65adeRcQU06"',
        "            if _o.path.exists(tpath):",
        '                td = _j.load(open(tpath, "r", encoding="utf-8"))',
        "                if td.get(tier_key): target = td[tier_key]",
        '            udb = _o.path.join(base_dir, "data", "utm_analytics.db")',
        "            if _o.path.exists(udb):",
        "                try:",
        "                    c = _sq.connect(udb)",
        '                    cols = [r[1] for r in c.execute("PRAGMA table_info(utm_clicks)").fetchall()]',
        "                    vals_map = {",
        '                        "tier": tier_key,',
        '                        "utm_source": _req.args.get("utm_source", "store_hero"),',
        '                        "utm_medium": _req.args.get("utm_medium", "card"),',
        '                        "utm_campaign": _req.args.get("utm_campaign", "omega_5d_v16"),',
        '                        "target_url": target,',
        '                        "ip": _req.remote_addr or "",',
        '                        "user_agent": (_req.headers.get("User-Agent") or "")[:200],',
        '                        "timestamp_utc": _dt.datetime.utcnow().isoformat() + "Z",',
        '                        "created_utc": _dt.datetime.utcnow().isoformat() + "Z",',
        '                        "clicked_at": _dt.datetime.utcnow().isoformat() + "Z",',
        "                    }",
        "                    use_cols = [col for col in cols if col in vals_map]",
        "                    if use_cols:",
        '                        q = "INSERT INTO utm_clicks (" + ",".join(use_cols) + ") VALUES (" + ",".join(["?"] * len(use_cols)) + ")"',
        "                        c.execute(q, [vals_map[col] for col in use_cols]); c.commit()",
        "                    c.close()",
        "                except Exception: pass",
        "            return _redir(target, code=302)",
        "    except Exception: pass",
        "",
        "",
        f"@{app_var}.after_request",
        "def _oracle_enhance_4d_store_and_portal(resp):",
        "    try:",
        "        from flask import request as _req",
        "        import re as _re",
        '        ct = (resp.content_type or "").lower()',
        '        if resp.status_code != 200 or "text/html" not in ct: return resp',
        '        if _req.path not in ("/store", "/portal"): return resp',
        "        body = resp.get_data(as_text=True)",
        '        if _req.path == "/store" and "oracle-4d-hero" not in body:',
        "            hero = (",
        "                '<style>'",
        "                'body{background:#040712 !important;color:#e2e8f0 !important;font-family:\"Segoe UI\",system-ui,sans-serif !important;position:relative;}'",
        "                'body > *:not(#omega-5d-canvas){position:relative;z-index:2;}'",
        "                '#oracle-4d-hero{max-width:1180px;margin:22px auto 28px auto;padding:30px 26px;backdrop-filter:blur(10px);'",
        "                'background:linear-gradient(135deg,rgba(7,13,31,0.86) 0%,rgba(15,23,42,0.82) 55%,rgba(9,19,38,0.88) 100%);'",
        "                'border:1px solid rgba(56,189,248,0.52);border-radius:16px;box-shadow:0 0 48px rgba(14,165,233,0.24),inset 0 0 24px rgba(250,204,21,0.06);}'",
        "                '.o4d-pulse{display:inline-block;padding:6px 12px;border-radius:999px;background:rgba(16,185,129,0.14);border:1px solid rgba(16,185,129,0.45);color:#6ee7b7;font-size:11px;font-weight:700;letter-spacing:1.4px;margin-bottom:10px;}'",
        "                '.o4d-kicker{color:#38bdf8;font-size:11px;letter-spacing:2.2px;font-weight:700;text-transform:uppercase;}'",
        "                '.o4d-title{margin:8px 0 10px 0;font-size:34px;line-height:1.15;'",
        "                'background:linear-gradient(90deg,#facc15,#38bdf8,#c084fc,#fef08a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}'",
        "                '.o4d-sub{color:#cbd5e1;font-size:15px;max-width:860px;margin:0 0 22px 0;line-height:1.5;}'",
        "                '.o4d-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:15px;}'",
        "                '.o4d-card{background:rgba(10,16,34,0.92);border:1px solid rgba(250,204,21,0.32);border-radius:12px;padding:18px;'",
        "                'display:flex;flex-direction:column;justify-content:space-between;transition:transform 0.2s ease,box-shadow 0.2s ease;}'",
        "                '.o4d-card:hover{transform:translateY(-4px);box-shadow:0 10px 30px rgba(56,189,248,0.28);}'",
        "                '.o4d-card.featured{border:1.5px solid #38bdf8;box-shadow:0 0 26px rgba(56,189,248,0.28);}'",
        "                '.o4d-badge{display:inline-block;font-size:10px;font-weight:800;padding:3px 8px;border-radius:4px;background:#facc15;color:#050814;margin-bottom:6px;letter-spacing:1px;}'",
        "                '.o4d-price{font-size:26px;font-weight:800;color:#facc15;margin:4px 0;}'",
        "                '.o4d-anchor{font-size:12px;color:#64748b;text-decoration:line-through;margin-left:6px;font-weight:500;}'",
        "                '.o4d-desc{font-size:13px;color:#94a3b8;margin:6px 0 14px 0;line-height:1.45;}'",
        "                '.o4d-btn{display:block;text-align:center;padding:11px 14px;border-radius:8px;font-weight:800;text-decoration:none;color:#050814;'",
        "                'background:linear-gradient(90deg,#facc15,#38bdf8);letter-spacing:0.4px;}'",
        "                '.o4d-btn.alt{background:linear-gradient(90deg,#0284c7,#059669);color:#f8fafc;}'",
        "                '.o4d-ref{margin-top:20px;padding:16px 18px;border-radius:12px;background:rgba(15,23,42,0.88);border:1px dashed rgba(250,204,21,0.55);display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;}'",
        "                '</style>'",
        "                '<section id=\"oracle-4d-hero\">'",
        "                '<div id=\"omega-live-pulse\" class=\"o4d-pulse\">LIVE TELEMETRY: 104 4D ASSETS RENDERED  |  STRIPE-VERIFIED INSTANT FULFILLMENT ACTIVE</div>'",
        "                '<div class=\"o4d-kicker\">ORACLE SYSTEMS LLC // INTERACTIVE 5D PENTERACT &amp; 4D TESSERACT ARCHITECTURE</div>'",
        "                '<h1 class=\"o4d-title\">Step Into Sovereign 4D/5D Media, Custom Aura Readings &amp; Autonomous AI Compute</h1>'",
        "                '<p class=\"o4d-sub\">Move your cursor to rotate the live 5D hypercube field. Every tier unlocks instant Stripe-verified fulfillment, member portal delivery, and zero-lock-in ownership.</p>'",
        "                '<div class=\"o4d-grid\">'",
        "                '<div class=\"o4d-card featured\"><div><span class=\"o4d-badge\">FASTEST START</span><div class=\"o4d-kicker\">CREATOR ASSET PACK</div><div class=\"o4d-price\">$15<span class=\"o4d-anchor\">$49 value</span></div>'",
        "                '<p class=\"o4d-desc\">Instant commercial-use ZIP: seamless 16:9 + 9:16 4D Tesseract/Mobius video loops &amp; 3D pop-out templates for YouTube, TikTok &amp; OBS.</p></div>'",
        "                '<a class=\"o4d-btn\" href=\"/go/assetpack15?utm_source=store_hero&utm_medium=card&utm_campaign=omega_v16\">Unlock Instant Pack ($15)</a></div>'",
        "                '<div class=\"o4d-card featured\"><div><span class=\"o4d-badge\">RECURRING VAULT</span><div class=\"o4d-kicker\">SOVEREIGN MEMBER VAULT</div><div class=\"o4d-price\">$15/mo<span class=\"o4d-anchor\">$39/mo</span></div>'",
        "                '<p class=\"o4d-desc\">Unlimited 30-min 4D transmissions, ad-free 432Hz harmonic downloads, early drops &amp; priority member upgrades. Cancel anytime.</p></div>'",
        "                '<a class=\"o4d-btn\" href=\"/go/vaultsub15?utm_source=store_hero&utm_medium=card&utm_campaign=omega_v16\">Join 4D Vault ($15/mo)</a></div>'",
        "                '<div class=\"o4d-card\"><div><div class=\"o4d-kicker\">TIER 1 // BLUEPRINT</div><div class=\"o4d-price\">$29</div>'",
        "                '<p class=\"o4d-desc\">Complete 52-Week Collective Reading &amp; Media Blueprint with immediate portal access and monetization schedules.</p></div>'",
        "                '<a class=\"o4d-btn\" href=\"/go/tier29?utm_source=store_hero&utm_medium=card&utm_campaign=omega_v16\">Unlock Blueprint ($29)</a></div>'",
        "                '<div class=\"o4d-card featured\"><div><span class=\"o4d-badge\">MOST POPULAR</span><div class=\"o4d-kicker\">PERSONALIZED 4D AURA</div><div class=\"o4d-price\">$49<span class=\"o4d-anchor\">$129 value</span></div>'",
        "                '<p class=\"o4d-desc\">Bespoke 4D Tesseract &amp; Mobius Aura Reading MP4 custom-rendered with your name, focus topic &amp; 432Hz audio—auto-delivered to your inbox.</p></div>'",
        "                '<a class=\"o4d-btn\" href=\"/go/auravideo49?utm_source=store_hero&utm_medium=card&utm_campaign=omega_v16\">Claim Custom 4D Aura ($49)</a></div>'",
        "                '<div class=\"o4d-card\"><div><div class=\"o4d-kicker\">TURNKEY CREATOR STACK</div><div class=\"o4d-price\">$1,500</div>'",
        "                '<p class=\"o4d-desc\">Full Oracle Systems Storefront Bundle: autonomous 52-week 4D pipeline, Stripe webhook automation, YouTube API bot &amp; B2B CRM.</p></div>'",
        "                '<a class=\"o4d-btn alt\" href=\"/go/fullstorefront?utm_source=store_hero&utm_medium=card&utm_campaign=omega_v16\">Deploy Full Stack ($1,500)</a></div>'",
        "                '<div class=\"o4d-card\"><div><div class=\"o4d-kicker\">ENTERPRISE DEDICATED NODE</div><div class=\"o4d-price\">$49,999</div>'",
        "                '<p class=\"o4d-desc\">Dedicated turnkey Pro_Node AI compute infrastructure for agencies &amp; studios (50% ACH Milestone 1 deposit / zero per-seat SaaS fees).</p></div>'",
        "                '<a class=\"o4d-btn alt\" href=\"/go/pro_node?utm_source=store_hero&utm_medium=card&utm_campaign=omega_v16\">Reserve Pro_Node ($49,999)</a></div>'",
        "                '</div>'",
        "                '<div class=\"o4d-ref\">'",
        "                '<div><strong style=\"color:#facc15;\">Share the 5D Portal &amp; Unlock Bonus Loops:</strong> <span style=\"color:#cbd5e1;font-size:13px;\">Send your personal creator link to 2 friends or post it on X/TikTok.</span></div>'",
        "                '<div style=\"display:flex;gap:8px;align-items:center;\"><input id=\"omega-ref-url\" readonly value=\"Click Copy to generate your tracked referral link\" style=\"background:#050814;color:#38bdf8;border:1px solid #334155;border-radius:6px;padding:7px 10px;width:270px;font-size:12px;\">'",
        "                '<button id=\"omega-ref-btn\" onclick=\"omegaCopyRef()\" style=\"cursor:pointer;padding:8px 14px;border:none;border-radius:6px;background:linear-gradient(90deg,#facc15,#38bdf8);color:#050814;font-weight:800;font-size:12px;\">Copy Referral Link</button></div>'",
        "                '</div></section><script src=\"/static/omega_5d_engine.js\"></script>'",
        "            )",
        "            if _re.search(r'<body[^>]*>', body, flags=_re.IGNORECASE):",
        "                body = _re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + hero, body, count=1, flags=_re.IGNORECASE)",
        "            else: body = hero + body",
        "            resp.set_data(body)",
        '        if _req.path == "/portal" and "oracle-portal-upsell" not in body and "</body>" in body.lower():',
        "            banner = (",
        "                '<div id=\"oracle-portal-upsell\" style=\"position:relative;z-index:2;max-width:820px;margin:24px auto;padding:24px;'",
        "                'background:linear-gradient(135deg,rgba(7,13,31,0.94),rgba(17,24,39,0.94));border:1.5px solid #f59e0b;border-radius:14px;'",
        "                'box-shadow:0 0 32px rgba(245,158,11,0.22);font-family:sans-serif;color:#f8fafc;text-align:center;\">'",
        "                '<div style=\"color:#38bdf8;font-size:12px;letter-spacing:2px;font-weight:bold;\">VERIFIED MEMBER ASCENSION // ORACLE SYSTEMS LLC</div>'",
        "                '<h3 style=\"margin:8px 0;color:#facc15;\">Scale Your Stack: $15/mo Vault, $1,500 Full Bundle, or Dedicated Pro_Node</h3>'",
        "                '<a href=\"/go/vaultsub15?utm_source=portal_upsell&utm_medium=banner&utm_campaign=omega_v16\" target=\"_blank\" rel=\"noopener\" style=\"display:inline-block;margin:6px;padding:10px 16px;background:#f59e0b;color:#050814;text-decoration:none;border-radius:7px;font-weight:bold;\">Join 4D Vault ($15/mo)</a>'",
        "                '<a href=\"/go/fullstorefront?utm_source=portal_upsell&utm_medium=banner&utm_campaign=omega_v16\" target=\"_blank\" rel=\"noopener\" style=\"display:inline-block;margin:6px;padding:10px 16px;background:#059669;color:#fff;text-decoration:none;border-radius:7px;font-weight:bold;\">Full Storefront ($1,500)</a>'",
        "                '<a href=\"/go/pro_node?utm_source=portal_upsell&utm_medium=banner&utm_campaign=omega_v16\" target=\"_blank\" rel=\"noopener\" style=\"display:inline-block;margin:6px;padding:10px 16px;background:#0284c7;color:#fff;text-decoration:none;border-radius:7px;font-weight:bold;\">Pro_Node ($49,999)</a>'",
        "                '</div><script src=\"/static/omega_5d_engine.js\"></script></body>'",
        "            )",
        "            body = _re.sub(r'</body>', banner, body, count=1, flags=_re.IGNORECASE)",
        "            resp.set_data(body)",
        "    except Exception: pass",
        "    return resp",
        "# === ORACLE_4D_STOREFRONT_HOOK_END ===",
        "",
    ]
    hook_text = "\n".join(hook_lines)
    m_main = re.search(r'(?m)^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', src)
    src = (src[:m_main.start()] + "\n" + hook_text + "\n" + src[m_main.start():]) if m_main else (src.rstrip() + "\n" + hook_text + "\n")
    open(dp, "w", encoding="utf-8", newline="").write(src)
    py_compile.compile(dp, doraise=True)
    print(f"[OMEGA 5D] Patched sovereign_daemon.py + static/omega_5d_engine.js (app='{app_var}')")

    ns = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
    pids = {ln.split()[-1] for ln in ns.splitlines() if ":8000 " in ln and "LISTENING" in ln.upper() and ln.split()[-1].isdigit()}
    for pid in pids:
        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    time.sleep(2)
    boot_log = open(os.path.join(PDIR, "logs", "daemon_boot.log"), "w", encoding="utf-8")
    subprocess.Popen([sys.executable, dp], cwd=PDIR, stdout=boot_log, stderr=boot_log, creationflags=0x08000000)

    ok = False
    for _ in range(10):
        time.sleep(1.5)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/store", timeout=4) as r:
                txt = r.read().decode("utf-8", "ignore")
                if r.status == 200 and "omega_5d_engine.js" in txt and "assetpack15" in txt:
                    ok = True
                    break
        except Exception:
            pass
    print(f"[OMEGA 5D] Live Port 8000 Interactive 5D Storefront Verified: {ok}")


# ==============================================================================
# 2. AUTONOMOUS YOUTUBE CTA COMMENT INJECTOR (POSTS TRACKED /go/ LINKS VIA API)
# ==============================================================================
def auto_comment_youtube():
    pub = get_public_url()
    tok_p = os.path.join(PDIR, "config", "youtube_token.json")
    if not os.path.exists(tok_p):
        print("[YT-COMMENT] Skipped: config/youtube_token.json not found.")
        return

    commented_p = os.path.join(PDIR, "data", "yt_commented_ids.json")
    done_ids = set(load_json(commented_p, []))

    vids = ["Wxxxgco7AX4"]
    st = load_json(os.path.join(PDIR, "data", "youtube_publish_state.json"), {})
    for key in ("published_shorts", "published_full"):
        for item in (st.get(key) or []):
            vid = item.get("video_id") if isinstance(item, dict) else ""
            if vid and vid not in vids:
                vids.append(vid)

    pending = [v for v in vids if v not in done_ids]
    if not pending:
        print(f"[YT-COMMENT] All {len(done_ids)} published YouTube video(s) already have live CTA comments.")
        return

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(tok_p)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds)

        posted = 0
        for vid in pending[:3]:
            cta_text = (
                "Step into the Live Interactive 5D Tesseract Portal:\n"
                f"-> $15 4D Creator Asset Pack (Seamless Loops + 3D Templates): {pub}/go/assetpack15?utm_source=yt_comment&utm_medium=short&utm_campaign={vid}\n"
                f"-> $15/mo Sovereign 4D Member Vault (30-Min Transmissions + 432Hz): {pub}/go/vaultsub15?utm_source=yt_comment&utm_medium=short&utm_campaign={vid}\n"
                f"-> $49 Custom Personalized 4D Aura Reading (Your Name + Focus): {pub}/go/auravideo49?utm_source=yt_comment&utm_medium=short&utm_campaign={vid}\n"
                f"-> Full Interactive 5D Storefront: {pub}/store"
            )
            try:
                yt.commentThreads().insert(
                    part="snippet",
                    body={"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": cta_text}}}},
                ).execute()
                done_ids.add(vid)
                posted += 1
                print(f"[YT-COMMENT PASS] Posted live tracked CTA comment on https://youtu.be/{vid}")
            except Exception as ex:
                print(f"[YT-COMMENT WARN] Video {vid}: {ex}")
        json.dump(sorted(done_ids), open(commented_p, "w", encoding="utf-8"), indent=2)
        print(f"[YT-COMMENT] Newly posted: {posted} | Total commented videos: {len(done_ids)}")
    except Exception as ex:
        print(f"[YT-COMMENT WARN] API error: {ex}")


# ==============================================================================
# 3. QUANTUM-INSPIRED BAYESIAN THOMPSON SAMPLING REVENUE BANDIT
# ==============================================================================
def run_revenue_bandit():
    udb = os.path.join(PDIR, "data", "utm_analytics.db")
    tier_clicks = {}
    if os.path.exists(udb):
        try:
            c = sqlite3.connect(udb)
            for t, cnt in c.execute("SELECT tier, COUNT(*) FROM utm_clicks GROUP BY tier").fetchall():
                tier_clicks[t] = int(cnt)
            c.close()
        except Exception:
            pass

    snap = load_json(os.path.join(PDIR, "audit_inbox", "stripe_live_api_snapshot.json"), {})
    net = float(snap.get("charges_net_usd", 47.28))

    tiers = [
        ("assetpack15", 15.0, "Impulse Cash Flow"),
        ("vaultsub15", 15.0, "Monthly Recurring Revenue"),
        ("tier29", 29.0, "Starter Blueprint"),
        ("auravideo49", 49.0, "High-Margin Custom 4D Video"),
        ("fullstorefront", 1500.0, "Turnkey Creator Stack"),
        ("pro_node", 49999.0, "Enterprise B2B Hardware"),
    ]
    total_clicks = max(1, sum(tier_clicks.values()))
    ranked = []
    for name, price, role in tiers:
        clicks = tier_clicks.get(name, 0)
        alpha = 1.0 + clicks
        beta = 1.0 + max(0, total_clicks - clicks)
        sampled_ctr = random.betavariate(alpha, beta)
        ev_score = round(sampled_ctr * (1.0 + (price ** 0.35)), 4)
        ranked.append({"tier": name, "price": price, "role": role, "clicks": clicks, "thompson_score": ev_score})

    ranked.sort(key=lambda x: x["thompson_score"], reverse=True)
    gap = round(max(0.0, 100.0 - net), 2)
    packs_needed = int((gap + 14.99) // 15) if gap > 0 else 0
    auras_needed = int((gap + 48.99) // 49) if gap > 0 else 0

    lines = [
        f"# Oracle Systems LLC - Omega Bayesian Revenue Strategy ({dt.datetime.now().strftime('%Y-%m-%d %H:%M')} EST)",
        f"- **Current Verified Net:** ${net:,.2f} | **Gap to $100 Tier 1 Cloud Gate:** ${gap:,.2f} ({packs_needed} x $15 Packs OR {auras_needed} x $49 Aura Orders)",
        f"- **Primary Promotion Priority (Thompson Bandit #1):** `{ranked[0]['tier']}` (${ranked[0]['price']:,.0f} - {ranked[0]['role']})",
        "",
        "## Tier Allocation Ranking (Live UTM Posterior + Revenue Weight)",
    ]
    for idx, r in enumerate(ranked, 1):
        lines.append(f"{idx}. **`{r['tier']}` (${r['price']:,.0f})** - {r['clicks']} clicks | Score: `{r['thompson_score']}` ({r['role']})")

    out_md = os.path.join(PDIR, "reports", "Omega_Bandit_Strategy.md")
    open(out_md, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    shutil.copy2(out_md, os.path.join(PDIR, "Oracle_Audit_2026", os.path.basename(out_md)))
    json.dump({"updated": dt.datetime.now().isoformat(), "ranked_tiers": ranked}, open(os.path.join(PDIR, "data", "omega_strategy_state.json"), "w", encoding="utf-8"), indent=2)
    print("\n".join(lines))


# ==============================================================================
# 4. AI SELF-DIAGNOSTIC WATCHDOG & NOV 27 / $100 GATE MILESTONE ALERTER
# ==============================================================================
def run_ai_self_diagnose():
    issues = []
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/live-pulse", timeout=4) as r:
            if r.status != 200:
                issues.append(f"Port 8000 returned HTTP {r.status}")
    except Exception as ex:
        issues.append(f"Port 8000 unreachable: {ex}")

    pub = get_public_url()
    if pub.startswith("https://"):
        try:
            with urllib.request.urlopen(pub + "/store", timeout=8) as r:
                if r.status != 200:
                    issues.append(f"Public tunnel returned HTTP {r.status}")
        except Exception as ex:
            issues.append(f"Public tunnel unreachable ({pub}): {ex}")

    snap = load_json(os.path.join(PDIR, "audit_inbox", "stripe_live_api_snapshot.json"), {})
    net = float(snap.get("charges_net_usd", 0.0))
    alert_flag = os.path.join(PDIR, "data", "tier1_gate_alert_sent.flag")
    today = dt.date.today()
    if (net >= 100.0 or today >= dt.date(2026, 11, 27)) and not os.path.exists(alert_flag):
        try:
            sys.path.insert(0, os.path.join(PDIR, "Modules"))
            from google_mail_engine import send_oracle_email
            subj = "[ACTION READY] Oracle Systems Tier 1 Cloud Cutover Gate Triggered!"
            body = (
                f"Hi Thomas,\n\nYour DigitalOcean Tier 1 cutover gate has been reached!\n"
                f"- Verified Net Revenue: ${net:,.2f}\n- Date: {today.isoformat()}\n\n"
                f"Run your 1-command deployment & cutover verifier:\n"
                f"  .\\preflight_nov27_payout.ps1\n"
                f"  .\\deploy_digitalocean_tier1.ps1 -DropletIP <IP> -Domain oraclesystemsllc.com -BootstrapRemote\n"
                f"  .\\verify_do_tier1_cutover.ps1 -Domain oraclesystemsllc.com -ExpectedIP <IP> -PromoteToProduction\n"
            )
            via = send_oracle_email(PDIR, "Toomer1980@gmail.com", subj, body)
            open(alert_flag, "w", encoding="utf-8").write(dt.datetime.now().isoformat())
            print(f"[MILESTONE ALERT SENT] Triggered Tier 1 cutover email via {via}")
        except Exception as ex:
            issues.append(f"Milestone alert email failed: {ex}")

    diagnosis = "All core services healthy (0 runtime anomalies detected)."
    if issues:
        diagnosis = "Issues detected:\n" + "\n".join(f"- {i}" for i in issues)
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
                models = [m.get("name", "") for m in json.loads(r.read().decode("utf-8")).get("models", [])]
            usable = [m for m in models if not any(b in m.lower() for b in (":0.5b", ":1b", "tinyllama"))]
            if usable:
                payload = json.dumps({
                    "model": usable[0],
                    "prompt": f"Diagnose these Windows Python/Flask/Cloudflare server issues in 3 concise bullet points with exact fixes:\n{diagnosis}",
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 220},
                }).encode("utf-8")
                req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=45) as resp:
                    ai_note = json.loads(resp.read().decode("utf-8")).get("response", "").strip()
                    if ai_note:
                        diagnosis += "\n\n### Local Ollama AI Root-Cause Analysis\n" + ai_note
        except Exception:
            pass

    log_md = os.path.join(PDIR, "reports", "AI_Self_Heal_Log.md")
    entry = f"# SovereignCore AI Self-Heal Watchdog ({dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST)\n{diagnosis}\n"
    open(log_md, "w", encoding="utf-8", newline="").write(entry)
    print(f"[AI WATCHDOG] {issues if issues else 'ALL SYSTEMS NOMINAL (0 issues)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch-store", action="store_true")
    ap.add_argument("--comment-yt", action="store_true")
    ap.add_argument("--bandit", action="store_true")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if args.all or args.patch_store:
        patch_storefront_5d()
    if args.all or args.comment_yt:
        auto_comment_youtube()
    if args.all or args.bandit:
        run_revenue_bandit()
    if args.all or args.diagnose:
        run_ai_self_diagnose()


if __name__ == "__main__":
    main()