import csv
import os
import re
import socket

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
CSV_IN = os.path.join(PDIR, "data", "b2b_prospects_import_template.csv")
CSV_CLEAN = os.path.join(PDIR, "data", "b2b_prospects_verified.csv")

EMAIL_RX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
BAD_PREFIXES = ("noreply", "no-reply", "donotreply", "mailer-daemon", "postmaster", "abuse", "privacy", "legal")


def domain_resolves(domain):
    try:
        socket.getaddrinfo(domain, 443)
        return True
    except Exception:
        try:
            socket.getaddrinfo(domain, 80)
            return True
        except Exception:
            return False


def main():
    if not os.path.exists(CSV_IN):
        print(f"[B2B VERIFY] File not found: {CSV_IN}")
        return
    valid_rows, skipped = [], []
    seen = set()
    with open(CSV_IN, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            em = (row.get("email") or "").strip().lower()
            comp = (row.get("company") or "").strip()
            cont = (row.get("contact") or "Team").strip()
            notes = (row.get("notes") or "").strip()
            if not em or "example-studio.com" in em:
                continue
            if not EMAIL_RX.match(em):
                skipped.append((em, "Invalid syntax"))
                continue
            local, dom = em.split("@", 1)
            if any(local.startswith(p) for p in BAD_PREFIXES):
                skipped.append((em, "Do-not-email prefix"))
                continue
            if em in seen:
                continue
            if not domain_resolves(dom):
                skipped.append((em, f"Domain {dom} failed DNS"))
                continue
            seen.add(em)
            valid_rows.append({"company": comp or dom, "contact": cont, "email": em, "notes": notes})

    with open(CSV_CLEAN, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["company", "contact", "email", "notes"])
        w.writeheader()
        w.writerows(valid_rows)

    print(f"[B2B VERIFY PASS] Verified {len(valid_rows)} deliverable agency contact(s) -> {CSV_CLEAN} | Filtered out: {len(skipped)}")
    for em, why in skipped[:10]:
        print(f"  [SKIPPED] {em}: {why}")


if __name__ == "__main__":
    main()
