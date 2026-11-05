from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SubmissionContentIn(BaseModel):
    """Sections are optional here so the editor can autosave a partial
    draft; the completeness check only runs at submit time, not on
    every save."""

    requirements_understanding: Optional[str] = None
    classes_responsibilities: Optional[str] = None
    key_relationships: Optional[str] = None
    tradeoffs_assumptions: Optional[str] = None


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attempt_id: int
    content_type: str
    content: dict
    updated_at: datetime
    submitted_at: Optional[datetime] = None
