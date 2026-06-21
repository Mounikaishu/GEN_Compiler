"""
Stage 3b Output: API Schema
Defines every endpoint, its method, request body, and response shape.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class APIField(BaseModel):
    name: str
    field_type: str  # "string", "integer", "boolean", "float", "datetime", "uuid"
    required: bool = True
    description: str = ""


class APIRoute(BaseModel):
    path: str  # e.g. "/api/contacts"
    method: str  # GET, POST, PUT, DELETE, PATCH
    summary: str
    tags: List[str] = Field(default_factory=list)
    auth_required: bool = True
    roles_allowed: List[str] = Field(default_factory=list)  # empty = all authenticated
    request_fields: List[APIField] = Field(default_factory=list)
    response_fields: List[APIField] = Field(default_factory=list)
    db_table: Optional[str] = None  # which DB table this route operates on
    is_premium: bool = False


class APISchema(BaseModel):
    schema_version: str = Field(default="1.0")
    app_name: str
    base_path: str = "/api"
    routes: List[APIRoute]
    auth_routes: List[APIRoute] = Field(
        default_factory=list,
        description="Login, register, refresh token endpoints"
    )
