"""
Stage 2 Output: Architecture Schema
Represents the high-level app structure derived from intent.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class DataRelationship(BaseModel):
    from_entity: str
    to_entity: str
    relation_type: str  # "one_to_many", "many_to_many", "one_to_one"
    description: str


class AppFlow(BaseModel):
    name: str
    steps: List[str]
    actors: List[str]  # roles involved


class ArchitectureSchema(BaseModel):
    schema_version: str = Field(default="1.0")
    app_name: str
    pages: List[str] = Field(..., description="All pages/screens in the app")
    entities: List[str] = Field(..., description="All data entities")
    flows: List[AppFlow] = Field(..., description="User flows / use cases")
    data_relationships: List[DataRelationship] = Field(..., description="Entity relationships")
    tech_stack: dict = Field(
        default_factory=lambda: {"frontend": "React", "backend": "FastAPI", "database": "SQLite"}
    )
