"""AI Service for generating health observations using OpenRouter API.

Integrates with OpenRouter via the OpenAI-compatible Chat Completions API with
robust error handling, timeouts, rate limits, medical safety guardrails, and key protection.
"""

import os
import logging
from typing import Tuple
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("health_ai_service")
logging.basicConfig(level=logging.INFO)

load_dotenv()

# OpenRouter Base URL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"


def get_openrouter_api_key() -> str:
    """Retrieve OPENROUTER_API_KEY from environment variables."""
    return os.getenv("OPENROUTER_API_KEY", "").strip()


# Backward-compatible alias for routers or scripts referencing previous function
def get_gemini_api_key() -> str:
    """Backward-compatible alias for retrieving active AI API key."""
    return get_openrouter_api_key()


def get_openrouter_model() -> str:
    """Retrieve OPENROUTER_MODEL from environment variables."""
    return os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL).strip() or DEFAULT_OPENROUTER_MODEL


def build_health_prompt(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    """Construct a medically safe, structured prompt for health observation."""
    return f"""You are an AI healthcare assistant providing preliminary, informational observational remarks on routine adult blood test results.

Blood Test Values:
- Blood Glucose: {glucose} mg/dL
- Haemoglobin: {haemoglobin} g/dL
- Total Cholesterol: {cholesterol} mg/dL

Please generate a concise health observation report (3 to 5 sentences or short bullet points) addressing:
1. General Interpretation: Provide an objective observation of these specific numbers relative to general adult clinical guidelines.
2. Potential Health Risk Indicators: Note any patterns (e.g., elevated glucose, atypical haemoglobin, high cholesterol) that warrant attention.
3. Clinical Summary: A brief, plain-language explanation of what these combined findings indicate.
4. Professional Recommendation: Explicitly recommend discussing these results with a licensed healthcare physician for formal interpretation against local laboratory reference ranges.

MANDATORY MEDICAL SAFETY GUIDELINES:
- Clearly label this as AI-generated informational guidance.
- Do NOT provide a definitive medical diagnosis.
- Do NOT prescribe medication, treatments, or specific lifestyle regimens.
- Note that clinical interpretation depends on patient medical history, symptoms, and laboratory-specific reference ranges.
- Keep the response concise, clear, and professional.
"""


def generate_health_remarks(
    glucose: float, haemoglobin: float, cholesterol: float
) -> Tuple[str, str]:
    """Generate AI health observations for blood test metrics via OpenRouter API.

    Args:
        glucose: Blood glucose level in mg/dL.
        haemoglobin: Haemoglobin level in g/dL.
        cholesterol: Total cholesterol in mg/dL.

    Returns:
        Tuple[str, str]: (remarks_text, ai_status)
        where ai_status is either "COMPLETED" or "FAILED".
    """
    api_key = get_openrouter_api_key()

    if not api_key or api_key in ["your_api_key", "your_openrouter_api_key_here"]:
        err_msg = (
            "AI Remarks unavailable: OPENROUTER_API_KEY is not configured in the environment. "
            "Please add a valid OpenRouter API key to your .env file to enable automated AI health observations."
        )
        logger.warning("generate_health_remarks called without valid OPENROUTER_API_KEY configured.")
        return err_msg, "FAILED"

    model_name = get_openrouter_model()

    try:
        from openai import OpenAI, APIError, RateLimitError, APITimeoutError, AuthenticationError

        logger.info(f"Connecting to OpenRouter API (Base URL: {OPENROUTER_BASE_URL}) using model '{model_name}'...")
        client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
            timeout=30.0,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "InfoCare HealthAI",
            },
        )

        prompt = build_health_prompt(glucose, haemoglobin, cholesterol)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI healthcare assistant providing preliminary, informational observational "
                        "guidance on routine adult blood test results. You never diagnose medical conditions or "
                        "prescribe treatments. You always include medical safety disclaimers."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=600,
        )

        if not response.choices or not response.choices[0].message:
            raise ValueError("OpenRouter API returned an empty choices list.")

        remarks = response.choices[0].message.content
        remarks = remarks.strip() if remarks else ""
        if not remarks:
            raise ValueError("OpenRouter API returned an empty response text.")

        logger.info("Successfully generated AI health remarks via OpenRouter.")
        return remarks, "COMPLETED"

    except Exception as exc:
        # Sanitize exception message to ensure API key is NEVER exposed in logs or user responses
        raw_error = str(exc)
        if api_key and api_key in raw_error:
            raw_error = raw_error.replace(api_key, "[REDACTED_API_KEY]")

        # Handle specific error classifications
        from openai import RateLimitError, APITimeoutError, AuthenticationError
        if isinstance(exc, RateLimitError):
            user_friendly_error = (
                "AI Health Service Error: OpenRouter rate limit exceeded (HTTP 429). "
                "Your patient record has been safely saved. You can retry generating AI remarks shortly."
            )
        elif isinstance(exc, AuthenticationError):
            user_friendly_error = (
                "AI Health Service Error: OpenRouter authentication failed. Please verify your OPENROUTER_API_KEY. "
                "Your patient record has been safely saved."
            )
        elif isinstance(exc, APITimeoutError):
            user_friendly_error = (
                "AI Health Service Error: OpenRouter API request timed out. "
                "Your patient record has been safely saved. You can retry generating AI remarks anytime."
            )
        else:
            user_friendly_error = (
                f"AI Health Service Error: Unable to complete analysis via OpenRouter ({raw_error[:180]}). "
                "Your patient record has been safely saved. You can retry generating AI remarks anytime."
            )

        logger.error(f"Failed to generate health remarks via OpenRouter: {user_friendly_error}")
        return user_friendly_error, "FAILED"
