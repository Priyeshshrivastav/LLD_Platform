from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base

# The structured-text sections a submission must contain. Kept here (not
# scattered across schemas/services) so completeness-checking and the
# editor UI have one shared source of truth.
REQUIRED_SECTIONS = [
    "requirements_understanding",
    "classes_responsibilities",
    "key_relationships",
    "tradeoffs_assumptions",
]


def utcnow():
    return datetime.now(timezone.utc)


class Submission(Base):
    """The learner's design content for an Attempt. Content is a typed,
    versionable payload (content_type) so a future format like a diagram
    is additive here, not a change to Attempt or Evaluation."""

    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=False, unique=True)
    content_type = Column(String(20), nullable=False, default="text")
    content = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    submitted_at = Column(DateTime, nullable=True)

    attempt = relationship("Attempt", back_populates="submission")
    evaluations = relationship(
        "Evaluation", back_populates="submission", cascade="all, delete-orphan"
    )

    def missing_sections(self) -> list[str]:
        """Deterministic completeness check — runs before any AI call."""
        content = self.content or {}
        return [
            section
            for section in REQUIRED_SECTIONS
            if not str(content.get(section, "")).strip()
        ]

    def is_complete(self) -> bool:
        return len(self.missing_sections()) == 0
