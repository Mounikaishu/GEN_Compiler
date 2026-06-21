"""
Stage 3c Output: DB Schema
Defines every table, column, type, constraints, and foreign keys.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class DBColumn(BaseModel):
    name: str
    col_type: str  # "VARCHAR", "INTEGER", "BOOLEAN", "FLOAT", "DATETIME", "TEXT", "UUID"
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False
    default: Optional[str] = None
    foreign_key: Optional[str] = None  # e.g. "users.id"
    description: str = ""


class DBTable(BaseModel):
    name: str  # snake_case table name
    entity_name: str  # PascalCase entity name
    columns: List[DBColumn]
    indexes: List[str] = Field(default_factory=list)  # column names to index
    description: str = ""


class DBSchema(BaseModel):
    schema_version: str = Field(default="1.0")
    app_name: str
    db_type: str = "SQLite"
    tables: List[DBTable]
