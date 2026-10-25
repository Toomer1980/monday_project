import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)

@dataclass
class EnterpriseLead:
    company: str
    annual_revenue: float
    engagement_score: int

def evaluate_lead(lead: EnterpriseLead) -> dict:
    composite = (lead.annual_revenue / 100000.0) * 0.4 + (lead.engagement_score * 0.6)
    tier = "Tier-1 Priority" if composite >= 50 else "Standard Nurture"
    return {
        "company": lead.company,
        "composite_score": round(composite, 2),
        "assigned_tier": tier
    }

if __name__ == "__main__":
    sample = EnterpriseLead("Apex Global Corp", 12000000.0, 88)
    logging.info(f"CRM Evaluation: {evaluate_lead(sample)}")
