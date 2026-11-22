import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import json
import subprocess
import sys

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
MANIFEST_P = os.path.join(PDIR, "data", "verified_deck_manifest.json")


def main():
    print("[PHASE 42] Scanning Downloads, Desktop, Pictures & assets\\tarot_deck for all 10 ray-traced cards...")
    subprocess.run([sys.executable, os.path.join(PDIR, "Modules", "qa_deep_audit.py")], check=False)

    deck = json.load(open(MANIFEST_P, "r", encoding="utf-8")) if os.path.exists(MANIFEST_P) else []
    print(f"[PHASE 42] Active verified ray-traced cards: {len(deck)}/10")
    for item in deck:
        print(f"  - {item['slug']}.png ({item.get('w','?')}x{item.get('h','?')}) -> {item['title']}")

    if os.path.exists(os.path.join(PDIR, "Modules", "rebuild_raytraced_thumbs.py")) and deck:
        subprocess.run([sys.executable, os.path.join(PDIR, "Modules", "rebuild_raytraced_thumbs.py")], check=False)

    missing = 10 - len(deck)
    if missing > 0:
        print(f"[PHASE 42 NOTE] {missing} card(s) still waiting to be saved to Downloads or assets\\tarot_deck\\; re-run this script anytime after saving them.")
    else:
        print("[PHASE 42 PASS] ALL 10/10 RAY-TRACED MAJOR ARCANA CARDS ACTIVE!")


if __name__ == "__main__":
    main()
