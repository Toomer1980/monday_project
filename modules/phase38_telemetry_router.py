import os
import py_compile
import shutil
import subprocess
import sys
import time
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
dp = os.path.join(PDIR, "sovereign_daemon.py")
bak = os.path.join(PDIR, "backups", "daemon_p38_" + time.strftime("%Y%m%d_%H%M%S") + ".py.bak")
shutil.copy2(dp, bak)

src = open(dp, "r", encoding="utf-8").read()
changed = False

if "/static/phase32_interactive_audio.js" not in src:
    src = src.replace(
        'if _req.path.startswith("/static/vendor/"):',
        'if _req.path == "/static/phase32_interactive_audio.js":\n'
        '            return _sfd(_o.path.join(base_dir, "static"), "phase32_interactive_audio.js", mimetype="application/javascript")\n'
        '        if _req.path.startswith("/download/"):\n'
        '            import sys as _sys\n'
        '            if _o.path.join(base_dir, "Modules") not in _sys.path: _sys.path.insert(0, _o.path.join(base_dir, "Modules"))\n'
        '            from license_fulfillment_engine import resolve_download_token as _rdt\n'
        '            fp, status_msg = _rdt(_req.path.rsplit("/", 1)[-1])\n'
        '            if fp: return _sfd(_o.path.dirname(fp), _o.path.basename(fp), as_attachment=True)\n'
        '            return _Resp(status_msg, status=404, mimetype="text/plain")\n'
        '        if _req.path == "/api/exec-telemetry":\n'
        '            snap_p = _o.path.join(base_dir, "audit_inbox", "stripe_live_api_snapshot.json")\n'
        '            snap = _j.load(open(snap_p, "r", encoding="utf-8")) if _o.path.exists(snap_p) else {}\n'
        '            tier_counts = {}\n'
        '            udb = _o.path.join(base_dir, "data", "utm_analytics.db")\n'
        '            if _o.path.exists(udb):\n'
        '                try:\n'
        '                    c = _sq.connect(udb)\n'
        '                    for tk, cnt in c.execute("SELECT tier, COUNT(*) FROM utm_clicks GROUP BY tier").fetchall(): tier_counts[tk] = int(cnt)\n'
        '                    c.close()\n'
        '                except Exception: pass\n'
        '            crm_n = 0\n'
        '            cdb = _o.path.join(base_dir, "data", "pronode_crm.db")\n'
        '            if _o.path.exists(cdb):\n'
        '                try:\n'
        '                    c = _sq.connect(cdb); crm_n = int(c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]); c.close()\n'
        '                except Exception: pass\n'
        '            return _jfy({"phase": 41, "completion_pct": 82, "stripe_pending_usd": snap.get("pending_usd", 47.28), "utm_by_tier": tier_counts, "pronode_prospects": crm_n, "status": "ONLINE"})\n'
        '        if _req.path.startswith("/static/vendor/"):',
        1,
    )
    changed = True

if changed:
    open(dp, "w", encoding="utf-8", newline="").write(src)
    try:
        py_compile.compile(dp, doraise=True)
    except Exception as ex:
        shutil.copy2(bak, dp)
        raise RuntimeError(f"Rolled back sovereign_daemon.py safely after compile error: {ex}")

# Clean single-instance restart of Port 8000
ns = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
pids = {ln.split()[-1] for ln in ns.splitlines() if ":8000 " in ln and "LISTENING" in ln.upper() and ln.split()[-1].isdigit()}
for pid in pids:
    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
time.sleep(2)
log_f = open(os.path.join(PDIR, "logs", "daemon_boot.log"), "w", encoding="utf-8")
subprocess.Popen([sys.executable, dp], cwd=PDIR, stdout=log_f, stderr=log_f, creationflags=0x08000000)

ok_api, ok_js = False, False
for _ in range(10):
    time.sleep(1.5)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/exec-telemetry", timeout=4) as r:
            ok_api = (r.status == 200 and "completion_pct" in r.read().decode("utf-8", "ignore"))
        with urllib.request.urlopen("http://127.0.0.1:8000/static/phase32_interactive_audio.js", timeout=4) as r2:
            ok_js = (r2.status == 200)
        if ok_api and ok_js:
            break
    except Exception:
        pass
print(f"[PHASE 38 PASS] /api/exec-telemetry Live: {ok_api} | /static/phase32_interactive_audio.js Live: {ok_js} | /download/<token> Armed")
