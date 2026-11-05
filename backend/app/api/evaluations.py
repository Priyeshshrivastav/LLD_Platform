from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.evaluation import EvaluationOut
from app.services.evaluation_service import evaluation_service

router = APIRouter(tags=["evaluations"])


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationOut)
def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    return evaluation_service.get_evaluation(db, evaluation_id)


@router.post("/evaluations/{evaluation_id}/retry", response_model=EvaluationOut)
def retry_evaluation(evaluation_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    evaluation = evaluation_service.retry_evaluation(db, evaluation_id)
    background_tasks.add_task(evaluation_service.run_evaluation, evaluation.id)
    return evaluation
