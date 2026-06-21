"""
Stage 2 — Architecture Planner
Converts structured intent into a full app architecture:
pages, entity relationships, and user flows.
"""
import time
import json
from schemas.architecture_schema import ArchitectureSchema
from pipeline.llm_client import call_llm

PLANNER_PROMPT = """You are Stage 2 of an AI App Compiler — the Architecture Planner.

Given the structured intent below, design the full application architecture.

RULES:
1. Every feature in intent.features must map to at least one page
2. Every entity in intent.entities must appear in data_relationships
3. If has_premium=true, include a Pricing/Upgrade page
4. If has_analytics=true, include a dedicated Analytics/Reports page
5. flows must cover: authentication flow, at least one core CRUD flow, and any premium flow
6. data_relationships must capture every meaningful entity connection

INTENT:
{intent}

Return a JSON object matching this exact schema:
{{
  "schema_version": "1.0",
  "app_name": "string",
  "pages": ["list of all page names e.g. Login, Dashboard, Contacts, Settings"],
  "entities": ["list of all data entities"],
  "flows": [
    {{
      "name": "string (e.g. User Login Flow)",
      "steps": ["step1", "step2", "..."],
      "actors": ["roles involved"]
    }}
  ],
  "data_relationships": [
    {{
      "from_entity": "string",
      "to_entity": "string",
      "relation_type": "one_to_many|many_to_many|one_to_one",
      "description": "string"
    }}
  ],
  "tech_stack": {{
    "frontend": "React",
    "backend": "FastAPI",
    "database": "SQLite"
  }}
}}
"""


def plan_architecture(intent: dict) -> tuple[dict, float, int]:
    """
    Run Stage 2: Architecture Planning.
    Returns (architecture_dict, latency_ms, token_count)
    """
    start = time.time()
    filled_prompt = PLANNER_PROMPT.format(intent=json.dumps(intent, indent=2))
    result, tokens = call_llm(filled_prompt, ArchitectureSchema)
    latency = (time.time() - start) * 1000
    return result, latency, tokens
