import datetime as dt
import glob
import json
import os
import py_compile
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
LOG_P = os.path.join(PDIR, "logs", "self_healing_supervisor.log")
os.makedirs(os.path.dirname(LOG_P), exist_ok=True)


def log(msg):
    line = f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        open(LOG_P, "a", encoding="utf-8").write(line + "\n")
    except Exception:
        pass


def check_syntax_all():
    bad = []
    targets = [os.path.join(PDIR, "sovereign_daemon.py")] + glob.glob(os.path.join(PDIR, "Modules", "*.py"))
    for fp in targets:
        try:
            py_compile.compile(fp, doraise=True)
        except Exception as ex:
            bad.append((fp, str(ex)))
    return bad


def rollback_daemon_if_needed():
    dp = os.path.join(PDIR, "sovereign_daemon.py")
    try:
        py_compile.compile(dp, doraise=True)
        return True
    except Exception as ex:
        log(f"[SELF-HEAL ALERT] sovereign_daemon.py compile error: {ex}")
        baks = sorted(glob.glob(os.path.join(PDIR, "backups", "daemon_*.py.bak")))
        if baks:
            shutil.copy2(baks[-1], dp)
            log(f"[SELF-HEAL ROLLBACK] Restored last known-good backup -> {os.path.basename(baks[-1])}")
            return True
        return False


def check_http_health():
    for path in ("/store", "/api/exec-telemetry", "/api/deck-manifest"):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000" + path, timeout=5) as r:
                if r.status != 200:
                    return False, f"{path} HTTP {r.status}"
        except Exception as ex:
            return False, f"{path} unreachable: {ex}"
    return True, "ALL_200_OK"


def restart_daemon():
    dp = os.path.join(PDIR, "sovereign_daemon.py")
    ns = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
    pids = {ln.split()[-1] for ln in ns.splitlines() if ":8000 " in ln and "LISTENING" in ln.upper() and ln.split()[-1].isdigit()}
    for pid in pids:
        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    time.sleep(2)
    lf = open(os.path.join(PDIR, "logs", "daemon_boot.log"), "w", encoding="utf-8")
    subprocess.Popen([sys.executable, dp], cwd=PDIR, stdout=lf, stderr=lf, creationflags=0x08000000)
    time.sleep(3)


def check_sqlite_dbs():
    dbs = glob.glob(os.path.join(PDIR, "data", "*.db"))
    ok, fail = 0, []
    for dbp in dbs:
        try:
            c = sqlite3.connect(dbp)
            res = c.execute("PRAGMA integrity_check").fetchone()[0]
            c.close()
            if str(res).lower() == "ok":
                ok += 1
            else:
                fail.append(os.path.basename(dbp))
        except Exception:
            fail.append(os.path.basename(dbp))
    return ok, len(dbs), fail


def main():
    rollback_daemon_if_needed()
    bad_py = check_syntax_all()
    if bad_py:
        log(f"[SYNTAX WARN] {len(bad_py)} module(s) failed compile: {[os.path.basename(x[0]) for x in bad_py]}")
    else:
        log("[SYNTAX PASS] sovereign_daemon.py + all Modules/*.py compiled cleanly.")

    ok_http, detail = check_http_health()
    if not ok_http:
        log(f"[SELF-HEAL ACTION] Local server unhealthy ({detail}) -> restarting Port 8000...")
        restart_daemon()
        ok_http, detail = check_http_health()
        log(f"[SELF-HEAL POST-RESTART] Health: {ok_http} ({detail})")
    else:
        log(f"[HTTP PASS] Port 8000 live endpoints verified ({detail})")

    ok_db, tot_db, fail_db = check_sqlite_dbs()
    log(f"[SQLITE PASS] {ok_db}/{tot_db} databases healthy" + (f" | Failed: {fail_db}" if fail_db else ""))


if __name__ == "__main__":
    main()
