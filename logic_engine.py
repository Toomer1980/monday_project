import subprocess
import time
import os

# Configuration
RELAY_SCRIPT = r"C:\Users\toome\OracleSystems\relay.py"
LOG_PATH = r"C:\Users\toome\OracleSystems\relay_log.txt"

def execute_relay():
    """Autonomous execution command."""
    try:
        subprocess.run(["python", RELAY_SCRIPT], check=True)
    except Exception as e:
        print(f"Logic Engine Error: {e}")

def self_correct():
    """Machine-led surveillance loop."""
    print("SovereignCore Logic Engine Online...")
    while True:
        try:
            # 1. Forensic Analysis: Check if the relay is functioning
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, 'r') as f:
                    last_line = f.readlines()[-1]
                    
                    # 2. Predictive Repair logic
                    if "FAILED" in last_line or "CRITICAL" in last_line:
                        print("Anomaly detected. Initiating autonomous reset...")
                        execute_relay()
            
            # 3. Heartbeat interval (5 seconds)
            time.sleep(5)
            
        except Exception as e:
            # Silence feedback: The machine repairs itself without bothering the user
            time.sleep(10)

if __name__ == "__main__":
    self_correct()