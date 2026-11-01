$ErrorActionPreference = "Stop"
$CoreDir = "C:\Users\toome\Desktop\SovereignCore"
$DataDir = "C:\Users\toome\Desktop\SovereignCore\data"
$BackupDir = "C:\Users\toome\Desktop\SovereignCore\data\backups"
$ReportDir = "C:\Users\toome\Desktop\SovereignCore\data\reports"
$ConfigDir = "C:\Users\toome\Desktop\SovereignCore\config"
$ModuleDir = "C:\Users\toome\Desktop\SovereignCore\modules"
$ProjectDir = "C:\Users\toome\monday_project"

foreach ($dir in @($CoreDir, $DataDir, $BackupDir, $ReportDir, $ConfigDir, $ModuleDir, $ProjectDir)) {
    if (-not (Test-Path -Path $dir)) { New-Item -Path $dir -ItemType Directory -Force | Out-Null }
}

Write-Host "[+] Initializing SovereignCore Master Subsystems..." -ForegroundColor Cyan

[System.IO.File]::WriteAllText("$ModuleDir\db.py", 'import os, json, sqlite3
from datetime import datetime
DB_PATH = r"C:\Users\toome\Desktop\SovereignCore\data\sovereign_tasks.db"
def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_connection()
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS task_history (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT NOT NULL, payload TEXT, status TEXT NOT NULL, queued_at TEXT NOT NULL, completed_at TEXT, duration_sec REAL, error_msg TEXT)")
    conn.close()
def record_task_queued(task_name, payload):
    conn = get_connection()
    with conn:
        cur = conn.execute("INSERT INTO task_history (task_name, payload, status, queued_at) VALUES (?, ?, ?, ?)", (task_name, json.dumps(payload or {}), "QUEUED", datetime.now().isoformat()))
        tid = cur.lastrowid
    conn.close()
    return tid
def record_task_completed(tid, dur):
    conn = get_connection()
    with conn:
        conn.execute("UPDATE task_history SET status = ?, completed_at = ?, duration_sec = ? WHERE id = ?", ("COMPLETED", datetime.now().isoformat(), dur, tid))
    conn.close()
def record_task_failed(tid, err, dur=0.0):
    conn = get_connection()
    with conn:
        conn.execute("UPDATE task_history SET status = ?, completed_at = ?, duration_sec = ?, error_msg = ? WHERE id = ?", ("FAILED", datetime.now().isoformat(), dur, str(err), tid))
    conn.close()
def record_task_cancelled(tid):
    conn = get_connection()
    with conn:
        conn.execute("UPDATE task_history SET status = ?, completed_at = ?, error_msg = ? WHERE id = ?", ("CANCELLED", datetime.now().isoformat(), "Purged", tid))
    conn.close()
def get_recent_tasks(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
def get_all_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_history ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
init_db()')

[System.IO.File]::WriteAllText("$ModuleDir\task_engine.py", 'import os, sys, time, queue, logging, threading
from datetime import datetime
sys.path.append(r"C:\Users\toome\Desktop\SovereignCore\modules")
import db
LOG_PATH = r"C:\Users\toome\Desktop\SovereignCore\logs\daemon.log"
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class WorkerSwarm:
    def __init__(self, num_workers=4):
        self.task_queue = queue.Queue()
        self.workers = []
        self.running = True
        for i in range(num_workers):
            t = threading.Thread(target=self._worker_loop, args=(f"SwarmWorker-{i+1}",), daemon=True)
            self.workers.append(t)
            t.start()
    def enqueue_task(self, task_name, task_func, *args, payload=None, max_retries=3, **kwargs):
        p_meta = payload if payload is not None else {}
        tid = db.record_task_queued(task_name, p_meta)
        self.task_queue.put({"task_id": tid, "task_name": task_name, "task_func": task_func, "args": args, "kwargs": kwargs, "max_retries": max_retries, "attempt": 0, "start_time": time.time()})
        return tid
    def purge_queue(self):
        count = 0
        while not self.task_queue.empty():
            try:
                job = self.task_queue.get_nowait()
                db.record_task_cancelled(job["task_id"])
                self.task_queue.task_done()
                count += 1
            except queue.Empty:
                break
        return count
    def _worker_loop(self, wid):
        while self.running:
            try:
                job = self.task_queue.get(timeout=1)
                tid, name, func, args, kw, retries, attempt, start = job["task_id"], job["task_name"], job["task_func"], job["args"], job["kwargs"], job["max_retries"], job["attempt"], job["start_time"]
                try:
                    func(*args, **kw)
                    db.record_task_completed(tid, round(time.time() - start, 3))
                except Exception as err:
                    attempt += 1
                    if attempt <= retries:
                        time.sleep(2 ** (attempt - 1))
                        job["attempt"] = attempt
                        self.task_queue.put(job)
                    else:
                        db.record_task_failed(tid, str(err), round(time.time() - start, 3))
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass
    def shutdown(self):
        self.running = False
        for w in self.workers: w.join(timeout=2)
swarm = WorkerSwarm(num_workers=4)'