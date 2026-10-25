import logging
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Oracle Systems LLC Automated Billing & Tax Engine", version="4.1.0")
logging.basicConfig(level=logging.INFO)

class RevenueLedger(BaseModel):
    client_id: str
    gross_amount: float
    currency: str = "USD"

@app.get("/auto-status")
def status():
    return {
        "status": "active",
        "service": "billing_reconciliation_node",
        "ein": "82-4737196",
        "autonomous": True,
        "port": 8001
    }

@app.post("/api/v1/billing/reconcile")
async def reconcile_revenue(ledger: RevenueLedger):
    tax_reserve = round(ledger.gross_amount * 0.22, 2)
    net_revenue = round(ledger.gross_amount - tax_reserve, 2)
    logging.info(f"Reconciled: Gross=${ledger.gross_amount} | Tax=${tax_reserve} | Net=${net_revenue}")
    return {
        "status": "reconciled",
        "ein": "82-4737196",
        "client_id": ledger.client_id,
        "gross": ledger.gross_amount,
        "tax_reserve": tax_reserve,
        "net_operational": net_revenue,
        "currency": ledger.currency
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
