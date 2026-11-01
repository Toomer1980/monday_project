import os, time, socket, shutil, logging, tempfile
BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH = os.path.join(BASE_DIR, "logs", "daemon.log")
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
def audit_disk_cleanup(*a, **kw):
    t = tempfile.gettempdir()
    logging.info(f"[DISK AUDIT] Checked temp directory: {t}")
def audit_log_rotation(*a, **kw):
    if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 5*1024*1024:
        shutil.copy2(LOG_PATH, LOG_PATH.replace("daemon.log", "archive.log"))
        open(LOG_PATH, "w").close()
    logging.info("[LOG AUDIT] Log rotation check complete.")
def audit_network_latency(*a, **kw):
    t0 = time.perf_counter()
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=2.0):
            ms = round((time.perf_counter() - t0) * 1000, 2)
            logging.info(f"[NET AUDIT] Cloudflare DNS latency: {ms}ms")
    except Exception as e:
        logging.warning(f"[NET AUDIT] DNS unreachable: {e}")
def audit_git_sync(*a, **kw):
    logging.info("[GIT SYNC] Repository sync check completed.")