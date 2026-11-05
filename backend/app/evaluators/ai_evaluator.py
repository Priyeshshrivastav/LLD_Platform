import json
import os

import httpx
from pydantic import ValidationError as PydanticValidationError

from app.evaluators.base import Evaluator, EvaluationError
from app.evaluators.rubric import RUBRIC_CRITERIA
from app.schemas.evaluation import EvaluationResult

SYSTEM_PROMPT = """You are evaluating a Low-Level Design (LLD) submission.
There is no single correct design for these problems — evaluate whether
the learner's choices are reasonable and well-justified given the stated
requirements, not whether they match a reference solution.

For each rubric criterion, cite specific evidence from the submission
text (evidence must be grounded in what the learner actually wrote).
Classify each criterion's finding as exactly one of:
- "issue": violates a stated requirement or a sound design principle
- "improvement": would help but is not required by the problem
- "tradeoff": a reasonable choice with a stated, acceptable downside
- "preference": stylistic, not substantive

Do not penalize a design merely for being different from a common
solution. Only classify something as an "issue" if you can point to a
specific requirement or principle it violates.

Respond with ONLY a single valid JSON object matching the schema you are
given. Do not include any text, explanation, or markdown code fences
outside the JSON object."""

OUTPUT_SCHEMA_HINT = """{
  "summary": "string",
  "criteria": [
    {
      "name": "string (must exactly match one of the provided rubric criterion names)",
      "score": 0,
      "evidence": "string",
      "classification": "issue | improvement | tradeoff | preference",
      "concern": "string",
      "suggestion": "string",
      "confidence": 0
    }
  ],
  "strengths": ["string"],
  "priority_improvements": ["string"],
  "tradeoffs_identified": ["string"]
}
score and confidence are integers from 0 to 10."""


class AIEvaluator(Evaluator):
    name = "ai_v1"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    def evaluate(self, problem, submission_content: dict) -> dict:
        if not self.api_key:
            raise EvaluationError("GEMINI_API_KEY is not configured")

        prompt = self._build_prompt(problem, submission_content)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

        try:
            response = httpx.post(
                url,
                headers={"content-type": "application/json"},
                json={
                    "contents": [
                        {
                            "parts": [{"text": full_prompt}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 3000,
                    },
                },
                timeout=60.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EvaluationError(f"LLM request failed: {exc}") from exc

        raw_text = self._extract_text(response.json())
        raw_text = self._strip_code_fences(raw_text)

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"Model did not return valid JSON: {exc}") from exc

        try:
            validated = EvaluationResult.model_validate(parsed)
        except PydanticValidationError as exc:
            raise EvaluationError(f"Model output failed schema validation: {exc}") from exc

        return validated.model_dump()

    def _build_prompt(self, problem, submission_content: dict) -> str:
        rubric_text = "\n".join(
            f"- {c['name']}: {c['description']}\n"
            f"  Good evidence looks like: {c['good_evidence']}\n"
            f"  Weak evidence looks like: {c['weak_evidence']}"
            for c in RUBRIC_CRITERIA
        )
        sections_text = "\n\n".join(
            f"### {key.replace('_', ' ').title()}\n{value}"
            for key, value in submission_content.items()
        )
        return f"""PROBLEM: {problem.title}

Requirements:
{problem.requirements}

Constraints:
{problem.constraints}

RUBRIC CRITERIA:
{rubric_text}

LEARNER SUBMISSION:
{sections_text}

OUTPUT SCHEMA (respond with ONLY this JSON object, one entry in
"criteria" per rubric criterion above, using the exact criterion names):
{OUTPUT_SCHEMA_HINT}"""

    @staticmethod
    def _extract_text(response_json: dict) -> str:
        """Extract text from Gemini API response format."""
        try:
            candidates = response_json.get("candidates", [])
            if not candidates:
                raise EvaluationError("LLM returned no candidates")
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            if not text.strip():
                raise EvaluationError("LLM returned no text content")
            return text.strip()
        except (KeyError, IndexError) as exc:
            raise EvaluationError(f"Unexpected LLM response format: {exc}") from exc

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:] if lines[0].startswith("```") else lines
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
        return text.strip()
