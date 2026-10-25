import shutil
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
BACKUP_DIR = ROOT_DIR / "data" / "shards"

def create_snapshot():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"ledger_snapshot_{stamp}"
    ledger_src = DATA_DIR / "ledger"
    if ledger_src.exists():
        shutil.make_archive(str(target), "zip", str(ledger_src))
        logging.info(f"Snapshot created: {target}.zip")

if __name__ == "__main__":
    create_snapshot()
