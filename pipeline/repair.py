"""
Stage 5 — Repair Engine
The intelligent repair layer: identifies which layer(s) failed validation
and regenerates ONLY those layers — not the entire pipeline.
This is the core differentiator vs brute-force retries.
"""
import json
import time
from typing import List
from schemas.output_schema import ValidationError, RepairAction
from pipeline.llm_client import call_llm
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema

MAX_REPAIR_ATTEMPTS = 3


def repair(
    errors: List[ValidationError],
    intent: dict,
    architecture: dict,
    ui: dict,
    api: dict,
    db: dict,
    auth: dict,
) -> tuple[dict, dict, dict, dict, List[RepairAction]]:
    """
    Intelligently repair only the failing layer(s).
    Returns updated (ui, api, db, auth) and a log of repair actions.
    """
    repair_log: List[RepairAction] = []

    # Group errors by layer prefix to decide what to repair
    layers_to_repair = _identify_failing_layers(errors)

    for layer, layer_errors in layers_to_repair.items():
        error_summary = "\n".join(f"- [{e.layer}] {e.location}: {e.message}" for e in layer_errors)

        for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
            try:
                if layer == "API":
                    api, tokens = _repair_api(api, db, intent, architecture, error_summary)
                    action = "Regenerated API routes to match DB column names"
                elif layer == "DB":
                    db, tokens = _repair_db(db, api, intent, architecture, error_summary)
                    action = "Regenerated DB tables to include missing columns"
                elif layer == "UI":
                    ui, tokens = _repair_ui(ui, api, intent, architecture, error_summary)
                    action = "Regenerated UI components to align with API response fields"
                elif layer == "Auth":
                    auth, tokens = _repair_auth(auth, ui, api, intent, architecture, error_summary)
                    action = "Regenerated Auth roles/permissions to match UI and API requirements"
                else:
                    break

                repair_log.append(RepairAction(
                    layer=layer,
                    attempt=attempt,
                    error_fixed=error_summary[:300],
                    action_taken=action,
                    success=True
                ))
                break  # Repair succeeded for this layer

            except Exception as e:
                repair_log.append(RepairAction(
                    layer=layer,
                    attempt=attempt,
                    error_fixed=error_summary[:300],
                    action_taken=f"Repair attempt {attempt} failed: {str(e)[:200]}",
                    success=False
                ))
                if attempt == MAX_REPAIR_ATTEMPTS:
                    # Give up on this layer after max attempts
                    break

    return ui, api, db, auth, repair_log


def _identify_failing_layers(errors: List[ValidationError]) -> dict[str, List[ValidationError]]:
    """Map errors to the layer that needs to be repaired (not the layer that's wrong)."""
    layer_map: dict[str, List[ValidationError]] = {}
    for error in errors:
        # Determine which layer to fix based on the error type
        if "UI→API" in error.layer:
            # API is missing fields that UI needs → repair API
            target = "API"
        elif "API→DB" in error.layer:
            # DB is missing columns that API references → repair DB
            target = "DB"
        elif "Auth→UI" in error.layer or "Auth→API" in error.layer:
            # Auth roles don't match → repair Auth
            target = "Auth"
        elif error.layer == "UI":
            target = "UI"
        elif error.layer == "DB":
            target = "DB"
        elif error.layer == "Auth":
            target = "Auth"
        else:
            target = "API"

        if target not in layer_map:
            layer_map[target] = []
        layer_map[target].append(error)
    return layer_map


def _repair_api(api, db, intent, architecture, error_summary) -> tuple[dict, int]:
    prompt = f"""You are the Repair Engine of an AI App Compiler.

The API Schema has validation errors. Fix ONLY the issues listed below without changing correct parts.

ERRORS TO FIX:
{error_summary}

CURRENT API SCHEMA (fix this):
{json.dumps(api, indent=2)}

DB SCHEMA (use these exact column names in response_fields):
{json.dumps(db, indent=2)}

INTENT: {json.dumps(intent, indent=2)}

Rules:
- response_fields names must exactly match DB column names
- Do not remove existing correct routes
- Keep all auth_routes unchanged
- Return the complete corrected API schema JSON
"""
    return call_llm(prompt, APISchema)


def _repair_db(db, api, intent, architecture, error_summary) -> tuple[dict, int]:
    prompt = f"""You are the Repair Engine of an AI App Compiler.

The DB Schema has validation errors. Fix ONLY the issues listed below.

ERRORS TO FIX:
{error_summary}

CURRENT DB SCHEMA (fix this):
{json.dumps(db, indent=2)}

API SCHEMA (add missing columns to match these response_fields):
{json.dumps(api, indent=2)}

Rules:
- Add missing columns to the correct tables
- Fix invalid foreign key references
- Add missing payment/premium tables if required
- Return the complete corrected DB schema JSON
"""
    return call_llm(prompt, DBSchema)


def _repair_ui(ui, api, intent, architecture, error_summary) -> tuple[dict, int]:
    prompt = f"""You are the Repair Engine of an AI App Compiler.

The UI Schema has validation errors. Fix ONLY the issues listed below.

ERRORS TO FIX:
{error_summary}

CURRENT UI SCHEMA (fix this):
{json.dumps(ui, indent=2)}

API SCHEMA (use only these field names in UI components):
{json.dumps(api, indent=2)}

Rules:
- Replace incorrect field names with the exact API response_field names
- Add missing premium/pricing pages if needed
- Return the complete corrected UI schema JSON
"""
    return call_llm(prompt, UISchema)


def _repair_auth(auth, ui, api, intent, architecture, error_summary) -> tuple[dict, int]:
    prompt = f"""You are the Repair Engine of an AI App Compiler.

The Auth Schema has validation errors. Fix ONLY the issues listed below.

ERRORS TO FIX:
{error_summary}

CURRENT AUTH SCHEMA (fix this):
{json.dumps(auth, indent=2)}

UI SCHEMA roles used: {[r for p in ui.get('pages', []) for r in p.get('roles_allowed', [])]}
API SCHEMA roles used: {[r for rt in api.get('routes', []) for r in rt.get('roles_allowed', [])]}

Rules:
- Add any missing role definitions
- Ensure role names match exactly (case-sensitive)
- Return the complete corrected Auth schema JSON
"""
    return call_llm(prompt, AuthSchema)
