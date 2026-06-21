"""
Stage 3a — UI Generator
Generates the complete UI schema: pages, components, fields.
"""
import time
import json
from schemas.ui_schema import UISchema
from pipeline.llm_client import call_llm

UI_PROMPT = """You are Stage 3a of an AI App Compiler — the UI Schema Generator.

Given the intent and architecture, generate a complete UI schema defining every page and component.

RULES:
1. Every page from architecture.pages must appear exactly once
2. Every component must declare which API endpoint feeds it (api_endpoint field)
3. Table components must list the exact field names (matching DB columns)
4. Form components must list input fields with correct types
5. Protected pages must have is_protected: true
6. Premium pages must have is_premium: true
7. Use snake_case for field names, PascalCase for component names
8. roles_allowed empty list means "all authenticated users"

INTENT: {intent}
ARCHITECTURE: {architecture}

Return a JSON object:
{{
  "schema_version": "1.0",
  "app_name": "string",
  "pages": [
    {{
      "name": "string",
      "route": "/path",
      "is_protected": true/false,
      "roles_allowed": [],
      "is_premium": false,
      "components": [
        {{
          "name": "string (PascalCase)",
          "component_type": "form|table|card|chart|navbar|sidebar|stats",
          "roles_allowed": [],
          "api_endpoint": "/api/resource",
          "fields": [
            {{
              "name": "snake_case_name",
              "field_type": "text|email|password|select|number|date|boolean|table|chart",
              "label": "Human Label",
              "required": true/false,
              "api_source": "/api/endpoint or null"
            }}
          ]
        }}
      ]
    }}
  ],
  "global_components": ["Navbar", "Sidebar"]
}}
"""


def generate_ui(intent: dict, architecture: dict) -> tuple[dict, float, int]:
    """Run Stage 3a: UI Schema Generation."""
    start = time.time()
    filled = UI_PROMPT.format(
        intent=json.dumps(intent, indent=2),
        architecture=json.dumps(architecture, indent=2)
    )
    result, tokens = call_llm(filled, UISchema)
    latency = (time.time() - start) * 1000
    return result, latency, tokens
