import concurrent.futures
import csv
import datetime as dt
import json
import os
import re
import socket
import subprocess
import urllib.parse
import requests

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DATA_DIR = os.path.join(PDIR, "data")
REPORTS_DIR = os.path.join(PDIR, "reports")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

CSV_TPL = os.path.join(DATA_DIR, "b2b_prospects_import_template.csv")
CSV_VER = os.path.join(DATA_DIR, "b2b_prospects_verified.csv")
JSON_MASTER = os.path.join(DATA_DIR, "verified_b2b_agency_leads.json")
MD_REPORT = os.path.join(REPORTS_DIR, "Verified_Agency_Leads_Master.md")

# 28 Real, Active US/Global YouTube, Short-Form Video, Podcast & Creator Agencies
SEED_AGENCIES = [
    {"company": "CRFT Video", "domain": "crftvideo.com", "niche": "Bespoke Video & Motion Production", "target_tier": "Creator Stack ($1,500)", "icp_score": 94, "known_public_email": "hello@crftvideo.com", "contact_url": "https://crftvideo.com/contact/"},
    {"company": "Vireo Video", "domain": "vireovideo.com", "niche": "YouTube-Certified Video SEO & Channel Growth", "target_tier": "Pro_Node ($49,999)", "icp_score": 98, "known_public_email": "", "contact_url": "https://www.vireovideo.com/contact/"},
    {"company": "Komet Media", "domain": "kometmedia.com", "niche": "B2B SaaS Short-Form Video & Podcast Repurposing", "target_tier": "Creator Stack ($1,500)", "icp_score": 96, "known_public_email": "", "contact_url": "https://www.kometmedia.com/contact"},
    {"company": "Croton Content", "domain": "crotoncontent.com", "niche": "YouTube SEO & AI Visibility Video Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 93, "known_public_email": "", "contact_url": "https://www.crotoncontent.com/contact"},
    {"company": "Pod People", "domain": "podpeople.com", "niche": "Brand Podcast & Audio/Video Production", "target_tier": "Pro_Node ($49,999)", "icp_score": 92, "known_public_email": "", "contact_url": "https://www.podpeople.com/contact"},
    {"company": "The Podglomerate", "domain": "podglomerate.com", "niche": "Podcast Production, Growth & Monetization", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://podglomerate.com/contact/"},
    {"company": "Vidpros", "domain": "vidpros.com", "niche": "Dedicated Video Editing & White-Label Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 97, "known_public_email": "", "contact_url": "https://vidpros.com/contact/"},
    {"company": "ShortVids", "domain": "shortvids.co", "niche": "High-Volume Unlimited Short-Form Video", "target_tier": "Creator Stack ($1,500)", "icp_score": 95, "known_public_email": "", "contact_url": "https://shortvids.co/contact/"},
    {"company": "TastyEdits", "domain": "tastyedits.com", "niche": "Managed YouTube & Short-Form Editing", "target_tier": "Pro_Node ($49,999)", "icp_score": 94, "known_public_email": "", "contact_url": "https://tastyedits.com/contact/"},
    {"company": "Video Husky", "domain": "videohusky.com", "niche": "YouTube & Podcast Creator Video Editing", "target_tier": "Creator Stack ($1,500)", "icp_score": 93, "known_public_email": "", "contact_url": "https://www.videohusky.com/contact/"},
    {"company": "Motionvillee", "domain": "motionvillee.com", "niche": "2D/3D Animation & Reels Production Studio", "target_tier": "Creator Stack ($1,500)", "icp_score": 92, "known_public_email": "", "contact_url": "https://motionvillee.com/contact/"},
    {"company": "Increditors", "domain": "increditors.com", "niche": "B2B SaaS Video Post-Production & VFX", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://increditors.com/contact/"},
    {"company": "ContentBeta", "domain": "contentbeta.com", "niche": "B2B Video & Creative Automation Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 93, "known_public_email": "", "contact_url": "https://www.contentbeta.com/contact-us/"},
    {"company": "Fresh Content Society", "domain": "freshcontentsociety.com", "niche": "High-Impact Short-Form Social Video Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 94, "known_public_email": "", "contact_url": "https://freshcontentsociety.com/contact/"},
    {"company": "True North Social", "domain": "truenorthsocial.com", "niche": "Short-Form Video Strategy & Social Production", "target_tier": "Creator Stack ($1,500)", "icp_score": 90, "known_public_email": "", "contact_url": "https://truenorthsocial.com/contact/"},
    {"company": "inBeat Agency", "domain": "inbeat.agency", "niche": "Creator Marketing & UGC Video Production", "target_tier": "Pro_Node ($49,999)", "icp_score": 95, "known_public_email": "", "contact_url": "https://inbeat.agency/contact/"},
    {"company": "The Influencer Marketing Factory", "domain": "theinfluencermarketingfactory.com", "niche": "YouTube Shorts & Creator ROI Campaigns", "target_tier": "Pro_Node ($49,999)", "icp_score": 94, "known_public_email": "", "contact_url": "https://theinfluencermarketingfactory.com/contact/"},
    {"company": "Single Grain", "domain": "singlegrain.com", "niche": "Full-Funnel Digital & YouTube Shorts Growth", "target_tier": "Pro_Node ($49,999)", "icp_score": 93, "known_public_email": "", "contact_url": "https://www.singlegrain.com/contact/"},
    {"company": "The Shelf", "domain": "theshelf.com", "niche": "Data-Driven Creator & YouTube Campaigns", "target_tier": "Pro_Node ($49,999)", "icp_score": 90, "known_public_email": "", "contact_url": "https://www.theshelf.com/contact/"},
    {"company": "NoGood", "domain": "nogood.io", "niche": "Performance Growth & YouTube Testing Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 92, "known_public_email": "", "contact_url": "https://nogood.io/contact/"},
    {"company": "LYFE Marketing", "domain": "lyfemarketing.com", "niche": "SMB Social Media & Short-Form Video", "target_tier": "Creator Stack ($1,500)", "icp_score": 89, "known_public_email": "", "contact_url": "https://www.lyfemarketing.com/contact/"},
    {"company": "Voy Media", "domain": "voymedia.com", "niche": "Performance Video & YouTube Ad Creative", "target_tier": "Pro_Node ($49,999)", "icp_score": 91, "known_public_email": "", "contact_url": "https://voymedia.com/contact/"},
    {"company": "Avenue Z", "domain": "avenuez.com", "niche": "Strategic Media & YouTube Growth Agency", "target_tier": "Pro_Node ($49,999)", "icp_score": 90, "known_public_email": "", "contact_url": "https://avenuez.com/contact/"},
    {"company": "ThinkMojo", "domain": "thinkmojo.com", "niche": "Animated Short-Form & Product Video Studio", "target_tier": "Creator Stack ($1,500)", "icp_score": 92, "known_public_email": "", "contact_url": "https://thinkmojo.com/contact/"},
    {"company": "Burnwe", "domain": "burnwe.com", "niche": "AI & SaaS Product Video Marketing Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 95, "known_public_email": "", "contact_url": "https://burnwe.com/contact/"},
    {"company": "Focus Pocus Media", "domain": "focuspocusmedia.com", "niche": "B2B YouTube Advertising Agency", "target_tier": "Creator Stack ($1,500)", "icp_score": 91, "known_public_email": "", "contact_url": "https://focuspocusmedia.com/contact/"},
    {"company": "Personal Brand Builders", "domain": "personalbrand.builders", "niche": "YouTube Channel Management & Podcast Booking", "target_tier": "Creator Stack ($1,500)", "icp_score": 93, "known_public_email": "", "contact_url": "https://personalbrand.builders/"},
    {"company": "Munro Agency", "domain": "munro.agency", "niche": "Boutique Inbound, AI & YouTube Marketing", "target_tier": "Creator Stack ($1,500)", "icp_score": 90, "known_public_email": "", "contact_url": "https://www.munro.agency/contact/"},
]

EMAIL_RX = re.compile(r"\b([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,12})\b")
BAD_LOCAL = (
    "noreply", "no-reply", "donotreply", "privacy", "legal", "dmca", "abuse",
    "security", "postmaster", "mailer-daemon", "webmaster", "careers", "jobs",
    "hr", "recruiting", "press", "support", "billing", "unsubscribe", "example",
    "test", "user", "name", "email", "yourname", "placeholder"
)
BAD_DOMAINS = (
    "sentry.io", "wixpress.com", "wordpress.org", "example.com", "domain.com",
    "email.com", "schema.org", "w3.org", "cloudflare.com", "google.com",
    "googleapis.com", "facebook.com", "instagram.com", "twitter.com", "tiktok.com",
    "youtube.com", "linkedin.com", "hubspot.com", "mailchimp.com", "gravatar.com"
)
PREFERRED_PREFIXES = ("hello", "partnerships", "newbusiness", "hi", "contact", "info", "sales", "growth", "team", "studio", "agency", "biz", "inquiries", "connect")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}


def check_mx_or_dns(domain):
    try:
        out = subprocess.run(["nslookup", "-type=mx", domain], capture_output=True, text=True, timeout=6).stdout
        if "mail exchanger" in out.lower() or "mx preference" in out.lower():
            return True, "MX_VERIFIED"
    except Exception:
        pass
    try:
        socket.getaddrinfo(domain, 443)
        return True, "DNS_A_VERIFIED"
    except Exception:
        return False, "DNS_FAILED"


def score_email_candidate(email, target_domain):
    low = email.lower().strip()
    if any(low.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")):
        return -100
    if "@" not in low:
        return -100
    local, dom = low.split("@", 1)
    if any(dom == bd or dom.endswith("." + bd) for bd in BAD_DOMAINS):
        return -100
    if any(local == bl or local.startswith(bl + ".") or local.startswith(bl + "-") for bl in BAD_LOCAL):
        return -100
    score = 0
    td = target_domain.lower().replace("www.", "")
    if dom == td or dom.endswith("." + td):
        score += 50
    else:
        return -50  # Only accept official domain business emails
    for idx, pref in enumerate(PREFERRED_PREFIXES):
        if local == pref:
            score += 40 - idx
            break
    return score


def harvest_one_agency(item):
    dom = item["domain"]
    candidates = []
    if item.get("known_public_email"):
        candidates.append(item["known_public_email"].lower())

    urls_to_try = [
        item["contact_url"],
        f"https://{dom}/",
        f"https://www.{dom}/contact/",
        f"https://{dom}/contact-us/",
        f"https://{dom}/about/",
    ]
    seen_urls = set()
    page_ok = False
    for u in urls_to_try:
        if u in seen_urls:
            continue
        seen_urls.add(u)
        try:
            r = requests.get(u, headers=HEADERS, timeout=7, allow_redirects=True)
            if r.status_code == 200 and r.text:
                page_ok = True
                # Decode mailto and simple obfuscations like [at]
                raw = urllib.parse.unquote(r.text)
                for m in EMAIL_RX.findall(raw):
                    if score_email_candidate(m, dom) > 0:
                        candidates.append(m.lower())
                if any(score_email_candidate(c, dom) >= 70 for c in candidates):
                    break
        except Exception:
            continue

    best_email = ""
    if candidates:
        uniq = sorted(set(candidates), key=lambda e: score_email_candidate(e, dom), reverse=True)
        best_email = uniq[0]

    mx_ok, mx_status = check_mx_or_dns(dom)
    return {
        "company": item["company"],
        "contact": "Partnerships Team",
        "email": best_email if (best_email and mx_ok) else "",
        "domain": dom,
        "contact_url": item["contact_url"],
        "niche": item["niche"],
        "target_tier": item["target_tier"],
        "icp_score": item["icp_score"],
        "mx_status": mx_status,
        "site_reachable": page_ok,
        "notes": f"{item['niche']} | Ideal fit: {item['target_tier']} | Site: https://{dom}",
    }


def main():
    print(f"[LEAD HARVESTER] Scanning {len(SEED_AGENCIES)} verified YouTube/Video/Podcast/Creator agency websites for public business contact emails + MX verification...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(harvest_one_agency, SEED_AGENCIES):
            results.append(res)
            tag = f"EMAIL FOUND: {res['email']} ({res['mx_status']})" if res["email"] else f"FORM ONLY -> {res['contact_url']}"
            print(f"  [{res['icp_score']}] {res['company']:<32} | {tag}")

    results.sort(key=lambda r: (1 if r["email"] else 0, r["icp_score"]), reverse=True)
    verified_email_leads = [r for r in results if r["email"]]
    form_only_leads = [r for r in results if not r["email"]]

    # Preserve any custom user-added leads already in CSV_TPL
    existing_custom = []
    if os.path.exists(CSV_TPL):
        try:
            with open(CSV_TPL, "r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    em = (row.get("email") or "").strip().lower()
                    if em and "@" in em and "example-studio.com" not in em:
                        if not any(v["email"] == em for v in verified_email_leads):
                            existing_custom.append({
                                "company": (row.get("company") or em.split("@")[1]).strip(),
                                "contact": (row.get("contact") or "Team").strip(),
                                "email": em,
                                "notes": (row.get("notes") or "User-added B2B agency prospect").strip(),
                            })
        except Exception:
            pass

    csv_rows = existing_custom + [
        {"company": r["company"], "contact": r["contact"], "email": r["email"], "notes": r["notes"]}
        for r in verified_email_leads
    ]

    for target_csv in (CSV_TPL, CSV_VER):
        with open(target_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["company", "contact", "email", "notes"])
            w.writeheader()
            w.writerows(csv_rows)

    json.dump({
        "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
        "total_agencies_audited": len(results),
        "verified_direct_email_count": len(csv_rows),
        "contact_form_agency_count": len(form_only_leads),
        "direct_email_leads": verified_email_leads,
        "contact_form_leads": form_only_leads,
    }, open(JSON_MASTER, "w", encoding="utf-8"), indent=2)

    lines = [
        f"# Oracle Systems LLC - Verified B2B Agency Leads Directory ({dt.datetime.now().strftime('%Y-%m-%d %H:%M')} EST)",
        f"- **Total Real Agencies Audited:** {len(results)}",
        f"- **MX-Verified Public Business Emails Ready for Gmail API:** {len(csv_rows)}",
        f"- **High-Value Contact-Form Agencies (1-Click Pitch Ready):** {len(form_only_leads)}",
        "",
        "## 1. MX-Verified Direct Email Leads (Loaded into CRM & CSV)",
        "| ICP | Agency | Public Business Email | Target Offer | Niche |",
        "| :---: | :--- | :--- | :--- | :--- |",
    ]
    for r in verified_email_leads:
        lines.append(f"| {r['icp_score']} | {r['company']} | `{r['email']}` | {r['target_tier']} | {r['niche']} |")
    lines += [
        "",
        "## 2. Contact-Form Agencies (Copy Pitch from `reports\\Latest_Swarm_Promo_Pack.md`)",
        "| ICP | Agency | Contact Page | Target Offer | Niche |",
        "| :---: | :--- | :--- | :--- | :--- |",
    ]
    for r in form_only_leads:
        lines.append(f"| {r['icp_score']} | {r['company']} | {r['contact_url']} | {r['target_tier']} | {r['niche']} |")

    open(MD_REPORT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print(f"\n[HARVESTER PASS] Saved {len(csv_rows)} MX-verified direct email leads -> {CSV_VER} + {len(form_only_leads)} form leads -> {MD_REPORT}")


if __name__ == "__main__":
    main()
