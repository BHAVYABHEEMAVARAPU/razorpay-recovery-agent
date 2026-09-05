# Revensight AI

## Autonomous Revenue Recovery Agent for Razorpay

Revensight AI is an AI-powered revenue recovery agent designed to help merchants recover failed subscription and checkout payments without blindly retrying every transaction.

Instead of treating every payment failure the same way, Revensight analyzes the failure reason, customer payment history, recovery probability, and expected economic value before deciding what action should be taken.

---

## Problem

Payment failures are not all equal.

A temporary gateway timeout may be recoverable immediately.

Insufficient funds may require a delayed retry.

An expired card requires customer action.

A risk-related rejection should not be automatically retried.

Blindly retrying failed payments can:

- Waste money on unnecessary payment attempts
- Increase payment-processing costs
- Create poor customer experiences
- Repeatedly retry transactions that are unlikely to succeed
- Increase operational and financial risk

Merchants therefore need an intelligent system that can determine **when to retry, when to wait, when to ask the customer to act, and when to stop.**

---

## Solution

Revensight AI combines AI-based diagnosis with deterministic financial decision-making.

The system evaluates each failed transaction using:

1. AI payment-failure diagnosis
2. Customer payment history
3. Recovery probability estimation
4. Economic expected-value analysis
5. Deterministic financial guardrails
6. Controlled recovery actions
7. Complete audit trail

The goal is not simply to maximize retries.

The goal is to maximize **expected recovered revenue while controlling unnecessary financial actions.**

---

## Architecture

```text
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
              +------------+------------+
              |                         |
              v                         v
       Recovery Action            Customer Action
              |
              v
         Audit Trail
```

---

## Decision Flow

For every failed payment, Revensight follows a structured decision process:

### 1. Diagnose

Identify the most likely payment failure category.

### 2. Understand Customer Context

Analyze historical payment behavior, previous failures, and customer value.

### 3. Estimate Recovery Probability

Estimate how likely the payment is to succeed under different recovery actions.

### 4. Evaluate Economics

Estimate the expected financial value of taking an action.

### 5. Apply Guardrails

Deterministic rules prevent unsafe or economically unreasonable actions.

### 6. Select Recovery Action

The agent chooses an appropriate action such as retrying, scheduling a retry, requesting customer action, escalating, or stopping.

### 7. Record the Decision

The decision and reasoning are recorded in the audit trail.

---

## AI Categories

The diagnosis engine supports the following payment-failure categories:

- `GATEWAY_TIMEOUT`
- `INSUFFICIENT_FUNDS`
- `CARD_EXPIRED`
- `AUTHENTICATION_FAILURE`
- `LIMIT_EXCEEDED`
- `RISK_REJECTION`
- `BANK_DECLINE`
- `UNKNOWN`

---

## Recovery Actions

The agent can recommend:

### `RETRY_NOW`

Used when the failure is likely temporary and an immediate retry has a reasonable expected value.

### `SCHEDULE_RETRY`

Used when the payment may become recoverable later, such as temporary insufficient funds.

### `SEND_PAYMENT_LINK`

Used when customer intervention is required, such as an expired card or authentication-related failure.

### `ESCALATE`

Used when the transaction requires manual investigation or should not be automatically recovered.

### `STOP`

Used when retrying is unlikely to be beneficial or when safety guardrails prevent further attempts.

---

## Economic Decision Making

Revensight does not make decisions based only on AI confidence.

It also considers the expected economic value of an action.

A simplified model is:

```text
Expected Recovery Value
        =
Payment Amount
×
Recovery Probability
-
Expected Recovery Cost
```

This allows the system to distinguish between:

- A high-probability, low-cost recovery
- A low-probability retry
- A customer-action flow
- A transaction where further recovery attempts are not economically justified

This helps prevent the agent from blindly maximizing payment attempts.

---

## Safety Guardrails

The AI does not have unrestricted authority over financial actions.

Deterministic guardrails enforce:

- Maximum retry limits
- Risk-rejection protection
- Economic thresholds
- Customer-action requirements
- Transaction safety rules
- Audit logging

This creates a separation between:

```text
AI
↓
Diagnosis + Recommendation

Deterministic Rules
↓
Safety + Financial Authorization
```

The AI can recommend an action, but deterministic rules determine whether that action is allowed.

---

## Customer Segmentation

Revensight can use customer history to provide additional context when making recovery decisions.

Customers can be categorized into segments such as:

- `HIGH_VALUE`
- `LOYAL`
- `NEW_OR_LOW_HISTORY`

Historical behavior can influence recovery probability and the expected value of a recovery action.

---

## Dashboard

The project includes a web dashboard for monitoring recovery decisions.

The dashboard provides visibility into:

- Revenue at risk
- Expected revenue recovered
- Expected recovery rate
- Expected recovery cost
- Expected net value
- Recovery actions
- Failure categories
- AI confidence
- Customer segments
- Transaction-level decisions
- Audit information

---

## Demo Metrics

The dashboard reports **expected** recovery metrics based on the simulation and recovery-probability model.

For example:

```text
Revenue at Risk
        ↓
Recovery Probability
        ↓
Expected Revenue Recovered
        ↓
Expected Recovery Rate
        ↓
Expected Net Value
```

