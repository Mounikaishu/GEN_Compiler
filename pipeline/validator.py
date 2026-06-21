"""
Stage 4 — Cross-Layer Validator
The most critical stage: detects inconsistencies across UI, API, DB, and Auth layers.
This is what separates a compiler from a prompt wrapper.
"""
from typing import List
from schemas.output_schema import ValidationError


def validate(
    ui: dict,
    api: dict,
    db: dict,
    auth: dict,
    intent: dict,
) -> List[ValidationError]:
    """
    Run all cross-layer validation checks.
    Returns a list of ValidationError objects (empty = all good).
    """
    errors: List[ValidationError] = []

    errors.extend(_check_ui_api_consistency(ui, api))
    errors.extend(_check_api_db_consistency(api, db))
    errors.extend(_check_auth_role_consistency(ui, api, auth))
    errors.extend(_check_premium_requirements(ui, api, db, auth, intent))
    errors.extend(_check_foreign_keys(db))
    errors.extend(_check_payment_requirements(ui, db, intent))

    return errors


# ── Check 1: UI fields must exist in API response fields ─────────────────────
def _check_ui_api_consistency(ui: dict, api: dict) -> List[ValidationError]:
    errors = []
    all_api_response_fields = set()
    for route in api.get("routes", []) + api.get("auth_routes", []):
        for f in route.get("response_fields", []):
            all_api_response_fields.add(f["name"])

    for page in ui.get("pages", []):
        for comp in page.get("components", []):
            for field in comp.get("fields", []):
                fname = field["name"]
                ftype = field.get("field_type", "")
                # Only validate data fields, not UI-only elements
                if ftype not in ("button", "chart") and fname not in all_api_response_fields:
                    errors.append(ValidationError(
                        layer="UI→API",
                        field=fname,
                        location=f"{page['name']}.{comp['name']}",
                        message=f"Field '{fname}' used in UI component '{comp['name']}' on page '{page['name']}' "
                                f"not found in any API response_fields. API has: {sorted(list(all_api_response_fields))[:10]}",
                        severity="error"
                    ))
    return errors


# ── Check 2: API response fields must exist in DB columns ───────────────────
def _check_api_db_consistency(api: dict, db: dict) -> List[ValidationError]:
    errors = []
    # Build map: table_name -> set of column names
    db_columns: dict[str, set] = {}
    for table in db.get("tables", []):
        db_columns[table["name"]] = {col["name"] for col in table.get("columns", [])}

    for route in api.get("routes", []):
        table = route.get("db_table")
        if not table:
            continue
        if table not in db_columns:
            errors.append(ValidationError(
                layer="API→DB",
                field="db_table",
                location=f"{route['method']} {route['path']}",
                message=f"Route references table '{table}' which does not exist in DB schema. "
                        f"Available tables: {list(db_columns.keys())}",
                severity="error"
            ))
            continue
        for field in route.get("response_fields", []):
            fname = field["name"]
            # Skip computed/meta fields
            if fname in ("access_token", "token_type", "message", "success", "count", "total"):
                continue
            if fname not in db_columns[table]:
                errors.append(ValidationError(
                    layer="API→DB",
                    field=fname,
                    location=f"{route['method']} {route['path']}",
                    message=f"API response field '{fname}' not found in table '{table}' columns. "
                            f"Table has: {sorted(list(db_columns[table]))[:10]}",
                    severity="error"
                ))
    return errors


# ── Check 3: Roles must be consistent across UI, API, and Auth ───────────────
def _check_auth_role_consistency(ui: dict, api: dict, auth: dict) -> List[ValidationError]:
    errors = []
    auth_roles = set(auth.get("roles", []))

    # Check UI roles
    for page in ui.get("pages", []):
        for role in page.get("roles_allowed", []):
            if role and role not in auth_roles:
                errors.append(ValidationError(
                    layer="Auth→UI",
                    field="roles_allowed",
                    location=f"Page: {page['name']}",
                    message=f"Role '{role}' used in UI page but not defined in Auth schema. "
                            f"Auth roles: {list(auth_roles)}",
                    severity="error"
                ))

    # Check API roles
    for route in api.get("routes", []):
        for role in route.get("roles_allowed", []):
            if role and role not in auth_roles:
                errors.append(ValidationError(
                    layer="Auth→API",
                    field="roles_allowed",
                    location=f"{route['method']} {route['path']}",
                    message=f"Role '{role}' used in API route but not defined in Auth schema.",
                    severity="error"
                ))
    return errors


# ── Check 4: Premium features require proper infrastructure ─────────────────
def _check_premium_requirements(ui, api, db, auth, intent) -> List[ValidationError]:
    errors = []
    if not intent.get("has_premium", False):
        return errors

    # Check pricing page exists in UI
    page_names = [p["name"].lower() for p in ui.get("pages", [])]
    if not any("pric" in n or "upgrade" in n or "plan" in n or "subscri" in n for n in page_names):
        errors.append(ValidationError(
            layer="UI",
            field="pages",
            location="UI Schema",
            message="App has premium features but no Pricing/Upgrade page found in UI schema.",
            severity="warning"
        ))

    # Check premium roles in auth
    role_perms = auth.get("role_permissions", [])
    has_premium_role = any(r.get("can_access_premium") for r in role_perms)
    if not has_premium_role:
        errors.append(ValidationError(
            layer="Auth",
            field="can_access_premium",
            location="Auth Schema",
            message="App has premium features but no role has can_access_premium=true in Auth schema.",
            severity="warning"
        ))
    return errors


# ── Check 5: Foreign keys reference real tables ──────────────────────────────
def _check_foreign_keys(db: dict) -> List[ValidationError]:
    errors = []
    table_names = {t["name"] for t in db.get("tables", [])}

    for table in db.get("tables", []):
        for col in table.get("columns", []):
            fk = col.get("foreign_key")
            if fk:
                ref_table = fk.split(".")[0]
                if ref_table not in table_names:
                    errors.append(ValidationError(
                        layer="DB",
                        field=col["name"],
                        location=f"Table: {table['name']}",
                        message=f"Foreign key '{fk}' references table '{ref_table}' "
                                f"which does not exist. Known tables: {sorted(list(table_names))}",
                        severity="error"
                    ))
    return errors


# ── Check 6: Payment feature needs a payments table ─────────────────────────
def _check_payment_requirements(ui, db, intent) -> List[ValidationError]:
    errors = []
    if not intent.get("has_payments", False):
        return errors

    table_names = [t["name"].lower() for t in db.get("tables", [])]
    if not any("payment" in n or "transaction" in n or "invoice" in n for n in table_names):
        errors.append(ValidationError(
            layer="DB",
            field="tables",
            location="DB Schema",
            message="App has payments enabled but no payments/transactions table found in DB schema.",
            severity="error"
        ))
    return errors
