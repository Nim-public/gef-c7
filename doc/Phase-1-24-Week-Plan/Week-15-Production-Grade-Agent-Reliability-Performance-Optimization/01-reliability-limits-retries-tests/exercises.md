# Exercises — Reliability: Limits, Retries, Tests

Expanded set with worked approaches. The deliverable: the RunBudget with
all four rails, tenacity policies inside the budget, the user-contract
map battery-tested, and the pyramid organized.

## 1. The RunBudget (from 01-run-budget)

**Task:** implement the four-rail budget; stress each rail with tiny
limits; verify the honest messages, `degraded=True`, and the ledger row.

**Worked approach:** each rail gets a dedicated stress fixture (tiny
turn cap, tiny token cap, tiny time, tiny spend) — four drills, four
messages, four ledger rows with the rail named.

**Pass criterion:** 4/4 rails trip correctly; partial results render;
ledger rows complete.

## 2. Retries inside the budget (from 02-retry-policies)

**Task:** implement the tenacity policy + the budgeted wrapper; fault-
inject transient failures; verify backoff timing, jitter, and the
budget-refusal on late attempts.

**Worked approach:** the two-layer rule is the exercise: tenacity
retries *within* the budget, and the budget refuses attempts it cannot
afford. The fault-injection harness (canned failures) is deterministic.

**Pass criterion:** backoff visible in logs; the budget-refusal fires
before the last attempt; success on recovery within budget.

## 3. The breaker (from 02)

**Task:** implement the per-dependency breaker; fail one dependency 5×;
verify open-state fast-fails, half-open probes once, and recovery
resets.

**Worked approach:** the breaker protects the dependency and the budget
— the drill asserts both (fast failure latency, and no budget burn while
open).

**Pass criterion:** open state fails fast (<10 ms); half-open probes
once; recovery resets the count.

## 4. User contracts (from 03-user-contracts)

**Task:** implement the handler map; run the contract battery; the leak
drill (path + key in an exception); the reference-id drill.

**Worked approach:** the leak drill is the map's security test — an
exception containing internals must produce a clean user message. The
reference drill proves the support workflow.

**Pass criterion:** 4/4 contract cases; zero leaks; the reference id
resolves to the trace.

## 5. The pyramid (from 04-test-pyramid)

**Task:** organize existing suites into the four tiers; verify runtimes;
record one bug per tier caught by its tier; wire the CI slots.

**Worked approach:** the pyramid's acceptance is the four-bug drill —
each tier catches its own class of bug, proving the tiers are not
redundant.

**Pass criterion:** tier runtimes within budget; 4/4 tier-specific bugs
caught; CI slots wired.

## 6. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| RunBudget: 4 rails + ledger | stress tests | 4 |
| Retries: policy + budget layer + breaker | fault-injection tests | 4 |
| User contracts: battery + leak drill | contract tests | 4 |
| Pyramid: 4 tiers organized + bug drill | CI config + drill | 4 |

**Pass bar:** 14/16 to proceed to file 02 (tracing). The budget
(4-pointer) is the reliability week's foundation — every rail is a
production promise.

## 7. The reliability pin note

**Task:** extend `reports/sdk-versions.md` with the reliability stack:
tenacity version, budget config version, breaker thresholds, and the
pyramid's CI slots — one block.

**Worked approach:** the reliability layer is policy-heavy — the pin
note records which policy versions the drills verified.

**Pass criterion:** note committed; the drill commands green as
recorded.

## Pitfalls recap

- A turn cap as the only budget — one giant model response blows tokens,
  time, and spend; all four rails check.
- Retries outside the budget — the budget bounds retries, not just
  calls.
- User messages containing internals — the leak drill is in CI; the map
  is the wall.