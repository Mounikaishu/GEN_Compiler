"""
Final Output Schema + Pipeline State
Wraps all stage outputs + validation + repair logs into a single output.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    REPAIRED = "repaired"


class ValidationError(BaseModel):
    layer: str           # "UI→API", "API→DB", "Auth→UI", etc.
    field: str
    location: str        # page name / route / table name
    message: str
    severity: str = "error"  # "error" | "warning"


class RepairAction(BaseModel):
    layer: str           # which layer was repaired
    attempt: int
    error_fixed: str
    action_taken: str
    success: bool


class StageLog(BaseModel):
    stage: str
    status: StageStatus
    latency_ms: float = 0.0
    token_usage: int = 0
    error: Optional[str] = None


class FinalOutput(BaseModel):
    prompt: str
    app_name: str
    intent: Optional[Dict[str, Any]] = None
    architecture: Optional[Dict[str, Any]] = None
    ui_schema: Optional[Dict[str, Any]] = None
    api_schema: Optional[Dict[str, Any]] = None
    db_schema: Optional[Dict[str, Any]] = None
    auth_schema: Optional[Dict[str, Any]] = None
    business_logic: Optional[Dict[str, Any]] = None
    validation_errors: List[ValidationError] = Field(default_factory=list)
    repair_actions: List[RepairAction] = Field(default_factory=list)
    stage_logs: List[StageLog] = Field(default_factory=list)
    generated_files: Dict[str, str] = Field(default_factory=dict)  # filename -> content
    assumptions: List[str] = Field(default_factory=list)
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    success: bool = False
    error_message: Optional[str] = None
