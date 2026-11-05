from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Problem(Base):
    """A curated LLD problem. Static reference data — seeded once, never
    created/edited through the API in this MVP."""

    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    difficulty = Column(String(20), nullable=False)  # Easy / Medium / Hard
    summary = Column(String(300), nullable=False)
    requirements = Column(Text, nullable=False)
    constraints = Column(Text, nullable=False)
    key_concepts = Column(Text, nullable=False)  # comma-separated for MVP simplicity

    attempts = relationship("Attempt", back_populates="problem")
