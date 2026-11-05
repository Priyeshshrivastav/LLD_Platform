from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attempt import AttemptOut, AttemptDetail, AttemptSummary
from app.schemas.submission import SubmissionContentIn, SubmissionOut
from app.schemas.evaluation import EvaluationOut
from app.services.evaluation_service import evaluation_service

router = APIRouter(tags=["attempts"])


@router.get("/attempts", response_model=list[AttemptSummary])
def list_attempts(problem_id: int | None = None, db: Session = Depends(get_db)):
    attempts = evaluation_service.list_attempts(db, problem_id=problem_id)
    out = []
    for attempt in attempts:
        evaluation = evaluation_service.latest_evaluation(db, attempt)
        out.append(
            AttemptSummary(
                attempt=AttemptOut.model_validate(attempt),
                problem_title=attempt.problem.title,
                evaluation_status=evaluation.status.value if evaluation else None,
            )
        )
    return out


@router.get("/attempts/{attempt_id}", response_model=AttemptDetail)
def get_attempt(attempt_id: int, db: Session = Depends(get_db)):
    attempt = evaluation_service.get_attempt(db, attempt_id)
    evaluation = evaluation_service.latest_evaluation(db, attempt)
    return AttemptDetail(
        attempt=AttemptOut.model_validate(attempt),
        submission=SubmissionOut.model_validate(attempt.submission) if attempt.submission else None,
        evaluation=EvaluationOut.model_validate(evaluation) if evaluation else None,
    )


@router.put("/attempts/{attempt_id}/submission", response_model=SubmissionOut)
def save_submission(attempt_id: int, content: SubmissionContentIn, db: Session = Depends(get_db)):
    submission = evaluation_service.save_draft(db, attempt_id, content.model_dump())
    return submission


@router.post("/attempts/{attempt_id}/submit", response_model=EvaluationOut)
def submit_attempt(attempt_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    evaluation = evaluation_service.submit_attempt(db, attempt_id)
    # Non-blocking: request returns immediately with EVALUATING/PENDING;
    # the actual LLM call happens after the response is sent.
    background_tasks.add_task(evaluation_service.run_evaluation, evaluation.id)
    return evaluation
