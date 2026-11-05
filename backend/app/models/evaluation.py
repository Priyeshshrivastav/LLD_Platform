import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class EvaluationStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def utcnow():
    return datetime.now(timezone.utc)


class Evaluation(Base):
    """Record of one evaluation run against a Submission. Separated from
    Submission so retries update this row rather than touching the
    learner's original content."""

    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    evaluator_type = Column(String(50), nullable=False)  # e.g. "ai_v1", "mock_v1"
    status = Column(Enum(EvaluationStatus), nullable=False, default=EvaluationStatus.PENDING)
    result = Column(JSON, nullable=True)  # structured output, see schemas.evaluation
    error_message = Column(String(1000), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    submission = relationship("Submission", back_populates="evaluations")
