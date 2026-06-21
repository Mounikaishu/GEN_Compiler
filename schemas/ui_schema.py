"""
Stage 3a Output: UI Schema
Defines every page, component, and field in the application UI.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class UIField(BaseModel):
    name: str
    field_type: str  # "text", "email", "password", "select", "table", "chart", "button"
    label: str
    required: bool = False
    api_source: Optional[str] = None  # which API endpoint populates this field


class UIComponent(BaseModel):
    name: str
    component_type: str  # "form", "table", "card", "chart", "navbar", "sidebar"
    fields: List[UIField] = Field(default_factory=list)
    roles_allowed: List[str] = Field(default_factory=list)  # empty = all roles
    api_endpoint: Optional[str] = None  # primary API endpoint for this component


class UIPage(BaseModel):
    name: str
    route: str  # e.g. "/dashboard"
    is_protected: bool = True
    roles_allowed: List[str] = Field(default_factory=list)  # empty = all authenticated
    components: List[UIComponent] = Field(default_factory=list)
    is_premium: bool = False


class UISchema(BaseModel):
    schema_version: str = Field(default="1.0")
    app_name: str
    pages: List[UIPage]
    global_components: List[str] = Field(
        default_factory=list,
        description="Components present on all pages (Navbar, Sidebar, Footer)"
    )
