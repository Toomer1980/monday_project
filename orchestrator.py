import subprocess
import time
import sys

def launch_matrix():
    print("[M.O.N.D.A.Y.] Initializing SovereignCore Global Matrix...")
    processes = ["prophet_pipeline.py", "swarm_api.py", "divination_core.py", "monday_hud.py"]
    active_procs = []
    
    for script in processes:
        proc = subprocess.Popen([sys.executable, script])
        active_procs.append(proc)
        print(f"[+] {script} engaged.")
        time.sleep(1)
        
    print("[M.O.N.D.A.Y.] All systems stable. Matrix operational.")
    try:
        for p in active_procs: p.wait()
    except KeyboardInterrupt:
        print("[!] Emergency Shutdown Requested.")
        for p in active_procs: p.terminate()

if __name__ == "__main__":
    launch_matrix()
