import os

from app.evaluators.base import Evaluator, EvaluationError
from app.evaluators.ai_evaluator import AIEvaluator
from app.evaluators.mock_evaluator import MockEvaluator


def get_default_evaluator() -> Evaluator:
    """Selects the evaluator: real AI (Gemini) if a key is configured,
    otherwise the mock evaluator so the whole flow stays testable without one.
    This is the one place that decides which Evaluator implementation
    EvaluationService uses — swapping/adding evaluators never touches
    the service or the API layer."""
    if os.getenv("GEMINI_API_KEY"):
        return AIEvaluator()
    return MockEvaluator()


__all__ = ["Evaluator", "EvaluationError", "AIEvaluator", "MockEvaluator", "get_default_evaluator"]
