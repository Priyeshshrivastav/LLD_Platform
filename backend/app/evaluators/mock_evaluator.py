from app.evaluators.base import Evaluator
from app.evaluators.rubric import RUBRIC_CRITERIA


class MockEvaluator(Evaluator):
    """Deterministic stand-in for AIEvaluator, used automatically when no
    ANTHROPIC_API_KEY is set. Lets the full submit -> evaluate -> feedback
    loop be smoke-tested end-to-end with zero external dependencies.
    Never used if a real API key is configured."""

    name = "mock_v1"

    def evaluate(self, problem, submission_content: dict) -> dict:
        criteria = []
        for c in RUBRIC_CRITERIA:
            section_key = self._closest_section(c["name"])
            text = str(submission_content.get(section_key, "")).strip()
            has_content = len(text) > 20
            criteria.append(
                {
                    "name": c["name"],
                    "score": 7 if has_content else 3,
                    "evidence": (text[:120] if has_content else "No substantial content found."),
                    "classification": "improvement" if has_content else "issue",
                    "concern": (
                        "Reasoning could be more specific." if has_content else "This section is too thin to evaluate meaningfully."
                    ),
                    "suggestion": c["good_evidence"],
                    "confidence": 5,
                }
            )

        return {
            "summary": (
                f"[MOCK EVALUATION — no ANTHROPIC_API_KEY set] Automated placeholder "
                f"feedback for '{problem.title}'. Configure ANTHROPIC_API_KEY for real evaluation."
            ),
            "criteria": criteria,
            "strengths": ["Submission includes all required sections." ],
            "priority_improvements": ["Add real AI evaluation by setting ANTHROPIC_API_KEY."],
            "tradeoffs_identified": [],
        }

    @staticmethod
    def _closest_section(criterion_name: str) -> str:
        mapping = {
            "Requirement understanding": "requirements_understanding",
            "Class responsibilities": "classes_responsibilities",
            "Coupling & cohesion": "classes_responsibilities",
            "Encapsulation": "classes_responsibilities",
            "Interface / abstraction usage": "key_relationships",
            "Extensibility": "tradeoffs_assumptions",
            "Explanation quality": "tradeoffs_assumptions",
        }
        return mapping.get(criterion_name, "classes_responsibilities")
