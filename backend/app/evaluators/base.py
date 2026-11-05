from abc import ABC, abstractmethod


class EvaluationError(Exception):
    """Raised when an evaluator fails (LLM timeout/error, malformed
    output, etc). The service layer catches this and marks the
    Evaluation FAILED without touching the Submission."""


class Evaluator(ABC):
    """Strategy interface. Any evaluation mechanism (AI, rule-based,
    human-review-backed, a second AI provider...) implements this one
    method and can be plugged into EvaluationService without changing
    the submission flow, Attempt, or Evaluation models."""

    name: str

    @abstractmethod
    def evaluate(self, problem, submission_content: dict) -> dict:
        """Returns a dict matching schemas.evaluation.EvaluationResult.
        Raises EvaluationError on any failure (never returns partial or
        malformed output silently)."""
        raise NotImplementedError
