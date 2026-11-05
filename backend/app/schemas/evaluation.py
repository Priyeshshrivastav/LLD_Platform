from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Classification(str, Enum):
    ISSUE = "issue"
    IMPROVEMENT = "improvement"
    TRADEOFF = "tradeoff"
    PREFERENCE = "preference"


class CriterionResult(BaseModel):
    name: str
    score: int = Field(ge=0, le=10)
    evidence: str
    classification: Classification
    concern: str
    suggestion: str
    confidence: int = Field(ge=0, le=10)


class EvaluationResult(BaseModel):
    """The exact JSON shape the AI evaluator must return. Used both to
    validate the model's output and to type the stored `result` field."""

    summary: str
    criteria: list[CriterionResult]
    strengths: list[str]
    priority_improvements: list[str]
    tradeoffs_identified: list[str]


class EvaluationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submission_id: int
    evaluator_type: str
    status: str
    result: Optional[dict] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None
