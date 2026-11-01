import os, time, requests, subprocess
HEALTH_URL = "http://127.0.0.1:8000/api/health"
def run_watchdog():
    while True:
        time.sleep(15)
        try:
            if requests.get(HEALTH_URL, timeout=4).status_code != 200:
                raise RuntimeError()
        except Exception:
            if os.name == "nt":
                subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", "Stop-ScheduledTask -TaskName SovereignCore-AutoDaemon -ErrorAction SilentlyContinue; Start-ScheduledTask -TaskName SovereignCore-AutoDaemon"], creationflags=0x08000000)
if __name__ == "__main__":
    run_watchdog()
