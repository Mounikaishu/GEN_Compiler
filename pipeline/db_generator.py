"""
Stage 3c — DB Generator
Generates complete database schema with tables, columns, types, and foreign keys.
"""
import time
import json
from schemas.db_schema import DBSchema
from pipeline.llm_client import call_llm

DB_PROMPT = """You are Stage 3c of an AI App Compiler — the Database Schema Generator.

Generate a complete relational database schema.

RULES:
1. Every entity in architecture.entities must map to exactly one table
2. Every table MUST have an 'id' column (UUID, primary key)
3. Every table should have 'created_at' and 'updated_at' (DATETIME)
4. Foreign keys must reference real tables using format "table_name.column_name"
5. Use snake_case for ALL table and column names
6. Many-to-many relationships need a junction table
7. If has_premium=true, users table must have 'is_premium' BOOLEAN column
8. If has_payments=true, include a 'payments' table

INTENT: {intent}
ARCHITECTURE: {architecture}

Return JSON:
{{
  "schema_version": "1.0",
  "app_name": "string",
  "db_type": "SQLite",
  "tables": [
    {{
      "name": "snake_case_table_name",
      "entity_name": "PascalCaseEntityName",
      "description": "what this table stores",
      "indexes": ["column_name_to_index"],
      "columns": [
        {{
          "name": "column_name",
          "col_type": "UUID|VARCHAR|INTEGER|BOOLEAN|FLOAT|DATETIME|TEXT",
          "primary_key": false,
          "nullable": true,
          "unique": false,
          "default": null,
          "foreign_key": null,
          "description": "what this column stores"
        }}
      ]
    }}
  ]
}}
"""


def generate_db(intent: dict, architecture: dict) -> tuple[dict, float, int]:
    """Run Stage 3c: DB Schema Generation."""
    start = time.time()
    filled = DB_PROMPT.format(
        intent=json.dumps(intent, indent=2),
        architecture=json.dumps(architecture, indent=2)
    )
    result, tokens = call_llm(filled, DBSchema)
    latency = (time.time() - start) * 1000
    return result, latency, tokens
