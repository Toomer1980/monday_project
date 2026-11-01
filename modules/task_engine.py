import os, sys, time, queue, logging, threading

BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "modules"))
import db

LOG_PATH = os.path.join(BASE_DIR, "logs", "daemon.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
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
        logging.info(f"WorkerSwarm initialized with {num_workers} threads.")

    def enqueue_task(self, task_name, task_func, *args, payload=None, max_retries=3, **kwargs):
        tid = db.record_task_queued(task_name, payload or {})
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
        logging.info(f"[QUEUE PURGE] Drained {count} tasks.")
        return count

    def _worker_loop(self, wid):
        while self.running:
            try:
                job = self.task_queue.get(timeout=1)
                tid, name, func, args, kw, retries, attempt, start = job["task_id"], job["task_name"], job["task_func"], job["args"], job["kwargs"], job["max_retries"], job["attempt"], job["start_time"]
                try:
                    func(*args, **kw)
                    dur = round(time.time() - start, 3)
                    db.record_task_completed(tid, dur)
                    logging.info(f"[{wid}] Completed: {name} in {dur}s")
                except Exception as err:
                    attempt += 1
                    if attempt <= retries:
                        time.sleep(2 ** (attempt - 1))
                        job["attempt"] = attempt
                        self.task_queue.put(job)
                    else:
                        db.record_task_failed(tid, str(err), round(time.time() - start, 3))
                        logging.error(f"[{wid}] Failed permanently: {name} -> {err}")
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

swarm = WorkerSwarm(num_workers=4)
