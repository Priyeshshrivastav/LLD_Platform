from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.submission import SubmissionOut
from app.schemas.evaluation import EvaluationOut


class AttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class AttemptDetail(BaseModel):
    """Attempt plus its submission and latest evaluation, if they exist —
    powers the attempt/feedback page in one call."""

    attempt: AttemptOut
    submission: Optional[SubmissionOut] = None
    evaluation: Optional[EvaluationOut] = None


class AttemptSummary(BaseModel):
    """Row shape for the attempt history list."""

    attempt: AttemptOut
    problem_title: str
    evaluation_status: Optional[str] = None
