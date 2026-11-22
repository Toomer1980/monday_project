import json
import os
import sqlite3

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
CAT_PATH = os.path.join(PDIR, "config", "merch_catalog.json")
DB_PATH = os.path.join(PDIR, "data", "merch_orders.db")
os.makedirs(os.path.dirname(CAT_PATH), exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

CATALOG = [
    {"sku": "ORCL-DECK-GOLD", "name": "Oracle Systems Collector Gold-Foil 10-Card Physical Deck", "price_usd": 49.00, "provider": "printify", "margin_est_usd": 31.00},
    {"sku": "ORCL-HOODIE-5D", "name": "Sovereign 5D Obsidian & Gold Heavyweight Hoodie", "price_usd": 68.00, "provider": "printful", "margin_est_usd": 29.50},
    {"sku": "ORCL-DESKMAT-3D", "name": "Celestial Astrolabe XL Gaming & Studio Desk Mat", "price_usd": 34.00, "provider": "printful", "margin_est_usd": 17.00},
    {"sku": "ORCL-MUG-MATTE", "name": "Oracle Systems Matte Black & Gold Ceramic Mug", "price_usd": 22.00, "provider": "printify", "margin_est_usd": 11.50},
]


def main():
    json.dump(CATALOG, open(CAT_PATH, "w", encoding="utf-8"), indent=2)
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "CREATE TABLE IF NOT EXISTS merch_orders ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, order_ref TEXT UNIQUE, sku TEXT, "
        "customer_email TEXT, shipping_json TEXT, fulfillment_status TEXT, created_utc TEXT)"
    )
    c.commit()
    c.close()
    print(f"[PHASE 48 PASS] Branded Merch Catalog ({len(CATALOG)} SKUs) & Printful/Printify fulfillment DB ready -> {CAT_PATH}")


if __name__ == "__main__":
    main()
