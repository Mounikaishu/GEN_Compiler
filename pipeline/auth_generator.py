"""
Stage 3d — Auth Generator
Generates roles, permissions matrix, JWT config, and access control rules.
"""
import time
import json
from schemas.auth_schema import AuthSchema
from pipeline.llm_client import call_llm

AUTH_PROMPT = """You are Stage 3d of an AI App Compiler — the Auth & Permissions Generator.

Generate a complete auth and access control schema.

RULES:
1. Every role from intent.roles must appear in role_permissions
2. Admin role must have is_admin: true and all permissions
3. If has_premium=true, add can_access_premium: true for premium users
4. permissions.resource must match actual API route tags or entity names
5. public_routes must include login and register paths
6. premium_routes must include routes that require paid subscription
7. Every entity/resource must appear in at least one role's permissions

INTENT: {intent}
ARCHITECTURE: {architecture}

Return JSON:
{{
  "schema_version": "1.0",
  "app_name": "string",
  "auth_method": "JWT",
  "roles": ["Admin", "User"],
  "role_permissions": [
    {{
      "role": "Admin",
      "is_admin": true,
      "can_access_premium": true,
      "permissions": [
        {{
          "resource": "resource_name",
          "actions": ["read", "write", "delete", "manage"]
        }}
      ]
    }}
  ],
  "jwt_config": {{
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7
  }},
  "public_routes": ["/api/auth/login", "/api/auth/register"],
  "premium_routes": []
}}
"""


def generate_auth(intent: dict, architecture: dict) -> tuple[dict, float, int]:
    """Run Stage 3d: Auth Schema Generation."""
    start = time.time()
    filled = AUTH_PROMPT.format(
        intent=json.dumps(intent, indent=2),
        architecture=json.dumps(architecture, indent=2)
    )
    result, tokens = call_llm(filled, AuthSchema)
    latency = (time.time() - start) * 1000
    return result, latency, tokens
