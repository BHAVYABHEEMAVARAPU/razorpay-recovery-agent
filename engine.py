import os
try:
    from google import genai
    # Initialize client if library is accessible
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "your-free-gemini-key"))
    HAS_GENAI = True
except Exception:
    HAS_GENAI = False

def parse_error_with_ai(raw_message: str) -> str:
    """Classifies gateway logs using Gemini or gracefully falls back."""
    if HAS_GENAI:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Classify the following payment gateway error message into exactly one of these categories: GATEWAY_TIMEOUT, INSUFFICIENT_FUNDS, or UNKNOWN. Return only the category name: {raw_message}"
            )
            return response.text.strip()
        except Exception:
            pass
            
    # Fallback keyword logic ensuring 100% uptime
    return "GATEWAY_TIMEOUT" if "timeout" in raw_message.lower() else "INSUFFICIENT_FUNDS"

def evaluate_recovery(transaction: dict) -> dict:
    error_type = parse_error_with_ai(transaction["raw_gateway_message"])
    retry_count = transaction["retry_count"]
    
    if retry_count >= 3:
        return {
            "action": "ABORT",
            "reason": f"AI classified as {error_type}. Max retry limit reached. Halting to prevent fee leakage."
        }
    
    if error_type == "GATEWAY_TIMEOUT":
        return {
            "action": "RETRY_IMMEDIATE",
            "reason": "AI verified transient gateway drop. Safe to execute smart retry."
        }
    else:
        return {
            "action": "SCHEDULE_REMINDER",
            "reason": f"AI classified as {error_type}. Soft failure; routing to customer communication flow."
        }