import os
import sqlite3

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
CRM_DB = os.path.join(PDIR, "data", "pronode_crm.db")
ENGINE_PY = os.path.join(PDIR, "Modules", "b2b_client_acquisition_engine.py")


def dedupe_crm():
    if not os.path.exists(CRM_DB):
        print("[CRM-DEDUPE] pronode_crm.db not found yet.")
        return
    c = sqlite3.connect(CRM_DB)
    c.row_factory = sqlite3.Row
    rows = c.execute("SELECT * FROM prospects ORDER BY id ASC").fetchall()
    before = len(rows)

    # Group by lowercase email; keep CONTACTED/REPLIED rows over NEW rows
    rank = {"REPLIED": 4, "PROPOSAL": 3, "CONTACTED": 2, "QUEUED": 1, "NEW": 0}
    keep_by_email = {}
    delete_ids = []
    for r in rows:
        em = (r["email"] or "").strip().lower()
        if not em:
            continue
        st = (r["stage"] or "NEW").upper() if "stage" in r.keys() else "NEW"
        sc = rank.get(st, 0)
        if em not in keep_by_email:
            keep_by_email[em] = (r["id"], sc)
        else:
            prev_id, prev_sc = keep_by_email[em]
            if sc > prev_sc:
                delete_ids.append(prev_id)
                keep_by_email[em] = (r["id"], sc)
            else:
                delete_ids.append(r["id"])

    for did in delete_ids:
        c.execute("DELETE FROM prospects WHERE id=?", (did,))

    # Normalize all emails to lowercase & enforce case-insensitive UNIQUE index
    c.execute("UPDATE prospects SET email = LOWER(TRIM(email)) WHERE email IS NOT NULL")
    try:
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_prospects_email_unique ON prospects(email COLLATE NOCASE)")
    except Exception as ex:
        print(f"[CRM-DEDUPE NOTE] Index note: {ex}")

    c.commit()
    after = c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]
    contacted = c.execute("SELECT COUNT(*) FROM prospects WHERE UPPER(COALESCE(stage,''))='CONTACTED'").fetchone()[0]
    queued_new = c.execute("SELECT COUNT(*) FROM prospects WHERE UPPER(COALESCE(stage,'NEW')) IN ('NEW','QUEUED')").fetchone()[0]
    c.close()
    print(f"[CRM-DEDUPE PASS] Cleaned {len(delete_ids)} duplicate row(s) ({before} -> {after} unique prospects) | Contacted: {contacted} | Ready for Next Batch: {queued_new}")


def patch_engine_import_guard():
    """Ensure b2b_client_acquisition_engine.py checks LOWER(email) explicitly before inserting."""
    if not os.path.exists(ENGINE_PY):
        return
    src = open(ENGINE_PY, "r", encoding="utf-8").read()
    marker = "SELECT 1 FROM prospects WHERE LOWER(email)=?"
    if marker in src:
        print("[CRM-GUARD PASS] b2b_client_acquisition_engine.py already has explicit email dedupe guard.")
        return
    old_snip = '            cur = c.execute(\n                "INSERT OR IGNORE INTO prospects'
    new_snip = (
        '            if c.execute("SELECT 1 FROM prospects WHERE LOWER(email)=?", (em,)).fetchone():\n'
        '                continue\n'
        '            cur = c.execute(\n'
        '                "INSERT OR IGNORE INTO prospects'
    )
    if old_snip in src:
        open(ENGINE_PY, "w", encoding="utf-8", newline="").write(src.replace(old_snip, new_snip, 1))
        print("[CRM-GUARD PASS] Patched b2b_client_acquisition_engine.py with explicit LOWER(email) duplicate guard.")


if __name__ == "__main__":
    dedupe_crm()
    patch_engine_import_guard()
