# 01 — Reliability: Limits, Retries, Error Handling, Tests

> Week 15 index: [README.md](README.md)

**Session 1 topics:** *Can add limits, retries, and robust error handling to agents. Can write unit/integration tests for agent workflows.*

---

## What you'll learn

- The four limit classes every production agent needs (turns, tokens, time, spend)
- Retry policies: what's retryable, backoff math, and retry budgets
- Error handling as *user-visible* contracts, not stack traces
- Unit vs integration tests for agent workflows — and what to stub

## 1. The four limits (all four, always)

| Limit | Guards against | Implementation |
|---|---|---|
| **Turns** | infinite loops (W10-01) | `max_turns` / loop counter → typed exception |
| **Tokens** | context/cost explosion (W10-05) | per-run budget counter → abort with partial state |
| **Wall time** | hung tools/models | per-call + per-run timeouts (W10-02) |
| **Spend** | bill shock (W9-03's P3) | cumulative $ counter from `usage` → circuit break |

```python
class BudgetExceeded(Exception): ...
class MaxTurnsExceeded(Exception): ...

class RunBudget:
    def __init__(self, max_turns=10, max_tokens=60000, max_seconds=120, max_usd=0.50):
        self.__dict__.update(max_turns=max_turns, max_tokens=max_tokens,
                             max_seconds=max_seconds, max_usd=max_usd)
        self.turns = self.tokens = 0
        self.t0 = time.monotonic()
        self.usd = 0.0

    def check_step(self, usage=None):
        self.turns += 1
        if usage: self.tokens += usage.total_tokens; self.usd += price(usage)
        if self.turns > self.max_turns:   raise MaxTurnsExceeded()
        if self.tokens > self.max_tokens: raise BudgetExceeded("tokens")
        if self.usd > self.max_usd:       raise BudgetExceeded("spend")
        if time.monotonic() - self.t0 > self.max_seconds: raise BudgetExceeded("time")
```

The caller maps exceptions to *user outcomes*: partial answer + "stopped early" beats a 500 error.

## 2. Retries: what's retryable and how

| Error class | Retryable? | Policy |
|---|---|---|
| 429 rate limit | yes | exponential backoff + jitter, respect `Retry-After` |
| 5xx / timeouts | yes | backoff, ≤2–3 attempts |
| 400 validation | **no** | fix the request (W6-03 repair loop instead) |
| guardrail tripwire | **no** | this is a *decision*, not a failure |
| tool exception | case-by-case | network yes; logic no — feed back as observation (W10-05) |

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

@retry(retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
       stop=stop_after_attempt(3),
       wait=wait_exponential_jitter(initial=1, max=30))
def call_llm(messages, **kw):
    return client.chat.completions.create(model=MODEL, messages=messages, **kw)
```

**Retry budget** discipline: retries multiply under load (a 429 storm with 3 retries × 10 parallel users = a self-DDoS). Bound total retry attempts *per run* and circuit-break a failing dependency after N consecutive failures (skip the call, use the fallback — W14-01's `with_fallbacks`).

## 3. Error handling as user contracts

```python
HANDLERS = {
    MaxTurnsExceeded:  "This task needed more steps than allowed. Partial findings: {partial}",
    BudgetExceeded:    "This task exceeded its resource budget. Nothing was charged beyond the cap.",
    ToolTimeout:       "A data source didn't respond. Try again or narrow the question.",
    TripwireTriggered: CANNED_REFUSAL,     # W11-02 — never expose internals
}
```

Rules: every exception has a handler; users see *outcomes and next steps*, never traces; every handler invocation is logged (W10-04's JSONL — the incident feed); partial results are returned when the budget cut mid-run (the state is checkpointed in LangGraph — file 13-06).

## 4. Tests for agent workflows

| Level | Tests | LLM? | Speed |
|---|---|---|---|
| **Unit** | tool validators, prompt rendering, budget checks, parsers, guardrail classification with *stubbed* judge | no | ms |
| **Contract** | real LLM, structured-output schemas, citation format | yes | seconds |
| **Integration** | full trajectory on golden cases (W10-04) | yes | minutes |
| **Soak/load** | concurrency, rate-limit behavior | yes | scheduled |

```python
def test_budget_aborts(run_budget):
    with pytest.raises(MaxTurnsExceeded):
        run_agent("endless task", budget=RunBudget(max_turns=2))

def test_retry_on_429(monkeypatch):
    calls = {"n": 0}
    def flaky(*a, **k):
        calls["n"] += 1
        if calls["n"] < 3: raise RateLimitError(...)
        return ok_response
    monkeypatch.setattr(module, "call_llm", flaky)
    assert run_agent("q").ok and calls["n"] == 3
```

Stub the LLM for unit tests (record/replay fixtures — `vcr`-style or saved responses); the W3-02 battery + W10-04 golden trajectories + W11-05 trace assertions compose into the full suite. **Pin model, temperature, and prompt versions** or the suite is noise (W5-05).

## Exercises

1. Add `RunBudget` to your W11/W14 agent; force each of the four aborts (tiny budgets) and verify each user-facing message.
2. Retry drill: wrap the LLM call with `tenacity`; simulate 429/5xx/400 — verify only the retryable ones retry, and the retry budget holds.
3. Unit-test pyramid: convert 5 of your W14 pytest cases to stubbed-LLM unit tests; measure suite time before/after.
4. Partial-result drill: abort mid-trajectory on budget; return the best-so-far state (LangGraph checkpoint or scratchpad) as the user answer.
5. Load smoke: 20 concurrent requests against your agent (threads); find the first limiter to break — your tool rate, provider rate, or the loop's memory.

## Pitfalls

- **Retries without budgets** — the retry storm is worse than the original error
- **Silent exception swallowing** — "it returned something" hiding a failed tool result; errors must be *structured* observations or user messages
- **Testing only the happy path** — 429s, timeouts, and guardrails are the production surface (this file's battery)
- **Budgets set once, never revisited** — p95 drift (W14-06 baseline) invalidates static limits; review with the metrics
- **Unit tests that call real LLMs** — slow, flaky, expensive; stub at the client boundary

## Resources

- [tenacity docs](https://tenacity.readthedocs.io/) — retry/backoff patterns
- OpenAI docs, *Rate limits & error handling* — the retryable classes, `Retry-After`
- W10-04 (instrumentation), W11-05 (trace assertions), W13-06 (checkpoints for partial results) — composed here
- pytest [monkeypatch/fixtures](https://docs.pytest.org/en/stable/) — the stubbing toolkit
