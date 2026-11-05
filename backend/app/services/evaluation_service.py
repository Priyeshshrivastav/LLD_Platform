from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.domain.errors import NotFoundError, ValidationError, ConflictError
from app.evaluators import get_default_evaluator, EvaluationError
from app.models import Problem, Attempt, AttemptStatus, Submission, Evaluation, EvaluationStatus


def utcnow():
    return datetime.now(timezone.utc)


class EvaluationService:
    """The only place that knows the full attempt/submission/evaluation
    flow end to end. Domain objects stay simple; orchestration,
    state-transition guards, and evaluator selection live here."""

    # ---------- Problems / Attempts ----------

    def start_attempt(self, db: Session, problem_id: int) -> Attempt:
        problem = db.get(Problem, problem_id)
        if not problem:
            raise NotFoundError(f"Problem {problem_id} not found")

        attempt = Attempt(problem_id=problem_id, status=AttemptStatus.DRAFT)
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # Create the (initially empty) submission up front so the editor
        # always has something to PUT against.
        submission = Submission(attempt_id=attempt.id, content_type="text", content={})
        db.add(submission)
        db.commit()

        return attempt

    def get_attempt(self, db: Session, attempt_id: int) -> Attempt:
        attempt = db.get(Attempt, attempt_id)
        if not attempt:
            raise NotFoundError(f"Attempt {attempt_id} not found")
        return attempt

    def list_attempts(self, db: Session, problem_id: int | None = None) -> list[Attempt]:
        query = db.query(Attempt)
        if problem_id is not None:
            query = query.filter(Attempt.problem_id == problem_id)
        return query.order_by(Attempt.created_at.desc()).all()

    def latest_evaluation(self, db: Session, attempt: Attempt) -> Evaluation | None:
        if not attempt.submission:
            return None
        return (
            db.query(Evaluation)
            .filter(Evaluation.submission_id == attempt.submission.id)
            .order_by(Evaluation.created_at.desc())
            .first()
        )

    # ---------- Submissions ----------

    def save_draft(self, db: Session, attempt_id: int, content: dict) -> Submission:
        attempt = self.get_attempt(db, attempt_id)
        if attempt.status != AttemptStatus.DRAFT:
            raise ConflictError(
                f"Cannot edit submission — attempt is {attempt.status.value}, not DRAFT"
            )

        submission = attempt.submission
        if submission is None:
            submission = Submission(attempt_id=attempt.id, content_type="text", content={})
            db.add(submission)

        # Merge rather than overwrite so autosave of a single changed
        # section never wipes the others.
        merged = dict(submission.content or {})
        merged.update({k: v for k, v in content.items() if v is not None})
        submission.content = merged

        db.commit()
        db.refresh(submission)
        return submission

    # ---------- Submit + evaluate ----------

    def submit_attempt(self, db: Session, attempt_id: int) -> Evaluation:
        attempt = self.get_attempt(db, attempt_id)

        if attempt.status != AttemptStatus.DRAFT:
            # Handles double-submit / re-submit idempotently: 409, not a
            # duplicate Evaluation.
            raise ConflictError(
                f"Attempt {attempt_id} cannot be submitted — status is {attempt.status.value}"
            )

        submission = attempt.submission
        if submission is None:
            raise ValidationError("No submission found for this attempt")

        missing = submission.missing_sections()
        if missing:
            raise ValidationError(
                "Submission is incomplete", details={"missing_sections": missing}
            )

        submission.submitted_at = utcnow()
        attempt.status = AttemptStatus.SUBMITTED

        evaluator = get_default_evaluator()
        evaluation = Evaluation(
            submission_id=submission.id,
            evaluator_type=evaluator.name,
            status=EvaluationStatus.PENDING,
        )
        db.add(evaluation)

        attempt.status = AttemptStatus.EVALUATING
        db.commit()
        db.refresh(evaluation)

        return evaluation

    def run_evaluation(self, evaluation_id: int) -> None:
        """Runs in a background task, so it opens its own DB session
        rather than reusing the (already-closed) request-scoped one."""
        db = SessionLocal()
        try:
            evaluation = db.get(Evaluation, evaluation_id)
            if evaluation is None:
                return

            submission = evaluation.submission
            attempt = submission.attempt
            problem = attempt.problem

            evaluator = get_default_evaluator()
            try:
                result = evaluator.evaluate(problem, submission.content)
            except EvaluationError as exc:
                evaluation.status = EvaluationStatus.FAILED
                evaluation.error_message = str(exc)[:1000]
                attempt.status = AttemptStatus.FAILED
                db.commit()
                return

            evaluation.status = EvaluationStatus.COMPLETED
            evaluation.result = result
            evaluation.completed_at = utcnow()
            evaluation.error_message = None
            attempt.status = AttemptStatus.COMPLETED
            db.commit()
        finally:
            db.close()

    def retry_evaluation(self, db: Session, evaluation_id: int) -> Evaluation:
        evaluation = db.get(Evaluation, evaluation_id)
        if evaluation is None:
            raise NotFoundError(f"Evaluation {evaluation_id} not found")

        if evaluation.status != EvaluationStatus.FAILED:
            raise ConflictError(
                f"Evaluation {evaluation_id} cannot be retried — status is {evaluation.status.value}"
            )

        evaluation.status = EvaluationStatus.PENDING
        evaluation.error_message = None
        evaluation.retry_count += 1

        attempt = evaluation.submission.attempt
        attempt.status = AttemptStatus.EVALUATING

        db.commit()
        db.refresh(evaluation)
        return evaluation

    def get_evaluation(self, db: Session, evaluation_id: int) -> Evaluation:
        evaluation = db.get(Evaluation, evaluation_id)
        if evaluation is None:
            raise NotFoundError(f"Evaluation {evaluation_id} not found")
        return evaluation


evaluation_service = EvaluationService()
