# Exercises — Tools, Handoffs & Guardrails

Expanded set with worked approaches. The deliverable: SDK tools with your
error contracts, a two-specialist router, both guardrail types, and the
battery in CI.

## 1. Decorator port (from 01-function-tool)

**Task:** port the three RAG tools to `@function_tool` with hint-
preserving `failure_error_function`; diff generated schemas vs the W10
hand-written ones; wire one `is_enabled` gate (quota).

**Worked approach:** the schema diff is the acceptance gate — any drift
means the docstring lost contract content in translation. The quota gate
proves context-conditional surfaces work.

**Pass criterion:** 3/3 schemas equivalent; hints intact through
`failure_error_function`; the disabled tool vanishes from the model's
view.

## 2. Handoff router (from 02-handoffs)

**Task:** build router → two specialists (charts, exact-terms); run the
three W9 routing tasks; assert `last_agent` per task; A/B one handoff
description after a deliberate misroute.

**Worked approach:** the A/B loop (misroute → rewrite description →
remeasure) is W10's hint discipline applied to a new surface — handoff
descriptions are now your routing table, and they rot the same way.

**Pass criterion:** 3/3 routes correct via `last_agent`; the A/B table
shows the fix; description version-stamped.

## 3. Guardrail pair (from 03, 04)

**Task:** implement the injection input guardrail (judge-agent) and the
citation output guardrail; run: (a) an injection query → blocked pre-
answer, (b) a phantom-citation answer → tripped, retried once, then
degraded.

**Worked approach:** the retry-once-then-degrade loop is the W10 ladder
in SDK clothing; budget it explicitly. The judge-agent uses a fast model
— its cost lands in the ledger (one ~200-tok call per run).

**Pass criterion:** both tripwires fire on their cases; the retry path
produces a clean answer on the second try; costs in the ledger.

## 4. Battery in CI (from 05-battery-as-pytest)

**Task:** port the W9 battery verbatim; wire markers (`real_llm` nightly);
add the provenance column; verify the fast suite runs <10 s.

**Worked approach:** provenance is curation — a case without a reason is
deleted in review, keeping the battery sharp. The nightly report files
pass rates per case over time.

**Pass criterion:** push CI green and fast; nightly report exists; every
case has provenance.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Decorator port: schemas + hints + gate | diff tests | 4 |
| Router with handoffs, `last_agent` asserted | routing tests | 3 |
| Both guardrails fire + retry ladder | guardrail tests | 4 |
| Battery in CI with provenance | CI + provenance table | 3 |
| Error fidelity at SDK layer (W10 parity) | fidelity tests | 2 |

**Pass bar:** 12/16 to proceed to file 03 (multi-agent orchestration).
The guardrail pair (4-pointer) is the week's safety deliverable — blocking
at generation time, not after.

## 6. The contract-parity sweep

**Task:** for each W10 contract (registry validation, error hints, gate
policy, observation format), verify its SDK-era equivalent preserves the
*content*: same hint text through `failure_error_function`, same gate
decisions through `needs_approval`, same observation shape from
formatters.

**Worked approach:** the sweep is a 4-row table (W10 contract → SDK
mechanism → parity test name). Any row without a test is a ported
contract that lost its enforcement — the exact failure the sweep exists
to catch.

**Pass criterion:** 4/4 rows with parity tests green; the table linked
from the port's verdict memo.

## Pitfalls recap

- Docstrings that lost contract content in the port — the schema diff
  test exists to catch exactly that.
- Handoff descriptions written once and never A/B'd — they are the
  routing table; they rot like hints.
- Guardrails that edit instead of trip — trip, retry with context, then
  degrade; edits hide model failures.
