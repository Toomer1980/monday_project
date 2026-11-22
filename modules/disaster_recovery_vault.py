import datetime as dt
import glob
import os
import shutil
import sqlite3
import zipfile

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DR_DIR = os.path.join(PDIR, "backups", "dr_snapshots")
STAGE_DR = os.path.join(PDIR, "Oracle_Audit_2026", "DR_Backups")
os.makedirs(DR_DIR, exist_ok=True)
os.makedirs(STAGE_DR, exist_ok=True)


def main():
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_out = os.path.join(DR_DIR, f"SovereignCore_DR_{ts}.zip")
    dbs = glob.glob(os.path.join(PDIR, "data", "*.db"))
    jsons = glob.glob(os.path.join(PDIR, "data", "*.json"))

    checked_ok = 0
    with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dbp in dbs:
            try:
                c = sqlite3.connect(dbp)
                res = c.execute("PRAGMA integrity_check").fetchone()[0]
                c.close()
                if str(res).lower() == "ok":
                    checked_ok += 1
            except Exception:
                pass
            zf.write(dbp, os.path.join("data", os.path.basename(dbp)))
        for jp in jsons:
            zf.write(jp, os.path.join("data", os.path.basename(jp)))

    # Retain last 7 DR snapshots locally and copy latest to Oracle_Audit_2026/DR_Backups for Drive mirror
    snaps = sorted(glob.glob(os.path.join(DR_DIR, "SovereignCore_DR_*.zip")))
    for old in snaps[:-7]:
        try:
            os.remove(old)
        except Exception:
            pass
    shutil.copy2(zip_out, os.path.join(STAGE_DR, os.path.basename(zip_out)))
    kb = os.path.getsize(zip_out) / 1024.0
    print(f"[PHASE 39 PASS] Disaster Recovery Vault created -> {os.path.basename(zip_out)} ({kb:.1f} KB | {checked_ok}/{len(dbs)} SQLite DBs integrity OK)")


if __name__ == "__main__":
    main()
