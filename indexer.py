import os
import json
import sqlite3
from datetime import datetime

class SovereignIndexer:
    def __init__(self, core_path="."):
        self.core_path = core_path
        self.modules_path = os.path.join(core_path, "modules")
        self.storage_path = os.path.join(core_path, "storage")
        self.db_path = os.path.join(self.storage_path, "global_memory.db")
        
        # Ensure directories exist
        os.makedirs(self.storage_path, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initializes the persistent memory database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Table for historical facts, code snippets, and chat insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                topic TEXT,
                content TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def catalog_modules(self):
        """Scans and maps all available python scripts."""
        manifest = {}
        if os.path.exists(self.modules_path):
            files = [f for f in os.listdir(self.modules_path) if f.endswith('.py')]
            for f in files:
                manifest[f] = {
                    "path": os.path.join(self.modules_path, f),
                    "last_modified": datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(self.modules_path, f))
                    ).strftime('%Y-%m-%d %H:%M:%S')
                }
        
        manifest_path = os.path.join(self.storage_path, "index_manifest.json")
        with open(manifest_path, 'w') as mf:
            json.dump(manifest, mf, indent=4)
        return f"Cataloged {len(manifest)} modules into index_manifest.json"

    def ingest_chat_data(self, category, topic, content):
        """Injects assessed information from past logs into global memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO knowledge_base (category, topic, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (category, topic, content, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

# Initialization stub
if __name__ == "__main__":
    indexer = SovereignIndexer()
    print(indexer.catalog_modules())