# RunBudget — Turns, Tokens, Time, and Spend Aborts

**What you'll learn:** the RunBudget: four abort rails (turns, tokens,
wall-clock time, dollars) checked *inside* the loop, with honest
degradation when any rail trips.

## 1. The budget object

```python
from dataclasses import dataclass, field
import time

@dataclass
class RunBudget:
    max_turns: int = 6
    max_tokens: int = 50_000
    max_seconds: float = 120.0
    max_spend_usd: float = 0.50
    start: float = field(default_factory=time.perf_counter)
    tokens_used: int = 0
    spend_usd: float = 0.0

    def turns_left(self, turns: int) -> int: return self.max_turns - turns
    def tokens_left(self) -> int: return self.max_tokens - self.tokens_used
    def seconds_left(self) -> float: return self.max_seconds - (time.perf_counter() - self.start)
    def spend_left(self) -> float: return self.max_spend_usd - self.spend_usd

    def breached(self, turns: int) -> str | None:
        if turns >= self.max_turns: return "turns"
        if self.tokens_used >= self.max_tokens: return "tokens"
        if self.seconds_left() <= 0: return "time"
        if self.spend_usd >= self.max_spend_usd: return "spend"
        return None
```

| Rail | Checked | Trips when |
|---|---|---|
| turns | per loop iteration | model calls ≥ max |
| tokens | per model response | cumulative usage ≥ max |
| time | per loop iteration | wall clock exceeded |
| spend | per model response | dollars exceeded |

The W10 episode budget grew a family: four rails, checked *inside* the
loop — because a turn cap alone lets one giant model response blow every
other limit.

## 2. The loop integration (abort with honest degradation)

```python
def run_with_budget(agent, query: str, budget: RunBudget) -> dict:
    turns = 0
    while True:
        if (rail := budget.breached(turns)) :
            return {"answer": BUDGET_MESSAGES[rail], "degraded": True,
                    "rail": rail, "partial": collect_partial(turns)}
        resp = agent.step(query)
        budget.tokens_used += resp.tokens
        budget.spend_usd += resp.cost_usd
        turns += 1
        if resp.final:
            return {"answer": resp.content, "degraded": False}
```

| Rail tripped | User message |
|---|---|
| turns | "This task needed more steps than allowed — here is what I found so far." |
| tokens | "This task was too large for one run — try narrowing it." |
| time | "This took too long — partial results attached." |
| spend | "Cost limit reached — showing the cheapest complete answer." |

The `BUDGET_MESSAGES` map is the user-contract layer (file 03) — the
rails abort *honestly*, with partial results where they exist.

## 3. The budget ledger (feeds the harness)

```python
def budget_row(budget: RunBudget, outcome: str) -> dict:
    return {"turns": turns, "tokens": budget.tokens_used,
            "seconds": round(time.perf_counter() - budget.start, 2),
            "spend_usd": budget.spend_usd,
            "rail": budget.breached(turns), "outcome": outcome}
```

Every run's row lands in the trajectory store — the budget table (file
04 of the test pyramid) reads it. The rails' trip rates are the
production reliability metrics: a spend rail tripping 5% of the time is
a cost-model alarm.

## 5. The budget pin (the limits as configuration)

```python
# data/manifests/budgets.json — committed
{
  "version": 2,
  "defaults": {"max_turns": 6, "max_tokens": 50000,
                "max_seconds": 120, "max_spend_usd": 0.50},
  "per_component": {
    "analytics": {"max_tokens": 60000, "max_spend_usd": 0.80},
    "voice":     {"max_seconds": 8}
  }
}
```

| Rule | Why |
|---|---|
| budgets are committed config | limits are policy, not code |
| per-component overrides | voice's time budget ≠ analytics' token budget |
| version stamped in trajectories | limit changes are attributable |

The budget pin is the settings-version discipline applied to limits —
the same artifact shape as `preproc-settings.json` (W7) and the fusion
policies (W12). A limit change without a version bump is an
unattributable behavior change.

## Exercises

1. Implement `RunBudget`; stress each rail (tiny limits); all four trip
   with the right message and `degraded=True`.
2. Partial-results drill: trip the turn rail mid-retrieval; the partial
   findings render in the degraded answer.
3. Ledger drill: 20 runs under budget; the trip-rate table; no rail
   above 5% on healthy tasks.
4. Pin drill: write `budgets.json`; move the limits from code constants;
   bump the version once and verify the trajectories split cleanly.