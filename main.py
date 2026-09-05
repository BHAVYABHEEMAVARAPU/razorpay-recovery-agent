from fastapi import FastAPI
import json
from engine import evaluate_recovery

app = FastAPI()

@app.post("/run-recovery-batch")
def run_batch():
    try:
        with open("data.json", "r") as f:
            transactions = json.load(f)
    except FileNotFoundError:
        return {"error": "data.json file not found. Please create it first."}
        
    results = []
    total_at_risk = 0.0
    recovered_amount = 0.0
    
    for tx in transactions:
        total_at_risk += tx.get("amount", 0.0)
        decision = evaluate_recovery(tx)
        
        if decision["action"] == "RETRY_IMMEDIATE":
            recovered_amount += tx.get("amount", 0.0)
            
        results.append({
            "transaction_id": tx.get("transaction_id"),
            "decision": decision["action"],
            "rationale": decision["reason"]
        })
        
    return {
        "metrics": {
            "total_records_processed": len(transactions),
            "total_revenue_at_risk": total_at_risk,
            "net_revenue_recovered": recovered_amount,
            "recovery_efficiency_percentage": (recovered_amount / total_at_risk) * 100 if total_at_risk > 0 else 0
        },
        "audit_trail": results
    }