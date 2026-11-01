import os, sys, csv
BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "modules"))
import db
def generate_csv_report():
    rdir = os.path.join(BASE_DIR, "data", "reports")
    os.makedirs(rdir, exist_ok=True)
    p = os.path.join(rdir, "latest_weekly_report.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Task Name", "Status", "Runtime", "Queued At"])
        for t in db.get_all_tasks():
            w.writerow([t["id"], t["task_name"], t["status"], t["duration_sec"], t["queued_at"]])
    return p