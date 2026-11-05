from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.errors import NotFoundError
from app.models import Problem
from app.schemas.problem import ProblemListItem, ProblemDetail
from app.schemas.attempt import AttemptOut
from app.services.evaluation_service import evaluation_service

router = APIRouter(tags=["problems"])


@router.get("/problems", response_model=list[ProblemListItem])
def list_problems(db: Session = Depends(get_db)):
    return db.query(Problem).order_by(Problem.id).all()


@router.get("/problems/{problem_id}", response_model=ProblemDetail)
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.get(Problem, problem_id)
    if not problem:
        raise NotFoundError(f"Problem {problem_id} not found")
    return problem


@router.get("/problems/{problem_id}/attempts", response_model=list[AttemptOut])
def list_problem_attempts(problem_id: int, db: Session = Depends(get_db)):
    problem = db.get(Problem, problem_id)
    if not problem:
        raise NotFoundError(f"Problem {problem_id} not found")
    return evaluation_service.list_attempts(db, problem_id=problem_id)


@router.post("/problems/{problem_id}/attempts", response_model=AttemptOut, status_code=201)
def start_attempt(problem_id: int, db: Session = Depends(get_db)):
    return evaluation_service.start_attempt(db, problem_id)
