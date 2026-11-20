import csv
import datetime as dt
import os
import re
import sqlite3
import sys

EMAIL_RX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
FREE_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com", "protonmail.com", "live.com"}
BLOCKED_DOMAINS = {"example.com", "prospect.com", "test.com", "mailinator.com", "tempmail.com", "yourdomain.com"}
BLOCKED_PREFIXES = ("noreply@", "no-reply@", "donotreply@", "mailer-daemon@", "postmaster@", "unsubscribe@")

HIGH_FIT_KW = ["agency", "media", "studio", "production", "video", "ai", "automation", "digital", "marketing", "consulting", "enterprise", "saas", "labs", "ventures", "holdings", "capital", "tech", "software"]
DECISION_TITLES = ["founder", "co-founder", "ceo", "chief", "coo", "cto", "president", "managing", "partner", "owner", "vp", "director", "head of"]


def pick_col(row_lower, candidates):
    for c in candidates:
        if c in row_lower and (row_lower[c] or "").strip():
            return row_lower[c].strip()
    return ""


def score_lead(company, contact, email, title, industry, notes):
    score = 40
    reasons = []
    dom = email.split("@", 1)[1].lower() if "@" in email else ""
    if dom and dom not in FREE_DOMAINS:
        score += 20
        reasons.append("corporate_domain")
    else:
        reasons.append("free_email")

    blob = f"{company} {industry} {notes}".lower()
    if any(k in blob for k in HIGH_FIT_KW):
        score += 20
        reasons.append("icp_industry")

    t_blob = f"{title} {contact} {notes}".lower()
    if any(k in t_blob for k in DECISION_TITLES):
        score += 15
        reasons.append("decision_maker")

    if contact and len(contact.split()) >= 2:
        score += 5
        reasons.append("named_contact")

    return min(100, score), ",".join(reasons)


def load_existing_crm_emails(db_path):
    existing = set()
    if not os.path.exists(db_path):
        return existing
    try:
        conn = sqlite3.connect(db_path)
        for (em,) in conn.execute("SELECT lower(email) FROM prospects").fetchall():
            if em:
                existing.add(em.strip().lower())
        conn.close()
    except Exception:
        pass
    return existing


def main():
    pdir = sys.argv[1]
    in_csv = sys.argv[2]
    out_csv = sys.argv[3]
    min_score = int(sys.argv[4]) if len(sys.argv) > 4 else 50

    if not os.path.exists(in_csv):
        print(f"[ERROR] Input CSV not found: {in_csv}")
        sys.exit(1)

    crm_emails = load_existing_crm_emails(os.path.join(pdir, "data", "pronode_crm.db"))
    seen_emails = set()
    accepted = []
    skipped = {"invalid_email": 0, "placeholder_or_blocked": 0, "duplicate_csv": 0, "duplicate_crm": 0, "below_min_score": 0}
    next_day = (dt.date.today() + dt.timedelta(days=1)).isoformat()

    with open(in_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            rl = {(k or "").strip().lower(): (v or "").strip() for k, v in raw_row.items()}
            email = pick_col(rl, ["email", "email address", "work email", "contact email", "e-mail"]).lower()
            if not email or not EMAIL_RX.match(email):
                skipped["invalid_email"] += 1
                continue

            dom = email.split("@", 1)[1]
            if dom in BLOCKED_DOMAINS or email.startswith(BLOCKED_PREFIXES):
                skipped["placeholder_or_blocked"] += 1
                continue
            if email in seen_emails:
                skipped["duplicate_csv"] += 1
                continue
            if email in crm_emails:
                skipped["duplicate_crm"] += 1
                continue

            company = pick_col(rl, ["company", "company name", "organization", "business", "account", "agency"])
            if not company:
                company = dom.split(".")[0].replace("-", " ").title()

            first = pick_col(rl, ["first name", "first", "fname"])
            last = pick_col(rl, ["last name", "last", "lname"])
            contact = pick_col(rl, ["contact", "contact name", "full name", "name"]) or f"{first} {last}".strip() or "Leadership Team"
            title = pick_col(rl, ["title", "job title", "role", "position"])
            industry = pick_col(rl, ["industry", "sector", "niche", "category"])
            website = pick_col(rl, ["website", "url", "domain"])
            notes_raw = pick_col(rl, ["notes", "note", "pain point", "context"])

            score, tags = score_lead(company, contact, email, title, industry, notes_raw)
            if score < min_score:
                skipped["below_min_score"] += 1
                continue

            seen_emails.add(email)
            note_parts = [p for p in [title, industry, website, notes_raw, f"ICP:{score} ({tags})"] if p]
            accepted.append({
                "company": company,
                "contact": contact,
                "email": email,
                "stage": "Lead",
                "next_followup": next_day,
                "icp_score": score,
                "notes": " | ".join(note_parts),
            })

    accepted.sort(key=lambda r: (-r["icp_score"], r["company"].lower()))

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    fields = ["company", "contact", "email", "stage", "next_followup", "notes", "icp_score"]
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(accepted)

    print(f"=== PRO_NODE ($49,999) B2B LEAD FORMATTER COMPLETE ===")
    print(f"Input CSV : {in_csv}")
    print(f"Output CSV: {out_csv}")
    print(f"Qualified : {len(accepted)} lead(s) (Min ICP Score: {min_score})")
    print(f"Filtered  : invalid={skipped['invalid_email']}, blocked/placeholder={skipped['placeholder_or_blocked']}, dup_csv={skipped['duplicate_csv']}, dup_crm={skipped['duplicate_crm']}, low_score={skipped['below_min_score']}")

    if accepted:
        print("\nTop Ranked Prospects (Ready for Weekly 20-Lead Sprint):")
        for idx, r in enumerate(accepted[:10], 1):
            print(f"  {idx:2d}. [ICP {r['icp_score']:3d}] {r['company']} ({r['contact']} <{r['email']}>)")
        top = accepted[0]
        print("\n--- SAMPLE PERSONALIZED PRO_NODE ($49,999) OUTREACH PREVIEW ---")
        print(f"To     : {top['contact']} <{top['email']}>")
        print(f"Subject: Dedicated Sovereign AI Node for {top['company']} (3-Min Live Sandbox)")
        print(f"Body   : Hi {top['contact'].split()[0]}, we built Oracle Systems Pro_Node so teams like {top['company']} run autonomous 4D media, CRM, and local LLM pipelines on dedicated hardware without per-seat SaaS lock-in ($24,999.50 M1 ACH deposit / $49,999 turnkey). Open to a 3-minute live sandbox walkthrough this week?")


if __name__ == "__main__":
    main()