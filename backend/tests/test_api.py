from app.models import Attempt, AttemptStatus, Submission, Evaluation, EvaluationStatus
from tests.conftest import VALID_CONTENT


def test_start_attempt_on_nonexistent_problem_returns_404(client):
    """Protects input validation at the API boundary."""
    response = client.post("/problems/9999/attempts")
    assert response.status_code == 404


def test_submit_incomplete_submission_returns_400_with_missing_sections(client, seeded_problem):
    """Protects the deterministic completeness gate at the API layer."""
    attempt = client.post(f"/problems/{seeded_problem.id}/attempts").json()
    attempt_id = attempt["id"]

    client.put(
        f"/attempts/{attempt_id}/submission",
        json={"requirements_understanding": "Only one section filled in."},
    )

    response = client.post(f"/attempts/{attempt_id}/submit")
    assert response.status_code == 400
    body = response.json()
    assert "classes_responsibilities" in body["missing_sections"]
    assert "key_relationships" in body["missing_sections"]
    assert "tradeoffs_assumptions" in body["missing_sections"]


def test_double_submit_returns_409(client, seeded_problem):
    """Protects idempotency (Case 5 from the plan): submitting an
    already-submitted/evaluated attempt must not create a duplicate
    Evaluation."""
    attempt = client.post(f"/problems/{seeded_problem.id}/attempts").json()
    attempt_id = attempt["id"]
    client.put(f"/attempts/{attempt_id}/submission", json=VALID_CONTENT)

    first = client.post(f"/attempts/{attempt_id}/submit")
    assert first.status_code == 200

    second = client.post(f"/attempts/{attempt_id}/submit")
    assert second.status_code == 409


def test_retry_on_non_failed_evaluation_returns_409(client, seeded_problem):
    """Protects the retry state guard — retry is only valid from FAILED."""
    attempt = client.post(f"/problems/{seeded_problem.id}/attempts").json()
    attempt_id = attempt["id"]
    client.put(f"/attempts/{attempt_id}/submission", json=VALID_CONTENT)
    submit_response = client.post(f"/attempts/{attempt_id}/submit")
    evaluation_id = submit_response.json()["id"]

    # MockEvaluator runs synchronously within the test client's request
    # cycle, so by now the evaluation has already completed.
    completed = client.get(f"/evaluations/{evaluation_id}").json()
    assert completed["status"] == "COMPLETED"

    retry_response = client.post(f"/evaluations/{evaluation_id}/retry")
    assert retry_response.status_code == 409


def test_get_attempt_with_pending_evaluation_does_not_crash(client, db_session, seeded_problem):
    """Protects the polling contract: the frontend polls GET
    /attempts/{id} while an evaluation is still PENDING, and the
    response must be well-formed with result=None, not error out."""
    attempt = Attempt(problem_id=seeded_problem.id, status=AttemptStatus.EVALUATING)
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)

    submission = Submission(attempt_id=attempt.id, content_type="text", content=dict(VALID_CONTENT))
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)

    evaluation = Evaluation(
        submission_id=submission.id, evaluator_type="ai_v1", status=EvaluationStatus.PENDING
    )
    db_session.add(evaluation)
    db_session.commit()

    response = client.get(f"/attempts/{attempt.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["evaluation"]["status"] == "PENDING"
    assert body["evaluation"]["result"] is None
