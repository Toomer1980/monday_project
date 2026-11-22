import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import glob
import json
import re
import subprocess
import sys

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
FULL_DIR = os.path.join(PDIR, "Content_Vault_4D_Full")
SHORTS_DIR = os.path.join(PDIR, "Content_Vault_4D_Shorts")
STATE_P = os.path.join(PDIR, "data", "ultra_4d5d_vault_progress.json")


def load_state():
    if os.path.exists(STATE_P):
        try:
            return json.load(open(STATE_P, "r", encoding="utf-8"))
        except Exception:
            pass
    return {"full_done": [], "shorts_done": []}


def save_state(st):
    json.dump(st, open(STATE_P, "w", encoding="utf-8"), indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full-batch", type=int, default=1)
    ap.add_argument("--shorts-batch", type=int, default=1)
    ap.add_argument("--full-minutes", type=int, default=10)
    ap.add_argument("--accent", type=str, default="Irish", choices=["Irish", "Australian"])
    args = ap.parse_args()

    st = load_state()
    full_done = set(st.get("full_done", []))
    shorts_done = set(st.get("shorts_done", []))

    all_full = sorted([os.path.basename(p) for p in glob.glob(os.path.join(FULL_DIR, "*.mp4")) if not p.endswith("_REAL_FULL.mp4")])
    all_shorts = sorted([os.path.basename(p) for p in glob.glob(os.path.join(SHORTS_DIR, "*_4D_MAX.mp4"))])

    todo_full = [f for f in all_full if f not in full_done][:args.full_batch]
    todo_shorts = [s for s in all_shorts if s not in shorts_done][:args.shorts_batch]

    print(f"[VAULT ULTRA-HD FACTORY] Upgrading {len(todo_full)} Full-Length (~{args.full_minutes} min) + {len(todo_shorts)} Shorts (1080p/30fps 4D/5D)")
    for fn in todo_full:
        m = re.match(r"Week_(\d+)_(.+?)(?:_4D_MAX)?\.mp4", fn, re.I)
        wk = int(m.group(1)) if m else 1
        topic = (m.group(2) if m else fn.replace(".mp4", "")).replace("_", " ")
        out_p = os.path.join(FULL_DIR, fn)
        r = subprocess.run([
            sys.executable, os.path.join(PDIR, "Modules", "render_real_full_reading.py"),
            "--week", str(wk), "--topic", topic, "--target-minutes", str(args.full_minutes),
            "--accent", args.accent, "--out-file", out_p,
        ])
        if r.returncode == 0:
            full_done.add(fn)
            st["full_done"] = sorted(full_done)
            save_state(st)

    for sn in todo_shorts:
        r = subprocess.run([
            sys.executable, os.path.join(PDIR, "Modules", "render_cinema_short.py"),
            "--short-file", sn, "--accent", args.accent,
        ])
        if r.returncode == 0:
            shorts_done.add(sn)
            st["shorts_done"] = sorted(shorts_done)
            save_state(st)

    print(f"[VAULT PROGRESS] Ultra-HD 4D/5D Full Upgraded: {len(full_done)}/{len(all_full)} | Ultra-HD 4D/5D Shorts Upgraded: {len(shorts_done)}/{len(all_shorts)}")


if __name__ == "__main__":
    main()
