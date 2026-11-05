import json
from types import SimpleNamespace

import pytest

from app.evaluators.ai_evaluator import AIEvaluator
from app.evaluators.base import Evaluator, EvaluationError
from app.evaluators.rubric import RUBRIC_CRITERIA
from app.models import Attempt, AttemptStatus, Submission, Evaluation, EvaluationStatus
from app.services.evaluation_service import evaluation_service
from tests.conftest import VALID_CONTENT


class FakeProblem:
    title = "Fake Problem"
    requirements = "Fake requirements."
    constraints = "Fake constraints."


def _valid_llm_result_dict():
    return {
        "summary": "A reasonable design overall.",
        "criteria": [
            {
                "name": c["name"],
                "score": 7,
                "evidence": "Evidence text.",
                "classification": "improvement",
                "concern": "Minor concern.",
                "suggestion": "A suggestion.",
                "confidence": 6,
            }
            for c in RUBRIC_CRITERIA
        ],
        "strengths": ["Clear class list."],
        "priority_improvements": ["Add more edge-case reasoning."],
        "tradeoffs_identified": ["Chose simplicity over flexibility."],
    }


def _fake_anthropic_response(text: str):
    """Mimics httpx.Response enough for AIEvaluator to consume."""
    return SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {"content": [{"type": "text", "text": text}]},
    )


def test_ai_evaluator_builds_prompt_with_problem_rubric_and_submission():
    """Protects that nothing silently drops from the evaluation input."""
    evaluator = AIEvaluator(api_key="fake-key")
    submission_content = {"requirements_understanding": "UNIQUE_MARKER_TEXT_123"}
    prompt = evaluator._build_prompt(FakeProblem(), submission_content)

    assert FakeProblem.title in prompt
    assert RUBRIC_CRITERIA[0]["name"] in prompt
    assert "UNIQUE_MARKER_TEXT_123" in prompt


def test_ai_evaluator_parses_valid_response(monkeypatch):
    """Protects the happy path: valid JSON in -> validated dict out."""
    evaluator = AIEvaluator(api_key="fake-key")
    valid_text = json.dumps(_valid_llm_result_dict())

    monkeypatch.setattr(
        "app.evaluators.ai_evaluator.httpx.post",
        lambda *a, **k: _fake_anthropic_response(valid_text),
    )

    result = evaluator.evaluate(FakeProblem(), VALID_CONTENT)
    assert result["summary"] == "A reasonable design overall."
    assert len(result["criteria"]) == len(RUBRIC_CRITERIA)


def test_ai_evaluator_raises_on_malformed_json(monkeypatch):
    """Protects Case 3 (LLM failure) from the plan — a broken response
    must raise EvaluationError, never crash the request or silently
    store garbage."""
    evaluator = AIEvaluator(api_key="fake-key")
    monkeypatch.setattr(
        "app.evaluators.ai_evaluator.httpx.post",
        lambda *a, **k: _fake_anthropic_response("this is not JSON at all"),
    )

    with pytest.raises(EvaluationError):
        evaluator.evaluate(FakeProblem(), VALID_CONTENT)


class AlwaysFailsEvaluator(Evaluator):
    name = "always_fails"

    def evaluate(self, problem, submission_content):
        raise EvaluationError("simulated evaluator failure")


def test_evaluation_service_marks_failed_and_preserves_submission(monkeypatch, db_session, seeded_problem):
    """Protects 'never lose learner work': a failing evaluator must not
    touch the Submission, only the Evaluation record."""
    attempt = Attempt(problem_id=seeded_problem.id, status=AttemptStatus.EVALUATING)
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)

    submission = Submission(attempt_id=attempt.id, content_type="text", content=dict(VALID_CONTENT))
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)

    evaluation = Evaluation(
        submission_id=submission.id, evaluator_type="always_fails", status=EvaluationStatus.PENDING
    )
    db_session.add(evaluation)
    db_session.commit()
    db_session.refresh(evaluation)

    monkeypatch.setattr(
        "app.services.evaluation_service.get_default_evaluator",
        lambda: AlwaysFailsEvaluator(),
    )

    evaluation_service.run_evaluation(evaluation.id)

    db_session.refresh(evaluation)
    db_session.refresh(submission)
    db_session.refresh(attempt)

    assert evaluation.status == EvaluationStatus.FAILED
    assert "simulated evaluator failure" in evaluation.error_message
    assert attempt.status == AttemptStatus.FAILED
    assert submission.content == VALID_CONTENT  # untouched
