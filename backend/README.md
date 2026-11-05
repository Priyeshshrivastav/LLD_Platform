# LLD Practice Platform — Backend (Day 1)

FastAPI + SQLAlchemy + SQLite backend implementing the full
Problem → Attempt → Submission → Evaluation loop from the Day 1 plan.

## Setup

```bash
cd backend
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY for real AI evaluation
python -m app.seed.seed
uvicorn app.main:app --reload
```

Server runs at `http://127.0.0.1:8000`. Interactive API docs at
`http://127.0.0.1:8000/docs`.

## Without an API key

If `ANTHROPIC_API_KEY` is left empty in `.env`, the service automatically
uses `MockEvaluator` instead of `AIEvaluator` — the entire submit →
evaluate → feedback → retry loop works end-to-end with zero external
calls, so you (or a reviewer) can smoke-test the whole flow before
wiring up a real key. Set the key and everything switches to real AI
evaluation with no code changes — that's the point of the `Evaluator`
interface.

## Quick manual test

```bash
curl http://127.0.0.1:8000/problems
curl -X POST http://127.0.0.1:8000/problems/1/attempts
curl -X PUT http://127.0.0.1:8000/attempts/1/submission \
  -H "Content-Type: application/json" \
  -d '{"requirements_understanding": "...", "classes_responsibilities": "...", "key_relationships": "...", "tradeoffs_assumptions": "..."}'
curl -X POST http://127.0.0.1:8000/attempts/1/submit
curl http://127.0.0.1:8000/evaluations/1
```

## What's implemented (Day 1 scope)

- All 8 endpoints from the API design (problems, attempts, submissions,
  evaluations, retry, history)
- Deterministic completeness gate before any AI call runs
- `Evaluator` interface (Strategy pattern) with `AIEvaluator` +
  `MockEvaluator` — swappable with zero changes to `EvaluationService`
  or the API layer
- Non-blocking async evaluation via FastAPI `BackgroundTasks`
- State-guarded idempotency: double-submit → 409, retry-when-not-failed
  → 409
- Failed evaluations never touch or lose the learner's submission

## What's NOT in Day 1 (frontend / Day 2)

React UI, tests, DESIGN.md/AI_USAGE.md/RESEARCH.md — see the main
2-day plan artifact for the full breakdown.
