import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import glob
import json
import subprocess
import sys

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
SHORTS_DIR = os.path.join(PDIR, "Content_Vault_4D_Shorts")
STATE_P = os.path.join(PDIR, "data", "living_shorts_rendered.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2)
    ap.add_argument("--accent", type=str, default="Irish", choices=["Irish", "Australian"])
    args = ap.parse_args()

    done = set(json.load(open(STATE_P, "r", encoding="utf-8"))) if os.path.exists(STATE_P) else set()
    # Prioritize next learning-curve Shorts (#13, #14, #15, #16)
    priority = [
        "Short_13_Abundance_Magnet_4D_MAX.mp4",
        "Short_14_Clearing_Blockages_4D_MAX.mp4",
        "Short_15_Victory_Unlocked_4D_MAX.mp4",
        "Short_16_Legacy_Builder_4D_MAX.mp4",
    ]
    all_shorts = [os.path.basename(p) for p in sorted(glob.glob(os.path.join(SHORTS_DIR, "*_4D_MAX.mp4")))]
    ordered = [s for s in priority if s in all_shorts] + [s for s in all_shorts if s not in priority]
    todo = [s for s in ordered if s not in done][:args.count]

    print(f"[PHASE 36] Batch Living-Card 9:16 Short Factory | Queued: {len(todo)} | Voice: {args.accent} Female")
    rendered = 0
    for sf in todo:
        r = subprocess.run([
            sys.executable, os.path.join(PDIR, "Modules", "render_cinema_short.py"),
            "--short-file", sf, "--accent", args.accent,
        ])
        if r.returncode == 0:
            done.add(sf)
            rendered += 1
            json.dump(sorted(done), open(STATE_P, "w", encoding="utf-8"), indent=2)
    print(f"[PHASE 36 PASS] Rendered {rendered}/{len(todo)} Living-Card Shorts | Total upgraded: {len(done)}/{len(all_shorts)}")


if __name__ == "__main__":
    main()
