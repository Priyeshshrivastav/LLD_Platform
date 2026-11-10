# LLD Practice Platform

A small end-to-end practice tool for Low-Level Design: choose a problem
write a structured design, submit it, and get AI-generated, evidence-cited
feedback. Attempts persist so a learner can retry and track improvement.

See [`DESIGN.md`](./DESIGN.md) for the domain model, evaluation approach,
and the two extensibility "Change Tests." See [`AI_USAGE.md`](./AI_USAGE.md)
for how AI was used while building this and which of its suggestions were
accepted or rejected.

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite + Pydantic
- **Frontend:** React (Vite), plain CSS, `react-router-dom`
- **AI:** Anthropic API, called only from `AIEvaluator` — falls back
  automatically to a deterministic `MockEvaluator` when no API key is
  configured, so the full flow is testable without one.

## Running it

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optionally set ANTHROPIC_API_KEY for real AI evaluation
python -m app.seed.seed
uvicorn app.main:app --reload
```
Runs at `http://127.0.0.1:8000` (interactive docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL defaults to http://127.0.0.1:8000
npm run dev
```
Runs at `http://localhost:5173`.

### Tests

```bash
cd backend
pytest tests/ -v
```
12 tests covering domain rules, evaluator behaviour (including malformed
LLM output), API state guards, and the failed-evaluation-preserves-work
guarantee. All run against an isolated SQLite test DB with the mock
evaluator — no API key required.

## What's implemented

- 5 seeded LLD problems (Parking Lot, Elevator, Library, Rate Limiter,
  Movie Ticket Booking)
- Full learner journey: browse -> start attempt -> structured-text
  editor with autosave -> submit -> non-blocking AI evaluation ->
  structured feedback -> attempt history -> retry
- Deterministic completeness gate before any AI call
- `Evaluator` interface (Strategy pattern) with a real `AIEvaluator` and
  a `MockEvaluator` fallback — demonstrates the extension point rather
  than just claiming it exists
- Idempotent submit (409 on double-submit) and evaluation retry with a
  state guard (409 on retrying a non-failed evaluation)
- 12 backend tests

## Known limitations

- No auth — single implicit user, by design (out of scope for a 2-day
  LLD-focused assignment)
- Only structured-text submissions (see `DESIGN.md`'s Change Test A for
  how a diagram format would be added)
- Only one AI evaluator ships; `MockEvaluator` demonstrates but doesn't
  fully exercise the multi-evaluator extension point (see Change Test B)
- Evaluation quality depends on the underlying model's output; the
  schema and prompt constrain but don't guarantee perfectly calibrated
  scores — see `AI_USAGE.md` for what was actually observed while
  testing
- No production concerns addressed (rate limiting, auth, horizontal
  scaling) — explicitly out of scope per the assignment's boundary
