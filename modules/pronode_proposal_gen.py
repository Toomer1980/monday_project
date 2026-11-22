import datetime as dt
import os
import re
import sqlite3
import subprocess
import sys

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
CRM_DB = os.path.join(PDIR, "data", "pronode_crm.db")
OUT_DIR = os.path.join(PDIR, "deliverables", "proposals")
os.makedirs(OUT_DIR, exist_ok=True)


def ensure_fpdf():
    try:
        from fpdf import FPDF  # noqa
        return True
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "fpdf2"], check=False)
        try:
            from fpdf import FPDF  # noqa
            return True
        except ImportError:
            return False


def get_public_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "https://oraclesystemsllc.com"


def generate_proposal_pdf(company, contact, email):
    slug = re.sub(r"[^A-Za-z0-9]+", "_", company).strip("_") or "Enterprise_Client"
    out_pdf = os.path.join(OUT_DIR, f"OracleSystems_ProNode_Proposal_{slug}.pdf")
    out_md = os.path.join(OUT_DIR, f"OracleSystems_ProNode_Proposal_{slug}.md")
    pub = get_public_url()
    today = dt.date.today().strftime("%B %d, %Y")

    md_text = (
        f"# ORACLE SYSTEMS LLC - TURNKEY SOVEREIGN AI & MEDIA PROPOSAL\n"
        f"- **Prepared For:** {company} ({contact} <{email}>)\n"
        f"- **Date:** {today} | **Prepared By:** Thomas Toomer, Founder - Oracle Systems LLC\n\n"
        f"## 1. Executive Architecture\n"
        f"Eliminate fragmented monthly SaaS seat fees with a dedicated, private autonomous media, CRM, and local AI compute stack:\n"
        f"- **Living 3D WebGL Storefront & Stripe Webhook Automation** (Live Preview: {pub}/store)\n"
        f"- **Autonomous 52-Week 24fps Cinema Media Pipeline** (YouTube Data API v3 + UCB1 Performance Engine)\n"
        f"- **Private Local LLM Inference & Automated B2B Outreach Engine** (Gmail API HTTPS/443 + SQLite CRM)\n\n"
        f"## 2. Deployment Options\n"
        f"- **Option A - Turnkey Creator Stack Software Deployment:** $1,500 one-time ({pub}/go/fullstorefront)\n"
        f"- **Option B - Dedicated Enterprise Pro_Node Hardware + Full Stack:** $49,999 ($24,999.50 Milestone 1 Stripe ACH deposit)\n"
        f"  Reserve Link: {pub}/go/pro_node\n"
    )
    open(out_md, "w", encoding="utf-8", newline="").write(md_text)

    if ensure_fpdf():
        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=16)
        pdf.add_page()
        pdf.set_fill_color(4, 7, 18)
        pdf.rect(0, 0, 210, 36, "F")
        pdf.set_text_color(250, 204, 21)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_xy(14, 10)
        pdf.cell(0, 8, "ORACLE SYSTEMS LLC // PRO_NODE EXECUTIVE PROPOSAL", ln=True)
        pdf.set_text_color(186, 230, 253)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(14)
        pdf.cell(0, 6, f"Prepared for {company} ({contact})  |  {today}", ln=True)

        pdf.set_y(44)
        pdf.set_text_color(20, 24, 38)
        for title, body in [
            ("1. Turnkey Autonomous AI & 3D Media Stack",
             f"Oracle Systems LLC deploys private, zero-per-seat autonomous media pipelines, live WebGL 3D storefronts, Stripe instant fulfillment webhooks, and local LLM CRM automation for {company}."),
            ("2. Verified Production Capabilities",
             f"- Live 3D WebGL Storefront & Interactive Preview: {pub}/store\n- 24fps Living-Card Video Rendering + Warm Studio Neural Narration\n- YouTube Data API v3 Auto-Publishing + UCB1 Conversion Telemetry\n- Automated Gmail API HTTPS/443 Outreach, 3-Day Follow-Ups & Cloud DR Backups"),
            ("3. Investment & Milestone Terms",
             f"- Turnkey Creator Stack Software License: $1,500 one-time ({pub}/go/fullstorefront)\n- Enterprise Dedicated Pro_Node Deployment: $49,999 turnkey\n  * Milestone 1 (50% ACH Deposit via Stripe): $24,999.50\n  * Milestone 2 (Final Acceptance & Cutover): $24,999.50\n  * Direct Reservation Portal: {pub}/go/pro_node"),
        ]:
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 35, 80)
            pdf.cell(0, 8, title, ln=True)
            pdf.set_font("Helvetica", "", 10.5)
            pdf.set_text_color(35, 40, 52)
            pdf.multi_cell(0, 6, body)
            pdf.ln(4)
        pdf.output(out_pdf)
        return out_pdf
    return out_md


def main():
    built = []
    if os.path.exists(CRM_DB):
        c = sqlite3.connect(CRM_DB)
        rows = c.execute("SELECT company, contact, email FROM prospects ORDER BY id ASC LIMIT 1000").fetchall()
        c.close()
        for comp, cont, em in rows:
            built.append(generate_proposal_pdf(comp or "Partner", cont or "Executive Team", em or ""))
    if not built:
        built.append(generate_proposal_pdf("Oracle Enterprise Template", "Managing Partner", "Toomer1980@gmail.com"))
    print(f"[PHASE 35 PASS] Generated {len(built)} B2B Pro_Node executive proposal(s) -> {OUT_DIR}")
    for b in built:
        print(f"  -> {os.path.basename(b)}")


if __name__ == "__main__":
    main()