These values are estimates used to demonstrate the decision-making system.

> **Important:** Expected recovered revenue is not the same as actual recovered revenue.

---

## Razorpay Integration

The project is designed around the Razorpay payment ecosystem.

The current implementation supports Razorpay Test Mode integration for payment-data retrieval and integration testing.

The optional Razorpay integration uses:

```text
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
```

Razorpay credentials should be stored in environment variables and should never be committed to GitHub.

The current execution layer is intentionally a **sandbox simulation**.

It does not move real money or perform uncontrolled live payment retries.

---

## Current Execution Model

The project currently follows:

```text
Transaction
    ↓
AI Diagnosis
    ↓
Customer History
    ↓
Recovery Probability
    ↓
Economic Evaluation
    ↓
Guardrails
    ↓
Recommended Action
    ↓
Sandbox Execution
    ↓
Audit Trail
```

The execution layer simulates recovery actions so that the system can be safely demonstrated without creating real financial transactions.

---

## API

The application provides a FastAPI backend.

Main endpoints include:

```text
GET /
```

Returns the dashboard.

```text
GET /health
```

Checks whether the API is running.

```text
POST /run-recovery
```

Runs the recovery engine on the available transactions.

```text
POST /simulate
```

Runs a recovery simulation.

```text
GET /razorpay/payment/{payment_id}
```

Optionally retrieves Razorpay payment information when Test Mode credentials are configured.

Interactive API documentation is available through FastAPI:

```text
/docs
```

---

## Project Structure

```text
razorpay-recovery-agent/
│
├── main.py
├── engine.py
├── agent.py
├── data.json
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
└── static/
    └── index.html
```

### `engine.py`

Contains the core diagnosis, recovery-probability, economic evaluation, and guardrail logic.

### `agent.py`

Contains the recovery agent and its tools for customer history, diagnosis, action execution, and transaction processing.

### `main.py`

Contains the FastAPI application and API endpoints.

### `data.json`

Contains synthetic customer and transaction data used for the demonstration.

### `static/index.html`

Contains the web dashboard.

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/BHAVYABHEEMAVARAPU/razorpay-recovery-agent.git
cd razorpay-recovery-agent
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`.

```env
GEMINI_API_KEY=your-gemini-api-key
RAZORPAY_KEY_ID=your-razorpay-test-key
RAZORPAY_KEY_SECRET=your-razorpay-test-secret
```

For PowerShell, you can also temporarily set the Gemini key:

```powershell
$env:GEMINI_API_KEY="your-key"
```

### 5. Start the application

```powershell
uvicorn main:app --reload
```

### 6. Open the dashboard

```text
http://127.0.0.1:8000
```

### 7. Open API documentation

```text
http://127.0.0.1:8000/docs
```

---

## AI Fallback Mode

The system can operate with a deterministic fallback classifier when a Gemini API key is not configured.

This allows the project to remain runnable during demonstrations without depending completely on an external AI service.

When Gemini is configured, the system can use the AI model for payment-failure diagnosis while deterministic rules continue to control financial decisions.

---

## Security

Sensitive credentials should never be hard-coded into the source code.

Use environment variables for:

```text
GEMINI_API_KEY
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
```

The repository includes `.gitignore` rules for:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
```

Razorpay Test Mode credentials should be used during development and demonstrations.

---

## Design Principles

Revensight AI is built around four principles:

### 1. Diagnose Before Acting

A failed payment should be understood before deciding whether another attempt makes sense.

### 2. Optimize Expected Value

The system considers both potential recovered revenue and the cost/risk of taking an action.

### 3. Keep Financial Guardrails Deterministic

AI recommendations should not directly control unrestricted financial operations.

### 4. Make Decisions Auditable

Every recovery decision should have an understandable reason and recorded action.

---

## Why This Approach?

Traditional retry systems often follow rules such as:

```text
Payment failed
      ↓
Wait
      ↓
Retry
      ↓
Retry again
      ↓
Retry again
```

Revensight instead follows:

```text
Payment failed
      ↓
Why did it fail?
      ↓
Can it realistically recover?
      ↓
What is the expected economic value?
      ↓
Is the action allowed by guardrails?
      ↓
Choose the safest useful action
```

This makes payment recovery more intelligent, explainable, and economically aware.

---

## Future Improvements

Potential production extensions include:

- Razorpay webhook-driven event ingestion
- Real payment outcome feedback loops
- Automatic model evaluation from historical outcomes
- More payment-failure categories
- Merchant-specific recovery policies
- Adaptive retry timing
- A/B testing of recovery strategies
- Customer communication workflows
- Production-grade authentication and authorization
- Persistent transaction and audit databases
- Recovery-performance analytics
- Closed-loop learning from successful and unsuccessful recovery attempts

---

## Disclaimer

This project is a hackathon prototype and demonstration system.

The transaction dataset is synthetic, and recovery metrics are model-based estimates.

The current execution layer operates in a sandbox simulation and does not claim actual recovered revenue.

It is not intended to independently execute unrestricted real-world financial transactions.

---

## Built For

**Razorpay Buildathon 2026**

### Revensight AI

**Recover revenue intelligently.  
Retry less. Recover more.**
