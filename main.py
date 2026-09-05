import json
import os
from pathlib import Path
from typing import Optional

import requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from agent import RecoveryAgent


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Revensight AI",
    description="AI-powered revenue recovery agent for Razorpay payment failures.",
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data.json"

STATIC_DIR = BASE_DIR / "static"


# =========================================================
# DATA LOADING
# =========================================================

def load_data():

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return FileResponse(
        STATIC_DIR / "index.html"
    )


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Revensight AI"
    }


# =========================================================
# RUN RECOVERY AGENT
# =========================================================

@app.post("/run-recovery")
def run_recovery():

    data = load_data()

    transactions = data["transactions"]

    customers = data["customers"]

    agent = RecoveryAgent(
        transactions,
        customers
    )

    output = agent.run()

    results = output["results"]

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    total_at_risk = sum(
        float(x["amount"])
        for x in results
    )

    retry_recommendations = [
        x for x in results
        if x["decision"] in [
            "RETRY_NOW",
            "SCHEDULE_RETRY"
        ]
    ]

    message_recommendations = [
        x for x in results
        if x["decision"] == "SEND_PAYMENT_LINK"
    ]

    escalations = [
        x for x in results
        if x["decision"] == "ESCALATE"
    ]

    stopped = [
        x for x in results
        if x["decision"] == "STOP"
    ]

    # -----------------------------------------------------
    # EXPECTED RECOVERABLE VALUE
    # -----------------------------------------------------

    expected_revenue = sum(
        x["economics"]["expected_revenue"]
        for x in results
        if x["decision"] in [
            "RETRY_NOW",
            "SCHEDULE_RETRY",
            "SEND_PAYMENT_LINK"
        ]
    )

    expected_cost = sum(
        x["economics"]["expected_cost"]
        for x in results
        if x["decision"] in [
            "RETRY_NOW",
            "SCHEDULE_RETRY",
            "SEND_PAYMENT_LINK"
        ]
    )

    expected_net_value = (
        expected_revenue - expected_cost
    )

    # IMPORTANT:
    # This is EXPECTED recovery, not actual recovered revenue.

    return {
        "metrics": {

            "transactions_processed":
                len(results),

            "revenue_at_risk":
                round(total_at_risk, 2),

            "expected_revenue_recovered":
                round(expected_revenue, 2),

            "estimated_recovery_rate":
                round(
                    (
                        expected_revenue /
                        total_at_risk *
                        100
                    )
                    if total_at_risk > 0
                    else 0,
                    2
                ),

            "estimated_recovery_cost":
                round(expected_cost, 2),

            "expected_net_value":
                round(expected_net_value, 2),

            "retry_recommendations":
                len(retry_recommendations),

            "payment_link_recommendations":
                len(message_recommendations),

            "escalations":
                len(escalations),

            "stopped":
                len(stopped)
        },

        "results": results,

        "audit_log":
            output["agent_audit_log"]
    }


# =========================================================
# SINGLE TRANSACTION SIMULATOR
# =========================================================

@app.post("/simulate")
def simulate_transaction(transaction: dict):

    data = load_data()

    customers = data["customers"]

    customer_id = transaction.get(
        "customer_id",
        "cust_new"
    )

    customer = customers.get(
        customer_id,
        {
            "successful_payments": 0,
            "previous_failures": 0,
            "lifetime_value": 0
        }
    )

    agent = RecoveryAgent(
        [transaction],
        customers
    )

    result = agent.run_transaction(
        transaction
    )

    return result


# =========================================================
# OPTIONAL RAZORPAY PAYMENT LOOKUP
# =========================================================

@app.get("/razorpay/payment/{payment_id}")
def get_razorpay_payment(
    payment_id: str
):

    key_id = os.getenv(
        "RAZORPAY_KEY_ID"
    )

    key_secret = os.getenv(
        "RAZORPAY_KEY_SECRET"
    )

    if not key_id or not key_secret:

        raise HTTPException(
            status_code=400,
            detail="Razorpay test API keys are not configured."
        )

    url = (
        "https://api.razorpay.com/v1/payments/"
        + payment_id
    )

    try:

        response = requests.get(
            url,
            auth=(key_id, key_secret),
            timeout=10
        )

        if response.status_code >= 400:

            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        return response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )