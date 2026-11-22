import concurrent.futures
import csv
import datetime as dt
import json
import os
import sys

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
sys.path.insert(0, os.path.join(PDIR, "Modules"))
import b2b_public_lead_harvester as hmod

DATA_DIR = os.path.join(PDIR, "data")
REPORTS_DIR = os.path.join(PDIR, "reports")
CSV_TPL = os.path.join(DATA_DIR, "b2b_prospects_import_template.csv")
CSV_VER = os.path.join(DATA_DIR, "b2b_prospects_verified.csv")
JSON_MASTER = os.path.join(DATA_DIR, "verified_b2b_agency_leads.json")
MD_REPORT = os.path.join(REPORTS_DIR, "Verified_Agency_Leads_Master.md")

# Wave 2: 30 Additional Real B2B Video, Podcast Production, SaaS Animation & Creator Agencies
WAVE2_AGENCIES = [
    {"company": "Lemonlight", "domain": "lemonlight.com", "niche": "On-Demand Brand Video Production at Scale", "target_tier": "Pro_Node ($49,999)", "icp_score": 96, "known_public_email": "", "contact_url": "https://www.lemonlight.com/contact/"},
    {"company": "Vidico", "domain": "vidico.com", "niche": "B2B SaaS & Tech Video Production Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 97, "known_public_email": "", "contact_url": "https://vidico.com/contact/"},
    {"company": "Demo Duck", "domain": "demoduck.com", "niche": "Explainer & Commercial Video Studio", "target_tier": "Creator Stack ($1,500)", "icp_score": 93, "known_public_email": "", "contact_url": "https://demoduck.com/contact/"},
    {"company": "Yum Yum Videos", "domain": "yumyumvideos.com", "niche": "B2B Animated Explainer & Marketing Videos", "target_tier": "Creator Stack ($1,500)", "icp_score": 94, "known_public_email": "", "contact_url": "https://www.yumyumvideos.com/contact/"},
    {"company": "Wyzowl", "domain": "wyzowl.com", "niche": "Animated Explainer & SaaS Video Studio", "target_tier": "Pro_Node ($49,999)", "icp_score": 95, "known_public_email": "", "contact_url": "https://www.wyzowl.com/contact/"},
    {"company": "Epipheo", "domain": "epipheo.com", "niche": "B2B Explainer & Story Video Production", "target_tier": "Creator Stack ($1,500)", "icp_score": 92, "known_public_email": "", "contact_url": "https://epipheo.com/contact/"},
    {"company": "Explainify", "domain": "explainify.com", "niche": "Enterprise Explainer & Animated Video Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://explainify.com/contact/"},
    {"company": "Breadnbeyond", "domain": "breadnbeyond.com", "niche": "Motion Graphics & Explainer Video Studio", "target_tier": "Creator Stack ($1,500)", "icp_score": 92, "known_public_email": "", "contact_url": "https://breadnbeyond.com/contact/"},
    {"company": "MotionGility", "domain": "motiongility.com", "niche": "B2B SaaS & Tech Explainer Video Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 93, "known_public_email": "", "contact_url": "https://motiongility.com/contact-us/"},
    {"company": "Kasra Design", "domain": "kasradesign.com", "niche": "3D Animation & Commercial Video Studio", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://www.kasradesign.com/contact/"},
    {"company": "Lower Street", "domain": "lowerstreet.co", "niche": "B2B Branded Podcast Production Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 94, "known_public_email": "", "contact_url": "https://lowerstreet.co/contact"},
    {"company": "Quill Podcasting", "domain": "quillpodcasting.com", "niche": "Full-Service Brand Podcast Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 93, "known_public_email": "", "contact_url": "https://www.quillpodcasting.com/contact"},
    {"company": "Sweet Fish Media", "domain": "sweetfishmedia.com", "niche": "B2B Podcast & Short-Form Video Content", "target_tier": "Pro_Node ($49,999)", "icp_score": 96, "known_public_email": "", "contact_url": "https://sweetfishmedia.com/contact/"},
    {"company": "Fame B2B Podcasting", "domain": "fame.so", "niche": "B2B Podcast Growth & YouTube Clips Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 95, "known_public_email": "", "contact_url": "https://www.fame.so/contact"},
    {"company": "Come Alive Creative", "domain": "comealivecreative.com", "niche": "Branded Podcast & Video Production", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://comealivecreative.com/contact/"},
    {"company": "Pacific Content", "domain": "pacific-content.com", "niche": "Enterprise Branded Audio & Podcast Studio", "target_tier": "Pro_Node ($49,999)", "icp_score": 92, "known_public_email": "", "contact_url": "https://pacific-content.com/contact/"},
    {"company": "JAR Audio", "domain": "jaraudio.com", "niche": "Brand Podcast Strategy & Production Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://jaraudio.com/contact/"},
    {"company": "Content Allies", "domain": "contentallies.com", "niche": "B2B Executive Podcast & Video Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 94, "known_public_email": "", "contact_url": "https://contentallies.com/contact"},
    {"company": "Resonate Recordings", "domain": "resonaterecordings.com", "niche": "Podcast & Video Post-Production Studio", "target_tier": "Pro_Node ($49,999)", "icp_score": 93, "known_public_email": "", "contact_url": "https://resonaterecordings.com/contact/"},
    {"company": "Billo Creator Video", "domain": "billo.app", "niche": "Creator Video Ads & Performance Production", "target_tier": "Pro_Node ($49,999)", "icp_score": 93, "known_public_email": "", "contact_url": "https://billo.app/contact-us/"},
    {"company": "Viral Nation", "domain": "viralnation.com", "niche": "Creator Talent, Social Video & AI Marketing", "target_tier": "Pro_Node ($49,999)", "icp_score": 95, "known_public_email": "", "contact_url": "https://www.viralnation.com/contact/"},
    {"company": "Ubiquitous", "domain": "ubiquitousinfluence.com", "niche": "YouTube & TikTok Creator Campaign Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 93, "known_public_email": "", "contact_url": "https://www.ubiquitousinfluence.com/contact"},
    {"company": "Sparkhouse", "domain": "thesparkhouse.com", "niche": "Commercial Brand Video & Social Ads Studio", "target_tier": "Creator Stack ($1,500)", "icp_score": 92, "known_public_email": "", "contact_url": "https://www.thesparkhouse.com/contact/"},
    {"company": "VeracityColab", "domain": "veracitycolab.com", "niche": "Video Creative & Brand Storytelling Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://www.veracitycolab.com/contact/"},
    {"company": "Beverley & Co / Think Branded", "domain": "thinkbrandedmedia.com", "niche": "Brand Video & Digital Content Production", "target_tier": "Creator Stack ($1,500)", "icp_score": 90, "known_public_email": "", "contact_url": "https://thinkbrandedmedia.com/contact/"},
    {"company": "Ydraw", "domain": "ydraw.com", "niche": "Animated Marketing & Explainer Videos", "target_tier": "Creator Stack ($1,500)", "icp_score": 90, "known_public_email": "", "contact_url": "https://ydraw.com/contact-us/"},
    {"company": "IdeaRocket", "domain": "idearocketanimation.com", "niche": "2D/3D B2B Animation & Video Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://idearocketanimation.com/contact/"},
    {"company": "Gisteo", "domain": "gisteo.com", "niche": "Explainer Video & Creator Motion Studio", "target_tier": "Creator Stack ($1,500)", "icp_score": 90, "known_public_email": "", "contact_url": "https://gisteo.com/contact/"},
    {"company": "Digital Brew", "domain": "digitalbrew.com", "niche": "Emmy-Winning Explainer & Brand Video Studio", "target_tier": "Pro_Node ($49,999)", "icp_score": 94, "known_public_email": "", "contact_url": "https://www.digitalbrew.com/contact/"},
    {"company": "MotionCue", "domain": "motioncue.com", "niche": "B2B Video Marketing & Motion Design Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 93, "known_public_email": "", "contact_url": "https://motioncue.com/contact/"},
]


def main():
    prev = json.load(open(JSON_MASTER, "r", encoding="utf-8")) if os.path.exists(JSON_MASTER) else {}
    existing_direct = list(prev.get("direct_email_leads") or [])
    existing_forms = list(prev.get("contact_form_leads") or [])
    seen_domains = {r.get("domain", "").lower() for r in existing_direct + existing_forms}

    to_scan = [a for a in WAVE2_AGENCIES if a["domain"].lower() not in seen_domains]
    print(f"[WAVE 2 HARVESTER] Auditing {len(to_scan)} new B2B Video, Podcast & Animation Agencies (skipping {len(WAVE2_AGENCIES)-len(to_scan)} already scanned)...")

    new_direct, new_forms = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(hmod.harvest_one_agency, to_scan):
            if res["email"]:
                new_direct.append(res)
                print(f"  [{res['icp_score']}] {res['company']:<32} | EMAIL FOUND: {res['email']} ({res['mx_status']})")
            elif res["site_reachable"]:
                new_forms.append(res)
                print(f"  [{res['icp_score']}] {res['company']:<32} | FORM ONLY -> {res['contact_url']}")
            else:
                print(f"  [--] {res['company']:<32} | Site unreachable / timeout, skipped")

    all_direct = sorted(existing_direct + new_direct, key=lambda r: r.get("icp_score", 0), reverse=True)
    # Dedupe direct by email
    dedup_direct, seen_em = [], set()
    for r in all_direct:
        em = (r.get("email") or "").lower().strip()
        if em and em not in seen_em:
            seen_em.add(em)
            dedup_direct.append(r)

    all_forms = sorted(existing_forms + new_forms, key=lambda r: r.get("icp_score", 0), reverse=True)
    dedup_forms, seen_fd = [], set()
    for r in all_forms:
        dm = (r.get("domain") or "").lower().strip()
        if dm and dm not in seen_fd:
            seen_fd.add(dm)
            dedup_forms.append(r)

    csv_rows = [
        {"company": r["company"], "contact": r.get("contact") or "Partnerships Team", "email": r["email"], "notes": r["notes"]}
        for r in dedup_direct
    ]
    for target_csv in (CSV_TPL, CSV_VER):
        with open(target_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["company", "contact", "email", "notes"])
            w.writeheader()
            w.writerows(csv_rows)

    json.dump({
        "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
        "total_agencies_audited": len(dedup_direct) + len(dedup_forms),
        "verified_direct_email_count": len(dedup_direct),
        "contact_form_agency_count": len(dedup_forms),
        "direct_email_leads": dedup_direct,
        "contact_form_leads": dedup_forms,
    }, open(JSON_MASTER, "w", encoding="utf-8"), indent=2)

    lines = [
        f"# Oracle Systems LLC - Verified B2B Agency Leads Directory (Wave 1 + Wave 2 | {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} EST)",
        f"- **Total Verified Active Agencies:** {len(dedup_direct) + len(dedup_forms)}",
        f"- **MX-Verified Direct Business Emails (Gmail API Ready):** {len(dedup_direct)} (+{len(new_direct)} new in Wave 2)",
        f"- **Contact-Form Agencies:** {len(dedup_forms)} (+{len(new_forms)} new in Wave 2)",
        "",
        "## 1. MX-Verified Direct Email Leads",
        "| ICP | Agency | Public Business Email | Target Offer | Niche |",
        "| :---: | :--- | :--- | :--- | :--- |",
    ]
    for r in dedup_direct:
        lines.append(f"| {r['icp_score']} | {r['company']} | `{r['email']}` | {r['target_tier']} | {r['niche']} |")
    lines += [
        "",
        "## 2. High-Value Contact-Form Agencies",
        "| ICP | Agency | Contact Page | Target Offer | Niche |",
        "| :---: | :--- | :--- | :--- | :--- |",
    ]
    for r in dedup_forms:
        lines.append(f"| {r['icp_score']} | {r['company']} | {r['contact_url']} | {r['target_tier']} | {r['niche']} |")
    open(MD_REPORT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")

    print(f"\n[WAVE 2 PASS] +{len(new_direct)} new MX-verified direct emails (Total: {len(dedup_direct)}) | +{len(new_forms)} new contact-form agencies (Total: {len(dedup_forms)})")


if __name__ == "__main__":
    main()
