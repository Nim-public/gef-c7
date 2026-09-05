# Exercises — Agentic RAG

Expanded set with worked approaches. The deliverable: the measured
fixed-vs-agentic decision, the three-power agent routed correctly, and
the blended-cost memo.

## 1. The both-modes run (from 01-fixed-vs-agentic)

**Task:** run the eval set through (a) your W9 fixed pipeline, (b) the
agentic agent (`search_knowledge=True`); produce the class × mode table
(R@5, tokens, latency).

**Worked approach:** the same corpus version, same queries, same header —
the comparison protocol from W11 file 06-02, applied to retrieval modes.
The skip instrumentation runs in both modes.

**Pass criterion:** the table committed; the class-split pattern visible
(agentic wins the tail, fixed wins the rigid classes).

## 2. Three-power routing (from 02-three-power-agent)

**Task:** build the three-power agent; run the 5-case battery × 3; verify
tool usage AND `source` labels; then the priority drill (corpus-vs-web
overlap query).

**Worked approach:** the `source` field is the structural check — the
harness asserts it matches the tools that fired. The priority drill is
the corpus-first rule under pressure.

**Pass criterion:** 5/5 routes + labels; the priority drill passes
(corpus preferred, labeled).

## 3. Route accuracy head-to-head (from 03-route-accuracy)

**Task:** run the 25-query head-to-head (regex vs model vs hybrid);
produce the class table with Δ; fix the modal miss type.

**Worked approach:** the miss taxonomy drives the fix — under-search is
the floor, over-search is the stop rule, wrong power is priority wording.
One fix per iteration, then remeasure.

**Pass criterion:** table committed; hybrid row computed; the modal miss
fixed with a before/after number.

## 4. The blended memo (from 04-cost-quality-trade)

**Task:** produce the §4 decision table from your runs; add the blended
row over your class distribution; add the revisit trigger.

**Worked approach:** the memo is the week's *decision* artifact — per
class, mode, and cause, with the blend computed from your distribution.
The trigger names the metric (skip-rate, recall) and its threshold.

**Pass criterion:** memo row in the boundary memo; at least one class
kept fixed with cited recall numbers.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Both-modes table with header | reports/rag-modes.md | 4 |
| Three-power battery + labels | route table | 3 |
| Head-to-head + hybrid row | accuracy table | 4 |
| Blended memo with trigger | boundary memo | 3 |
| Skip instrumentation in both modes | call-count logs | 2 |

**Pass bar:** 13/16 to proceed to file 06 (CrewAI). The head-to-head
(4-pointer) is the week's measurement crown — regex vs model vs hybrid,
on your data.

## Pitfalls recap

- Mode comparisons across corpus versions — the header discipline is not
  optional.
- Routing fixes without remeasure — the A/B loop or the fix is a guess.
- Blended numbers without the class split — the average is where the
  decision hides.