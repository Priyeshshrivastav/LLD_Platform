import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class AttemptStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def utcnow():
    return datetime.now(timezone.utc)


class Attempt(Base):
    """One learner's try at one Problem. Owns the lifecycle state; the
    actual design content lives on the linked Submission."""

    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    status = Column(Enum(AttemptStatus), nullable=False, default=AttemptStatus.DRAFT)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    problem = relationship("Problem", back_populates="attempts")
    submission = relationship(
        "Submission", back_populates="attempt", uselist=False, cascade="all, delete-orphan"
    )
