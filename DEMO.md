# Demo Script (5–7 min)

Pre-demo setup: backend running with `ANTHROPIC_API_KEY` set (for real
AI feedback), seeded, frontend running, and **one evaluation already
completed beforehand** as a fallback in case the live LLM call is slow.

1. **Problem selection (30s)** — Land on `/`, point out the 5 problems
   and difficulty spread (Parking Lot through Movie Ticket Booking).
2. **Problem requirements (30s)** — Click into "Parking Lot System,"
   show requirements/constraints — mention this is what grounds
   evaluation (the AI is told these, not just the submission).
3. **Creating an attempt (20s)** — Click "Start New Attempt," land in
   the editor.
4. **Submitting a solution (60s)** — Walk through the four sections
   using a pre-written, solid submission (don't type live). Point out
   the autosave indicator.
5. **Evaluation (30s)** — Click submit, show the `EVALUATING` state
   with the spinner — mention it's non-blocking (the request returned
   immediately; the LLM call runs in the background).
6. **Explainable feedback (90s)** — Once complete, walk through 2–3
   criteria cards: point at the evidence quote, the concern, the
   suggestion, and specifically call out one criterion classified as
   `tradeoff` or `preference` (not `issue`) to show the design isn't
   penalized just for being different from some reference solution.
7. **Previous attempt / history (30s)** — Navigate to "History," show
   more than one attempt across problems.
8. **Retry / improvement (30s)** — From the feedback page, click "Try
   Again," show a second attempt gets created on the same problem and
   appears in history.
9. **Brief architecture explanation (45s)** — One sentence per layer:
   React -> FastAPI routers -> `EvaluationService` -> `Evaluator`
   interface -> SQLite -> Anthropic API.
10. **Extensibility example (45s)** — State both Change Tests out loud
    and answer them directly: "If I added diagram submissions, only
    `Submission.content_type` and a new editor page change —
    `Evaluator` and `Attempt` are untouched. If I added a second
    evaluator, I implement `Evaluator` once more — `MockEvaluator`
    already proves this works, since it's a second real implementation
    running today with zero changes to `EvaluationService`."

## Decisions to verbally highlight

- Structured **text over code/diagram** submissions, and why (Phase 4
  reasoning: evaluation tractability + reasoning-capture over
  implementation cost).
- The **deterministic completeness gate** running before any AI call.
- **`BackgroundTasks` instead of a queue** — non-blocking without
  distributed-systems overhead.
- The **`classification` field** (issue/improvement/tradeoff/preference)
  as the concrete mechanism for handling multiple valid LLD solutions.
- One thing deliberately **not** built and why: no generic
  `Repository<T>`, no diagram support yet, no full State-pattern class
  hierarchy for a 5-state linear lifecycle.
