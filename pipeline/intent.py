"""
Stage 1 — Intent Extraction
Parses raw NL prompt into a structured IntentSchema.
Handles vague, conflicting, and underspecified inputs gracefully.
"""
import time
from schemas.intent_schema import IntentSchema
from pipeline.llm_client import call_llm

INTENT_PROMPT = """You are Stage 1 of an AI App Compiler — the Intent Extractor.

Your job: Parse the user's natural language description into a strict JSON structure.

RULES:
1. Extract ONLY what is explicitly mentioned or strongly implied
2. If the prompt is vague (e.g. "build something"), list clarifications_needed
3. If a requirement is conflicting (e.g. "admin dashboard but no login"), document it in assumptions and resolve it reasonably
4. If auth is not mentioned but an admin role is, assume JWT auth is needed
5. Always return valid JSON matching the schema exactly

USER PROMPT:
{prompt}

Return a JSON object matching this exact schema:
{{
  "schema_version": "1.0",
  "app_name": "string (derive a concise name)",
  "app_type": "string (CRM|LMS|ERP|eCommerce|HRMS|Hospital|Inventory|Booking|Portal|Other)",
  "description": "string (one sentence what the app does)",
  "features": ["list of features explicitly mentioned or implied"],
  "roles": ["list of user roles, always include at least one"],
  "entities": ["list of data entities like User, Contact, Product, Order"],
  "has_premium": true/false,
  "has_payments": true/false,
  "has_auth": true/false,
  "has_analytics": true/false,
  "assumptions": ["list any assumptions made for underspecified inputs"],
  "clarifications_needed": ["questions if prompt was genuinely ambiguous, else empty list"]
}}
"""


def extract_intent(prompt: str) -> tuple[dict, float, int]:
    """
    Run Stage 1: Intent Extraction.
    Returns (intent_dict, latency_ms, token_count)
    """
    start = time.time()
    filled_prompt = INTENT_PROMPT.format(prompt=prompt)
    result, tokens = call_llm(filled_prompt, IntentSchema)
    latency = (time.time() - start) * 1000
    return result, latency, tokens
