import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import csv
import datetime as dt
import json
import sqlite3
import subprocess
import sys
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
CRM_DB = os.path.join(PDIR, "data", "pronode_crm.db")
CSV_IN = os.path.join(PDIR, "data", "b2b_prospects_import_template.csv")
OUTBOX_DIR = os.path.join(PDIR, "deliverables", "b2b_outbox")
os.makedirs(OUTBOX_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CRM_DB), exist_ok=True)


def init_crm():
    c = sqlite3.connect(CRM_DB)
    c.execute(
        "CREATE TABLE IF NOT EXISTS prospects ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "company TEXT, contact TEXT, email TEXT UNIQUE, notes TEXT, "
        "stage TEXT DEFAULT 'NEW', deal_value REAL DEFAULT 1500.0, "
        "last_contacted_utc TEXT DEFAULT '', followup_count INTEGER DEFAULT 0, "
        "created_utc TEXT)"
    )
    # Safely ensure columns exist if an earlier schema created prospects
    cols = {r[1] for r in c.execute("PRAGMA table_info(prospects)").fetchall()}
    for col, ddl in [
        ("notes", "TEXT DEFAULT ''"),
        ("stage", "TEXT DEFAULT 'NEW'"),
        ("deal_value", "REAL DEFAULT 1500.0"),
        ("last_contacted_utc", "TEXT DEFAULT ''"),
        ("followup_count", "INTEGER DEFAULT 0"),
        ("created_utc", "TEXT DEFAULT ''"),
    ]:
        if col not in cols:
            try:
                c.execute(f"ALTER TABLE prospects ADD COLUMN {col} {ddl}")
            except Exception:
                pass
    c.commit()
    c.close()


def get_pub_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "https://oraclesystemsllc.com"


def import_csv(csv_path):
    init_crm()
    if not os.path.exists(csv_path):
        print(f"[B2B IMPORT] CSV not found: {csv_path}")
        return 0
    added = 0
    c = sqlite3.connect(CRM_DB)
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            comp = (row.get("company") or "").strip()
            cont = (row.get("contact") or "Team").strip()
            em = (row.get("email") or "").strip().lower()
            notes = (row.get("notes") or "").strip()
            if not em or "@" not in em or "example-studio.com" in em:
                continue
            cur = c.execute(
                "INSERT OR IGNORE INTO prospects (company, contact, email, notes, stage, deal_value, created_utc) "
                "VALUES (?,?,?,?,?,?,?)",
                (comp or em.split("@")[1], cont, em, notes, "NEW", 1500.0, dt.datetime.utcnow().isoformat() + "Z"),
            )
            if cur.rowcount > 0:
                added += 1
    c.commit()
    total = c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]
    c.close()
    print(f"[B2B IMPORT PASS] Imported {added} new real prospect(s) | Total CRM prospects: {total}")
    return added


