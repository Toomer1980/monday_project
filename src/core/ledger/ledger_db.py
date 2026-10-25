import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "ledger" / "oracle_ledger.db"

def init_ledger():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                client_id TEXT NOT NULL,
                gross_amount REAL NOT NULL,
                tax_reserve REAL NOT NULL,
                net_amount REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)
        conn.commit()

def record_transaction(client_id: str, gross: float, status: str = "CLEARED"):
    init_ledger()
    tax = round(gross * 0.22, 2)
    net = round(gross - tax, 2)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO transactions (timestamp, client_id, gross_amount, tax_reserve, net_amount, status) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), client_id, gross, tax, net, status)
        )
        conn.commit()

if __name__ == "__main__":
    init_ledger()
