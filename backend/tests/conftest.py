import os

# Must run before any `app.*` import, since app/database.py reads
# DATABASE_URL at import time. Isolated test DB, separate from the dev DB.
os.environ["DATABASE_URL"] = "sqlite:///./test_lld_platform.db"
os.environ.pop("ANTHROPIC_API_KEY", None)  # force MockEvaluator unless a test opts in

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import Problem


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def seeded_problem(db_session):
    problem = Problem(
        title="Test Parking Lot",
        difficulty="Easy",
        summary="A test problem.",
        requirements="Handle multiple vehicle types.",
        constraints="Single entry/exit gate.",
        key_concepts="entity modeling",
    )
    db_session.add(problem)
    db_session.commit()
    db_session.refresh(problem)
    return problem


VALID_CONTENT = {
    "requirements_understanding": "The system must handle multiple vehicle types and levels.",
    "classes_responsibilities": "ParkingLot owns levels; Level owns spots; Ticket tracks assignment.",
    "key_relationships": "ParkingLot has-many Level; Level has-many ParkingSpot.",
    "tradeoffs_assumptions": "Assumed a single gate to keep scope small.",
}
