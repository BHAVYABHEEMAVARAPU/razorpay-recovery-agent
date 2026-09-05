# Revensight AI: Intelligent Subscription & Checkout Recovery Agent

Revensight AI is an autonomous, cost-aware financial recovery agent built for **Track 3: AI Revenue Recovery** for the Razorpay Buildathon. It bridges modern generative AI with bulletproof backend financial guardrails to recover lost merchant revenue from failed subscriptions and checkouts without wasting capital on blind retry fees.

---

## **The Problem**
Digital merchants lose substantial revenue due to recurring subscription renewals and checkouts failing from temporary gateway timeouts, dropped packets, or insufficient funds. However, blindly retrying every failed transaction incurs heavy processing fee leakage and can trigger issuer penalties.

## **The Solution**
Revensight AI uses a hybrid architecture:
1. **AI Parsing Layer:** Utilizes the Gemini API to analyze unstructured, messy human/gateway error messages and normalize them into clear categories (`GATEWAY_TIMEOUT`, `INSUFFICIENT_FUNDS`, etc.).
2. **Deterministic Guardrail Layer:** Enforces hardcoded business safety rules (such as strict retry limits) to ensure money actions are never executed blindly.

---

## **Project Structure**
```text
razorpay-recovery-agent/
│
├── main.py        # FastAPI service handling batch execution and metrics
├── engine.py      # Hybrid AI parsing and deterministic safety logic
├── data.json      # Synthetic failed transaction records
└── README.md      # Project documentation