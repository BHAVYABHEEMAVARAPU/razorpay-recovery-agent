# Revensight AI

## Autonomous Revenue Recovery Agent for Razorpay

Revensight AI is an AI-powered revenue recovery agent designed to help merchants recover failed subscription and checkout payments without blindly retrying every transaction.

## Problem

Payment failures are not all equal.

A temporary gateway timeout may be recoverable immediately.

<<<<<<< HEAD
## **Project Structure**
```text
razorpay-recovery-agent/
│
├── main.py        # FastAPI service handling batch execution and metrics
├── engine.py      # Hybrid AI parsing and deterministic safety logic
├── data.json      # Synthetic failed transaction records
└── README.md      # Project documentation


---

## **Setup & Installation Instructions**
```text
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
=======
Insufficient funds may require a delayed retry.

An expired card requires customer action.

A risk-related rejection should not be automatically retried.

Blind retrying can waste money, create unnecessary payment attempts and damage customer experience.

## Solution

Revensight combines:

1. AI payment-failure diagnosis
2. Customer payment history
3. Recovery probability estimation
4. Economic expected-value analysis
5. Deterministic financial guardrails
6. Controlled recovery actions
7. Complete audit trail

## Architecture

Payment Failure
        |
        v
AI Diagnosis
        |
        v
Customer Context
        |
        v
Recovery Probability
        |
        v
Economic Evaluation
        |
        v
Safety Guardrails
        |
        +----------------+
        |                |
        v                v
     Recovery          Customer
      Action            Action
        |
        v
    Audit Trail

## AI Categories

The diagnosis engine supports:

- GATEWAY_TIMEOUT
- INSUFFICIENT_FUNDS
- CARD_EXPIRED
- AUTHENTICATION_FAILURE
- LIMIT_EXCEEDED
- RISK_REJECTION
- BANK_DECLINE
- UNKNOWN

## Recovery Actions

The agent can recommend:

- RETRY_NOW
- SCHEDULE_RETRY
- SEND_PAYMENT_LINK
- ESCALATE
- STOP

## Safety

The LLM does not have unrestricted authority over financial actions.

Deterministic guardrails enforce:

- Maximum retry limits
- Risk rejection protection
- Economic thresholds
- Customer-action requirements
- Audit logging

## Important

The current execution layer is a sandbox simulation.

It does not move real money.

Razorpay Test Mode can be connected for payment-data retrieval and integration testing.

## Running locally

```bash
python -m venv venv
>>>>>>> d2eb23a (Upgrade Revensight AI revenue recovery agent)
