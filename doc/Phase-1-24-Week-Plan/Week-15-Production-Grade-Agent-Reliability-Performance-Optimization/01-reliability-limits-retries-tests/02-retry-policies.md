# Retry Policies — Tenacity Backoff, Budgets, Circuit Breakers

**What you'll learn:** production retries with tenacity: exponential
backoff with jitter, retry-conditions (which failures deserve retries),
and the circuit breaker that stops hammering a dead dependency.

## 1. The tenacity policy

```python
from tenacity import (retry, stop_after_attempt, wait_random_exponential,
                      retry_if_exception_type, before_log)
import logging

logger = logging.getLogger("reliability")

@retry(
    stop=stop_after_attempt(4),
    wait=wait_random_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, RateLimitError)),
    before=before_log(logger, logging.WARNING),
    reraise=True,
)
def call_model_with_retry(messages: list) -> str:
    return raw_model_call(messages)
```

| Parameter | Meaning | Value rationale |
|---|---|---|
| `stop_after_attempt(4)` | 1 try + 3 retries | bounded by the RunBudget |
| `wait_random_exponential` | backoff with jitter | avoids thundering herd |
| `retry_if_exception_type(...)` | transient only | RateLimit retries; validation errors don't |
| `reraise=True` | final failure propagates | the user contract handles it |

The policy encodes the W10 distinction: *transient* failures retry
(rate limits, timeouts), *structural* failures don't (schema errors,
validation). The jitter matters at any concurrency — two agents retrying
without jitter collide forever.

## 2. Retries inside the budget (the two-layer rule)

```python
def budgeted_call(fn, *args, budget: RunBudget):
    for attempt in range(3):
        if budget.seconds_left() < 5:           # don't start what you can't finish
            raise BudgetExhausted("time")
        try:
            out = fn(*args)
            budget.tokens_used += out.tokens
            return out
        except TransientError:
            if attempt == 2:
                raise
            time.sleep(min(2 ** attempt, 8))
```

The rule: **the budget bounds retries, not just calls.** A tenacity
policy that ignores the RunBudget will happily spend 30 s retrying when
the run has 5 s left. The budgeted wrapper checks `seconds_left()`
*before each attempt* and counts tokens into the budget.

## 3. The circuit breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, cooldown_s: float = 60.0):
        self.failures = 0
        self.threshold = failure_threshold
        self.cooldown = cooldown_s
        self.opened_at: float | None = None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        if time.time() - self.opened_at > self.cooldown:
            self.opened_at = None               # half-open: try again
            return True
        return False

    def record(self, ok: bool):
        if ok:
            self.failures = 0
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = time.time()
```

| State | Meaning |
|---|---|
| closed | normal; failures counted |
| open | failing fast — calls refused without hitting the dependency |
| half-open | one probe after cooldown |

The breaker protects the *dependency* (an already-struggling API) and
the *budget* (failing fast instead of retrying for the full budget).
Per-dependency breakers: the model, the vector DB, the warehouse each
get one.

## 5. The retry decision table (what retries, what doesn't)

| Failure | Retry? | Why |
|---|---|---|
| 429 rate limit | yes, with backoff | transient by design |
| timeout | yes, once | may have been a blip |
| connection reset | yes | transient |
| schema/validation error | no | the input is the problem |
| 401/403 auth | no | retrying won't fix credentials |
| tool contract error | no | the hint teaches instead |

The decision table is the policy's content — tenacity's
`retry_if_exception_type` encodes it, and the table is its
documentation. The two-column rule: transient → retry with backoff;
everything else → fail fast into the user contract (file 03).

## Exercises

1. Implement the policy; fault-inject 3 transient failures; verify
   backoff timing (jitter visible) and eventual success.
2. Budget-layer drill: a RunBudget with 5 s left vs a retry policy with
   20 s of backoff; the budgeted wrapper must refuse to start the last
   attempt.
3. Breaker drill: fail the dependency 5×; the breaker opens; subsequent
   calls fail fast; after cooldown, one probe.
4. Table drill: for each §5 row, name the code path that implements the
   decision — the table is the policy, the code is its enforcement.