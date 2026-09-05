import os
import json
from typing import Dict, Any


# =========================================================
# OPTIONAL GEMINI IMPORT
# =========================================================

try:
    from google import genai

    HAS_GENAI = bool(
        os.getenv("GEMINI_API_KEY")
    )

except Exception:
    HAS_GENAI = False


# =========================================================
# CONFIGURATION
# =========================================================

# Maximum number of automatic retry attempts.
MAX_RETRIES = 3


# These are SIMULATION costs.
# They are NOT Razorpay's actual fees.
DEFAULT_RETRY_COST = 8.0
DEFAULT_MESSAGE_COST = 0.50


# Minimum expected net value required
# before an automatic retry.
MIN_EXPECTED_NET_VALUE = 50.0


# =========================================================
# GEMINI CLIENT
# =========================================================

client = None


if HAS_GENAI:

    try:

        client = genai.Client(
            api_key=os.getenv(
                "GEMINI_API_KEY"
            )
        )

    except Exception:

        client = None


# =========================================================
# FALLBACK ERROR CLASSIFIER
# =========================================================

def fallback_classify(
    raw_message: str
) -> str:

    """
    Deterministic fallback classifier.

    This allows the system to continue working
    even if Gemini is unavailable.
    """

    text = raw_message.lower()


    # -----------------------------------------------------
    # GATEWAY / NETWORK FAILURE
    # -----------------------------------------------------

    if any(
        word in text
        for word in [
            "timeout",
            "timed out",
            "gateway",
            "connection dropped",
            "network",
            "temporarily unavailable",
            "issuer unavailable"
        ]
    ):

        return "GATEWAY_TIMEOUT"


    # -----------------------------------------------------
    # INSUFFICIENT FUNDS
    # -----------------------------------------------------

    if any(
        word in text
        for word in [
            "insufficient funds",
            "low balance",
            "balance",
            "not enough funds"
        ]
    ):

        return "INSUFFICIENT_FUNDS"


    # -----------------------------------------------------
    # EXPIRED CARD
    # -----------------------------------------------------

    if any(
        word in text
        for word in [
            "expired",
            "expiry"
        ]
    ):

        return "CARD_EXPIRED"


    # -----------------------------------------------------
    # AUTHENTICATION FAILURE
    # -----------------------------------------------------

    if any(
        word in text
        for word in [
            "authentication",
            "otp",
            "3ds",
            "3-d secure"
        ]
    ):

        return "AUTHENTICATION_FAILURE"


    # -----------------------------------------------------
    # LIMIT EXCEEDED
    # -----------------------------------------------------

    if any(
        word in text
        for word in [
            "limit exceeded",
            "limit",
            "daily limit"
        ]
    ):

        return "LIMIT_EXCEEDED"


    # -----------------------------------------------------
    # RISK / FRAUD
    # -----------------------------------------------------

    if any(
        word in text
        for word in [
            "fraud",
            "risk",
            "suspicious"
        ]
    ):

        return "RISK_REJECTION"


    # -----------------------------------------------------
    # BANK DECLINE
    # -----------------------------------------------------

    if any(
        word in text
        for word in [
            "declined",
            "decline",
            "rejected"
        ]
    ):

        return "BANK_DECLINE"


    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    return "UNKNOWN"


# =========================================================
# AI ERROR CLASSIFICATION
# =========================================================

def parse_error_with_ai(
    raw_message: str
) -> Dict[str, Any]:

    """
    Uses Gemini to classify an unstructured
    payment failure.

    Falls back to deterministic rules when
    Gemini is unavailable.
    """

    allowed_categories = [

        "GATEWAY_TIMEOUT",

        "INSUFFICIENT_FUNDS",

        "CARD_EXPIRED",

        "AUTHENTICATION_FAILURE",

        "LIMIT_EXCEEDED",

        "RISK_REJECTION",

        "BANK_DECLINE",

        "UNKNOWN"
    ]


    # -----------------------------------------------------
    # GEMINI NOT AVAILABLE
    # -----------------------------------------------------

    if client is None:

        category = fallback_classify(
            raw_message
        )

        return {

            "category":
                category,

            "confidence":
                0.82,

            "reason":
                "Classified using deterministic fallback rules.",

            "source":
                "fallback_rules"
        }


    # -----------------------------------------------------
    # GEMINI PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are a payment recovery diagnosis agent.

