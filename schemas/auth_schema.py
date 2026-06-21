"""
Stage 3d Output: Auth Schema
Defines roles, permissions, JWT config, and access control matrix.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Permission(BaseModel):
    resource: str   # e.g. "contacts", "analytics", "payments"
    actions: List[str]  # "read", "write", "delete", "manage"


class RolePermissions(BaseModel):
    role: str
    permissions: List[Permission]
    is_admin: bool = False
    can_access_premium: bool = False


class AuthSchema(BaseModel):
    schema_version: str = Field(default="1.0")
    app_name: str
    auth_method: str = "JWT"  # JWT, Session, OAuth2
    roles: List[str]
    role_permissions: List[RolePermissions]
    jwt_config: Dict = Field(
        default_factory=lambda: {
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7
        }
    )
    public_routes: List[str] = Field(
        default_factory=list,
        description="Routes accessible without authentication"
    )
    premium_routes: List[str] = Field(
        default_factory=list,
        description="Routes requiring premium subscription"
    )
