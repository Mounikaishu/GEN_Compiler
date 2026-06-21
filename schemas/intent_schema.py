"""
Stage 1 Output: Intent Schema
Represents the parsed understanding of what the user wants to build.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class IntentSchema(BaseModel):
    schema_version: str = Field(default="1.0", description="Schema version for IR tracking")
    app_name: str = Field(..., description="Name of the application")
    app_type: str = Field(..., description="Type: CRM, LMS, ERP, eCommerce, etc.")
    description: str = Field(..., description="One-sentence description of what the app does")
    features: List[str] = Field(..., description="List of core features requested")
    roles: List[str] = Field(..., description="User roles in the system (e.g. Admin, User, Manager)")
    entities: List[str] = Field(..., description="Core data entities (e.g. User, Contact, Product)")
    has_premium: bool = Field(default=False, description="Whether the app has premium/paid features")
    has_payments: bool = Field(default=False, description="Whether the app handles payments")
    has_auth: bool = Field(default=True, description="Whether the app requires authentication")
    has_analytics: bool = Field(default=False, description="Whether the app includes analytics/reporting")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made for underspecified inputs")
    clarifications_needed: List[str] = Field(default_factory=list, description="Questions if prompt was ambiguous")
