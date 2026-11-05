import pytest

from app.domain.errors import ConflictError
from app.models import Attempt, AttemptStatus, Submission
from app.evaluators.rubric import RUBRIC_CRITERIA
from app.services.evaluation_service import evaluation_service
from tests.conftest import VALID_CONTENT


def test_attempt_cannot_be_submitted_when_not_in_draft(db_session, seeded_problem):
    """Protects lifecycle integrity: an attempt already past DRAFT (e.g.
    already COMPLETED) must not be re-submittable into a new evaluation."""
    attempt = Attempt(problem_id=seeded_problem.id, status=AttemptStatus.COMPLETED)
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)

    with pytest.raises(ConflictError):
        evaluation_service.submit_attempt(db_session, attempt.id)


def test_submission_completeness_check_flags_missing_sections(db_session):
    """Protects the deterministic gate that runs before any AI call."""
    submission = Submission(
        attempt_id=1,
        content_type="text",
        content={
            "requirements_understanding": "Some real content here.",
            "classes_responsibilities": "",  # blank counts as missing
            # key_relationships omitted entirely
            "tradeoffs_assumptions": "Some trade-off reasoning.",
        },
    )
    missing = submission.missing_sections()
    assert set(missing) == {"classes_responsibilities", "key_relationships"}
    assert not submission.is_complete()


def test_rubric_has_fixed_expected_criteria():
    """Protects against silent rubric drift — the evaluation prompt and
    the schema both depend on this exact shape."""
    assert len(RUBRIC_CRITERIA) == 7
    required_keys = {"name", "description", "good_evidence", "weak_evidence"}
    names = set()
    for criterion in RUBRIC_CRITERIA:
        assert required_keys.issubset(criterion.keys())
        names.add(criterion["name"])
    assert "Requirement understanding" in names
    assert "Extensibility" in names
