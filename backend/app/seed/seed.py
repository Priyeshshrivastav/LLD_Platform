"""Run with: python -m app.seed.seed
Idempotent — skips problems that already exist (matched by title)."""

from app.database import Base, engine, SessionLocal
from app.models import Problem
from app.seed.problems_data import PROBLEMS


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_titles = {p.title for p in db.query(Problem.title).all()}
        created = 0
        for data in PROBLEMS:
            if data["title"] in existing_titles:
                continue
            db.add(Problem(**data))
            created += 1
        db.commit()
        print(f"Seed complete: {created} problem(s) created, {len(PROBLEMS) - created} already present.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
