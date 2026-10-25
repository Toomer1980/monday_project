import time
import psutil
import logging
from pathlib import Path

logging.basicConfig(
    filename=Path(__file__).resolve().parents[3] / 'logs' / 'audit' / 'governor.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [GOVERNOR] %(message)s'
)

class SystemGovernor:
    def __init__(self):
        self.max_cpu_threshold = 85.0
        self.max_memory_threshold = 90.0

    def inspect_resources(self):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        logging.info(f"System Telemetry -> CPU: {cpu}% | RAM: {mem}%")
        if cpu > self.max_cpu_threshold or mem > self.max_memory_threshold:
            logging.warning("High resource utilization detected. Throttling non-critical daemons.")
            return False
        return True

if __name__ == "__main__":
    gov = SystemGovernor()
    gov.inspect_resources()
