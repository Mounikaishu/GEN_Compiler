"""
Stage 3b — API Generator
Generates every API route with request/response field definitions.
"""
import time
import json
from schemas.api_schema import APISchema
from pipeline.llm_client import call_llm

API_PROMPT = """You are Stage 3b of an AI App Compiler — the API Schema Generator.

Generate a complete REST API schema for the application.

RULES:
1. Every entity must have CRUD routes (GET list, GET by id, POST, PUT, DELETE)
2. Field names in response_fields MUST match DB column names exactly (snake_case)
3. Auth routes (login, register, refresh) go in auth_routes
4. Premium routes must have is_premium: true and roles_allowed set
5. Analytics routes must be restricted to Admin role
6. Every route must declare which db_table it operates on

INTENT: {intent}
ARCHITECTURE: {architecture}

Return JSON:
{{
  "schema_version": "1.0",
  "app_name": "string",
  "base_path": "/api",
  "routes": [
    {{
      "path": "/api/resource",
      "method": "GET|POST|PUT|DELETE|PATCH",
      "summary": "string",
      "tags": ["tag"],
      "auth_required": true,
      "roles_allowed": [],
      "request_fields": [
        {{"name": "field_name", "field_type": "string|integer|boolean|float|datetime|uuid", "required": true, "description": ""}}
      ],
      "response_fields": [
        {{"name": "field_name", "field_type": "string|integer|boolean|float|datetime|uuid", "required": true, "description": ""}}
      ],
      "db_table": "table_name",
      "is_premium": false
    }}
  ],
  "auth_routes": [
    {{
      "path": "/api/auth/login",
      "method": "POST",
      "summary": "User login",
      "tags": ["auth"],
      "auth_required": false,
      "roles_allowed": [],
      "request_fields": [{{"name": "email", "field_type": "string", "required": true, "description": ""}}, {{"name": "password", "field_type": "string", "required": true, "description": ""}}],
      "response_fields": [{{"name": "access_token", "field_type": "string", "required": true, "description": ""}}, {{"name": "token_type", "field_type": "string", "required": true, "description": ""}}],
      "db_table": "users",
      "is_premium": false
    }}
  ]
}}
"""


def generate_api(intent: dict, architecture: dict) -> tuple[dict, float, int]:
    """Run Stage 3b: API Schema Generation."""
    start = time.time()
    filled = API_PROMPT.format(
        intent=json.dumps(intent, indent=2),
        architecture=json.dumps(architecture, indent=2)
    )
    result, tokens = call_llm(filled, APISchema)
    latency = (time.time() - start) * 1000
    return result, latency, tokens
