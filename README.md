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


## **Setup & Installation Instructions**
Clone the repository and enter the directory:

Bash
git clone [https://github.com/BHAVYABHEEMAVARAPU/razorpay-recovery-agent.git](https://github.com/BHAVYABHEEMAVARAPU/razorpay-recovery-agent.git)
cd razorpay-recovery-agent
Create and activate a Python virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\Activate
# On macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install fastapi uvicorn pydantic google-genai
(Optional) Set your free Gemini API key:

Bash
# On Windows PowerShell:
$env:GEMINI_API_KEY="your-api-key-here"
(Note: The system features built-in fallback logic, so it runs seamlessly even without an active API key).

Run the local server:

Bash
uvicorn main:app --reload
Test the Endpoint:
Open your browser and navigate to http://127.0.0.1:8000/docs to interact with the Swagger UI, expand the POST /run-recovery-batch route, and execute the simulation.
