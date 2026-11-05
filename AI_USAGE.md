# AI_USAGE.md

This project was built with Claude as a pair-programming/design partner.
Below are the meaningful decisions where Claude proposed something and I
(the author) had to accept, reject, or modify it based on engineering
judgement — not just "AI wrote the code."

## 1. Strategy pattern for `Evaluator`, not an `if/else` branch

**Suggested:** an `Evaluator` abstract interface with `AIEvaluator` as
the concrete implementation, rather than a simple
`if evaluator_type == "ai": call_llm()` branch inside the service.

**Accepted, because:** the assignment's Change Test B ("can a second
evaluator be added without rewriting the main flow?") directly rewards
this. An `if/else` would have worked for a single evaluator but would
have needed to grow with every future evaluator, coupling orchestration
logic to implementation details. The interface costs one extra file for
a real, demonstrable payoff.

## 2. Structural completeness stays deterministic; only design-quality criteria go to the AI

**Suggested:** split the 8 rubric criteria so that "submission
completeness" is a plain Python check on the `Submission` model, run
*before* any AI call, and only the 7 genuinely subjective criteria
(coupling, abstraction, extensibility, etc.) are sent to the LLM.

**Accepted, because:** whether a required section is empty is
unambiguous and free to check — spending an LLM call (latency, cost, and
a chance of malformed output) to answer a question a `len()` check
already answers would be wasteful. This also means an incomplete
submission fails fast with a specific, actionable 400 response instead
of a vague AI complaint.

## 3. Diagram submission format — deferred, not built

**Suggested (by me, checked with Claude):** whether to add a minimal
diagram/Mermaid submission option alongside text, to show more breadth.

**Rejected, because:** Claude's cost/benefit breakdown (implementation
effort vs. evaluation difficulty vs. 2-day budget) showed diagram
support would consume a disproportionate share of the available time on
editor tooling alone, without adding evaluation depth — text already
captures the *reasoning* that's actually being graded. I deferred this
and documented the extension point (`Submission.content_type`) instead
of half-building it.

## 4. `BackgroundTasks` instead of a real task queue

**Suggested:** FastAPI's built-in `BackgroundTasks` for non-blocking
evaluation, instead of Celery/RabbitMQ.

**Accepted, because:** the assignment explicitly excludes
distributed-systems scope, and `BackgroundTasks` gives the same
observable behaviour (submit returns immediately, evaluation completes
async) at a fraction of the setup cost. I'd reconsider this only if the
project needed to survive a server restart mid-evaluation, which is out
of scope here.

## 5. A `MockEvaluator` fallback when no API key is set

**Suggested:** implement a second, real `Evaluator` (not a stub) that
returns deterministic placeholder feedback, and have the service
auto-select it whenever `ANTHROPIC_API_KEY` is unset.

**Accepted, and it paid off immediately:** this let the entire
submit -> evaluate -> feedback -> retry loop be tested end-to-end
without any external API calls. While testing this flow, it actually
surfaced a real bug — the autosave merge in `save_draft` was silently
overwriting previously-saved sections with empty strings whenever a
partial update omitted them, because the Pydantic schema defaulted
unset fields to `""` instead of `None`. That bug would have been much
harder to notice against a real (slower, non-deterministic) AI call.
Fixed by changing the schema defaults to `None` so the merge correctly
skips omitted fields.

## Still to evaluate once tested against a real API key

- Whether the `classification` field (issue / improvement / tradeoff /
  preference) actually produces more defensible feedback than a plain
  score once run against real, varied learner submissions — this can
  only be judged by reading real model output, not assumed in advance.
- Whether `temperature=0.2` is the right consistency/quality trade-off,
  or whether it needs tuning after seeing a handful of real evaluations.