Your job is to classify a failed payment.

Choose EXACTLY ONE category from:

{", ".join(allowed_categories)}

Payment gateway error:

{raw_message}

Return ONLY valid JSON.

Use this exact structure:

{{
    "category": "CATEGORY_NAME",
    "confidence": 0.0,
    "reason": "short explanation"
}}

The confidence must be between 0 and 1.
"""


    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )


        text = response.text.strip()


        # -------------------------------------------------
        # REMOVE MARKDOWN CODE FENCES
        # -------------------------------------------------

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()


        # -------------------------------------------------
        # PARSE JSON
        # -------------------------------------------------

        result = json.loads(
            text
        )


        category = result.get(
            "category",
            "UNKNOWN"
        )


        # -------------------------------------------------
        # VALIDATE CATEGORY
        # -------------------------------------------------

        if category not in allowed_categories:

            category = "UNKNOWN"


        confidence = float(
            result.get(
                "confidence",
                0.75
            )
        )


        # Keep confidence in valid range.

        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )


        return {

            "category":
                category,

            "confidence":
                confidence,

            "reason":
                result.get(
                    "reason",
                    "AI classification."
                ),

            "source":
                "gemini"
        }


    except Exception:

        # -------------------------------------------------
        # GEMINI FAILURE → FALLBACK
        # -------------------------------------------------

        category = fallback_classify(
            raw_message
        )


        return {

            "category":
                category,

            "confidence":
                0.75,

            "reason":
                "Gemini classification failed; deterministic fallback was used.",

            "source":
                "fallback_rules"
        }


# =========================================================
# RECOVERY PROBABILITY
# =========================================================

def estimate_recovery_probability(
    error_type: str,
    customer: Dict[str, Any],
    retry_count: int
) -> float:

    """
    Estimates the probability that a failed
    payment can eventually be recovered.

    This is currently a heuristic model for
    the hackathon simulation.
    """


    # -----------------------------------------------------
    # BASE PROBABILITIES
    # -----------------------------------------------------

    probability_map = {

        "GATEWAY_TIMEOUT":
            0.78,

        "INSUFFICIENT_FUNDS":
            0.32,

        "CARD_EXPIRED":
            0.18,

        "AUTHENTICATION_FAILURE":
            0.42,

        "LIMIT_EXCEEDED":
            0.28,

        "RISK_REJECTION":
            0.05,

        "BANK_DECLINE":
            0.24,

        "UNKNOWN":
            0.25
    }


    probability = probability_map.get(

        error_type,

        0.25
    )


    # -----------------------------------------------------
    # CUSTOMER HISTORY
    # -----------------------------------------------------

    successful_payments = customer.get(

        "successful_payments",

        0
    )


    previous_failures = customer.get(

        "previous_failures",

        0
    )


    # -----------------------------------------------------
    # POSITIVE CUSTOMER HISTORY
    # -----------------------------------------------------

    if successful_payments >= 10:

        probability += 0.12

    elif successful_payments >= 5:

        probability += 0.10

    elif successful_payments >= 2:

        probability += 0.05


    # -----------------------------------------------------
    # NEGATIVE CUSTOMER HISTORY
    # -----------------------------------------------------

    if previous_failures >= 5:

        probability -= 0.18

    elif previous_failures >= 3:

        probability -= 0.12

    elif previous_failures >= 2:

        probability -= 0.05


    # -----------------------------------------------------
    # RETRY HISTORY
    # -----------------------------------------------------

    if retry_count == 1:

        probability -= 0.02

    elif retry_count == 2:

        probability -= 0.10

    elif retry_count >= 3:

        probability -= 0.20


    # -----------------------------------------------------
    # KEEP VALUE BETWEEN 2% AND 95%
    # -----------------------------------------------------

    probability = max(

        0.02,

        min(
            probability,
            0.95
        )
    )


    return round(

        probability,

        4
    )


# =========================================================
# CUSTOMER SEGMENT
# =========================================================

def customer_segment(
    customer: Dict[str, Any]
) -> str:

    """
    Determines the customer's commercial segment.
    """

    successful = customer.get(

        "successful_payments",

        0
    )


    lifetime_value = customer.get(

        "lifetime_value",

        0
    )


    # -----------------------------------------------------
    # HIGH VALUE
    # -----------------------------------------------------

    if (

        lifetime_value >= 50000

        or

        successful >= 10

    ):

        return "HIGH_VALUE"


    # -----------------------------------------------------
    # LOYAL
    # -----------------------------------------------------

    if (

        lifetime_value >= 10000

        or

        successful >= 3

    ):

        return "LOYAL"


    # -----------------------------------------------------
    # NEW / LOW HISTORY
    # -----------------------------------------------------

    return "NEW_OR_LOW_HISTORY"


# =========================================================
# EXPECTED VALUE CALCULATION
# =========================================================

def calculate_expected_value(
    amount: float,
    probability: float,
    action: str,
    retry_cost: float = DEFAULT_RETRY_COST
) -> Dict[str, float]:

    """
    Calculates expected revenue and expected
    net value for a particular recovery action.

    IMPORTANT:
    These are simulated expected values.
    They are NOT guaranteed revenue.
    """


    # -----------------------------------------------------
    # RETRY NOW
    # -----------------------------------------------------

    if action == "RETRY_NOW":

        expected_revenue = (
            amount * probability
        )

        expected_cost = (
            retry_cost
        )


    # -----------------------------------------------------
    # SEND PAYMENT LINK
    # -----------------------------------------------------

    elif action == "SEND_PAYMENT_LINK":

        expected_revenue = (
            amount * probability
        )

        expected_cost = (
            DEFAULT_MESSAGE_COST
        )


    # -----------------------------------------------------
    # SCHEDULE RETRY
    # -----------------------------------------------------

    elif action == "SCHEDULE_RETRY":

        expected_revenue = (
            amount * probability
        )

        expected_cost = (
            retry_cost * 0.75
        )


    # -----------------------------------------------------
    # NO FINANCIAL ACTION
    # -----------------------------------------------------

    else:

        expected_revenue = 0

        expected_cost = 0


    # -----------------------------------------------------
    # EXPECTED NET VALUE
    # -----------------------------------------------------

    expected_net_value = (

        expected_revenue

        -

        expected_cost
    )


    return {

        "expected_revenue":
            round(
                expected_revenue,
                2
            ),

        "expected_cost":
            round(
                expected_cost,
                2
            ),

        "expected_net_value":
            round(
                expected_net_value,
                2
            )
    }


# =========================================================
# DETERMINISTIC SAFETY POLICY
# =========================================================

def apply_guardrails(
    transaction: Dict[str, Any],
    diagnosis: Dict[str, Any],
    probability: float,
    economics: Dict[str, float]
) -> Dict[str, Any]:

    """
    Deterministic financial safety layer.

    The AI can diagnose the problem, but these
    rules control what actions are allowed.
    """


    error_type = diagnosis.get(

        "category",

        "UNKNOWN"
    )


    retry_count = transaction.get(

        "retry_count",

        0
    )


    amount = float(

        transaction.get(

            "amount",

            0
        )
    )


    # =====================================================
    # HARD RETRY LIMIT
    # =====================================================

    if retry_count >= MAX_RETRIES:

        return {

            "action":
                "STOP",

            "reason":
                "Maximum retry limit reached. Automatic retry blocked.",

            "risk":
                "HIGH"
        }


    # =====================================================
    # RISK / FRAUD
    # =====================================================

    if error_type == "RISK_REJECTION":

        return {

            "action":
                "ESCALATE",

            "reason":
                "Risk-related rejection must not be automatically retried.",

            "risk":
                "HIGH"
        }


    # =====================================================
    # EXPIRED CARD
    # =====================================================

    if error_type == "CARD_EXPIRED":

        return {

            "action":
                "SEND_PAYMENT_LINK",

            "reason":
                "Card appears expired. Customer action is required.",

            "risk":
                "LOW"
        }


    # =====================================================
    # AUTHENTICATION FAILURE
    # =====================================================

    if error_type == "AUTHENTICATION_FAILURE":

        return {

            "action":
                "SEND_PAYMENT_LINK",

            "reason":
                "Customer authentication is required before another attempt.",

            "risk":
                "LOW"
        }


    # =====================================================
    # LOW-VALUE TRANSACTION
    # =====================================================

    if (

        amount < 100

        and

        probability < 0.50

    ):

        return {

            "action":
                "SEND_PAYMENT_LINK",

            "reason":
                "Low-value transaction with weak recovery probability; avoid unnecessary retries.",

            "risk":
                "LOW"
        }


    # =====================================================
    # ECONOMIC GUARDRAIL
    # =====================================================

    if (

        economics[
            "expected_net_value"
        ]

        <

        MIN_EXPECTED_NET_VALUE

    ):

        # -----------------------------------------------
        # MODERATE RECOVERY PROBABILITY
        # -----------------------------------------------

        if probability >= 0.45:

            return {

                "action":
                    "SCHEDULE_RETRY",

                "reason":
                    "Recovery is plausible, but immediate retry does not provide sufficient expected net value.",

                "risk":
                    "MEDIUM"
            }


        # -----------------------------------------------
        # LOW RECOVERY PROBABILITY
        # -----------------------------------------------

        return {

            "action":
                "SEND_PAYMENT_LINK",

            "reason":
                "Expected retry value is too low. Route customer to a payment recovery flow.",

            "risk":
                "LOW"
        }


    # =====================================================
    # GATEWAY TIMEOUT
    # =====================================================

    if error_type == "GATEWAY_TIMEOUT":

        return {

            "action":
                "RETRY_NOW",

            "reason":
                "Transient gateway failure with favorable expected recovery value.",

            "risk":
                "LOW"
        }


    # =====================================================
    # INSUFFICIENT FUNDS
    # =====================================================

    if error_type == "INSUFFICIENT_FUNDS":

        if probability >= 0.50:

            return {

                "action":
                    "SCHEDULE_RETRY",

                "reason":
                    "Customer history suggests recovery is possible, but immediate retry is not optimal.",

                "risk":
                    "MEDIUM"
            }


        return {

            "action":
                "SEND_PAYMENT_LINK",

            "reason":
                "Insufficient funds and low immediate recovery probability. Ask customer to update payment method.",

            "risk":
                "LOW"
        }


    # =====================================================
    # GENERAL HIGH-PROBABILITY CASE
    # =====================================================

    if probability >= 0.60:

        return {

            "action":
                "SCHEDULE_RETRY",

            "reason":
                "Recovery probability is sufficiently high for a controlled future retry.",

            "risk":
                "MEDIUM"
        }


    # =====================================================
    # DEFAULT
    # =====================================================

    return {

        "action":
            "SEND_PAYMENT_LINK",

        "reason":
            "Insufficient confidence for automatic retry.",

        "risk":
            "LOW"
    }


# =========================================================
# MAIN RECOVERY DECISION
# =========================================================

def evaluate_recovery(
    transaction: Dict[str, Any],
    customer: Dict[str, Any]
) -> Dict[str, Any]:

    """
    Complete Revensight decision pipeline.

    Flow:

    Payment Failure
          ↓
    AI Diagnosis
          ↓
    Customer Context
          ↓
    Recovery Probability
          ↓
    Economic Evaluation
          ↓
    Safety Guardrails
          ↓
    Recovery Action
    """


    # =====================================================
    # STEP 1 — AI DIAGNOSIS
    # =====================================================

    diagnosis = parse_error_with_ai(

        transaction.get(

            "raw_gateway_message",

            ""
        )
    )


    error_type = diagnosis.get(

        "category",

        "UNKNOWN"
    )


    # =====================================================
    # STEP 2 — RECOVERY PROBABILITY
    # =====================================================

    probability = estimate_recovery_probability(

        error_type,

        customer,

        transaction.get(

            "retry_count",

            0
        )
    )


    # =====================================================
    # STEP 3 — INITIAL RETRY ECONOMICS
    # =====================================================

    retry_economics = calculate_expected_value(

        amount=float(

            transaction.get(

                "amount",

                0
            )
        ),

        probability=probability,

        action="RETRY_NOW"
    )


    # =====================================================
    # STEP 4 — APPLY SAFETY GUARDRAILS
    # =====================================================

    guardrail = apply_guardrails(

        transaction,

        diagnosis,

        probability,

        retry_economics
    )


    # =====================================================
    # STEP 5 — DETERMINE FINAL ACTION
    # =====================================================

    action = guardrail.get(

        "action",

        "STOP"
    )


    # =====================================================
    # STEP 6 — CALCULATE ECONOMICS FOR ACTUAL ACTION
    # =====================================================

    if action == "STOP":

        economics = {

            "expected_revenue":
                0,

            "expected_cost":
                0,

            "expected_net_value":
                0
        }


    elif action == "ESCALATE":

        economics = {

            "expected_revenue":
                0,

            "expected_cost":
                0,

            "expected_net_value":
                0
        }


    elif action == "SEND_PAYMENT_LINK":

        economics = calculate_expected_value(

            amount=float(

                transaction.get(

                    "amount",

                    0
                )
            ),

            probability=probability,

            action="SEND_PAYMENT_LINK"
        )


    elif action == "SCHEDULE_RETRY":

        economics = calculate_expected_value(

            amount=float(

                transaction.get(

                    "amount",

                    0
                )
            ),

            probability=probability,

            action="SCHEDULE_RETRY"
        )


    elif action == "RETRY_NOW":

        economics = retry_economics


    else:

        economics = {

            "expected_revenue":
                0,

            "expected_cost":
                0,

            "expected_net_value":
                0
        }


    # =====================================================
    # STEP 7 — CUSTOMER SEGMENT
    # =====================================================

    segment = customer_segment(

        customer
    )


    # =====================================================
    # STEP 8 — RETURN COMPLETE DECISION
    # =====================================================

    return {

        "transaction_id":
            transaction.get(
                "transaction_id"
            ),

        "customer_id":
            transaction.get(
                "customer_id"
            ),

        "amount":
            transaction.get(
                "amount",
                0
            ),


        # -------------------------------------------------
        # AI DIAGNOSIS
        # -------------------------------------------------

        "diagnosis": {

            "category":
                error_type,

            "confidence":
                diagnosis.get(
                    "confidence",
                    0.75
                ),

            "source":
                diagnosis.get(
                    "source",
                    "unknown"
                ),

            "reason":
                diagnosis.get(
                    "reason",
                    ""
                )
        },


        # -------------------------------------------------
        # CUSTOMER INFORMATION
        # -------------------------------------------------

        "customer": {

            "segment":
                segment,

            "successful_payments":
                customer.get(
                    "successful_payments",
                    0
                ),

            "previous_failures":
                customer.get(
                    "previous_failures",
                    0
                ),

            "lifetime_value":
                customer.get(
                    "lifetime_value",
                    0
                )
        },


        # -------------------------------------------------
        # RECOVERY PROBABILITY
        # -------------------------------------------------

        "recovery_probability":
            round(

                probability * 100,

                2
            ),


        # -------------------------------------------------
        # ECONOMIC ANALYSIS
        # -------------------------------------------------

        "economics":
            economics,


        # -------------------------------------------------
        # FINAL AGENT DECISION
        # -------------------------------------------------

        "decision":
            action,


        # -------------------------------------------------
        # RISK
        # -------------------------------------------------

        "risk":
            guardrail.get(

                "risk",

                "UNKNOWN"
            ),


        # -------------------------------------------------
        # EXPLANATION
        # -------------------------------------------------

        "reason":
            guardrail.get(

                "reason",

                ""
            )
    }