def monday_ollama_personalize(company, contact, notes, pub_url):
    stack_url = f"{pub_url}/go/fullstorefront?utm_source=b2b_monday&utm_medium=email&utm_campaign=creator_stack1500"
    pro_url = f"{pub_url}/go/pro_node?utm_source=b2b_monday&utm_medium=email&utm_campaign=pronode49999"
    store_url = f"{pub_url}/store?utm_source=b2b_monday&utm_medium=email&utm_campaign=demo"

    fallback = (
        f"Hi {contact},\n\n"
        f"I came across {company} ({notes or 'your digital media work'}) and wanted to share a live system we built at Oracle Systems LLC.\n\n"
        f"Instead of paying thousands every month across fragmented SaaS tools for video rendering, WebGL landing pages, YouTube publishing, and Stripe checkout automation, "
        f"we deploy private turnkey 4D/5D media & AI stacks you own outright.\n\n"
        f"Live interactive 4D Tesseract & 5D Mobius demo:\n{store_url}\n\n"
        f"Two deployment options for {company}:\n"
        f"1) Turnkey 4D/5D Creator Stack ($1,500 one-time): {stack_url}\n"
        f"2) Enterprise Dedicated Pro_Node Hardware + Full Stack ($49,999, 50% Stripe ACH Milestone 1): {pro_url}\n\n"
        f"Would you like a 10-minute walkthrough or a custom proposal PDF for {company}?\n\n"
        f"Best,\nThomas Toomer\nFounder, Oracle Systems LLC\nReply UNSUBSCRIBE to opt out anytime."
    )

    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as r:
            models = [m.get("name", "") for m in json.loads(r.read().decode("utf-8")).get("models", [])]
        usable = [m for m in models if not any(b in m.lower() for b in (":0.5b", ":1b", ":1.5b", "tinyllama"))]
        if usable:
            prompt = (
                f"Write a concise, respectful, high-converting 140-word B2B email from Thomas Toomer (Founder, Oracle Systems LLC) "
                f"to {contact} at {company} (context: {notes or 'digital media agency'}). "
                f"Highlight cutting monthly SaaS overhead with a private turnkey 4D/5D media & local AI stack. "
                f"Include these exact links verbatim: Live Demo {store_url}, $1,500 Turnkey Stack {stack_url}, and $49,999 Pro_Node {pro_url}. "
                f"End with 'Reply UNSUBSCRIBE to opt out anytime.' Plain text only, no subject line."
            )
            payload = json.dumps({
                "model": usable[0], "prompt": prompt, "stream": False,
                "options": {"temperature": 0.65, "repeat_penalty": 1.22, "num_predict": 260},
            }).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=45) as resp:
                txt = json.loads(resp.read().decode("utf-8")).get("response", "").strip()
                if len(txt) > 120 and stack_url in txt and "UNSUBSCRIBE" in txt.upper():
                    return txt
    except Exception:
        pass
    return fallback


def dispatch_outreach(live=False, daily_cap=10):
    init_crm()
    pub = get_pub_url()
    c = sqlite3.connect(CRM_DB)
    c.row_factory = sqlite3.Row
    rows = c.execute(
        "SELECT * FROM prospects WHERE stage IN ('NEW', 'QUEUED') ORDER BY id ASC LIMIT ?",
        (daily_cap,),
    ).fetchall()

    print(f"[B2B OUTREACH] Mode: {'LIVE GMAIL API' if live else 'DRY-RUN STAGING'} | Queued: {len(rows)} (cap={daily_cap})")
    sent = 0
    for r in rows:
        comp = r["company"] or "Partner"
        cont = r["contact"] or "Team"
        em = r["email"] or ""
        notes = r["notes"] if "notes" in r.keys() else ""
        if not em or "@" not in em:
            continue
        subj = f"Private 4D/5D AI & Media Stack for {comp} (Zero Monthly SaaS Lock-In)"
        body = monday_ollama_personalize(comp, cont, notes, pub)

        draft_p = os.path.join(OUTBOX_DIR, f"draft_{r['id']}_{em.replace('@','_at_')}.txt")
        open(draft_p, "w", encoding="utf-8", newline="").write(f"To: {em}\nSubject: {subj}\n\n{body}\n")

        if live:
            sys.path.insert(0, os.path.join(PDIR, "Modules"))
            from google_mail_engine import send_oracle_email
            via = send_oracle_email(PDIR, em, subj, body)
            c.execute(
                "UPDATE prospects SET stage='CONTACTED', last_contacted_utc=? WHERE id=?",
                (dt.datetime.utcnow().isoformat() + "Z", r["id"]),
            )
            c.commit()
            sent += 1
            print(f"  [SENT LIVE] {comp} <{em}> via {via}")
        else:
            print(f"  [STAGED DRAFT] {comp} <{em}> -> {os.path.basename(draft_p)}")

    c.close()
    # Auto-regenerate PDF proposals for all CRM prospects
    prop_py = os.path.join(PDIR, "Modules", "pronode_proposal_gen.py")
    if os.path.exists(prop_py):
        subprocess.run([sys.executable, prop_py], check=False)
    print(f"[B2B ENGINE PASS] Staged {len(rows)} outreach email(s) | Sent live: {sent}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default=CSV_IN)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--cap", type=int, default=10)
    args = ap.parse_args()
    import_csv(args.csv)
    dispatch_outreach(live=args.live, daily_cap=args.cap)
