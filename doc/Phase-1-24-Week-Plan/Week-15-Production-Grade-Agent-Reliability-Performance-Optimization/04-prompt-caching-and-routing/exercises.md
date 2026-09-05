# Exercises — Prompt Caching & Model Routing

Expanded set with worked approaches. The deliverable: reordered prompts
with verified cache hits, the routing ladder implemented, and the
calibrated threshold table.

## 1. Prefix restructuring (from 01-prefix-structuring)

**Task:** reorder the grounding prompt to stable/variable; measure the
byte-identical prefix; run the audit on 20 logged prompts.

**Worked approach:** the reorder is often a move of one block (context
into the user message) — measure the prefix before/after, and let the
audit catch any leaking variable (timestamps and counters are the
usual suspects).

**Pass criterion:** 100% byte-identical prefix; the prefix length
recorded; the checklist (§3) all checked.

## 2. Cache verification (from 02-cache-verification)

**Task:** run the verification test (two identical calls, `cached_tokens`
≥80%); add `cached_tokens` + effective cost to the ledger; report the
savings on the eval set.

**Worked approach:** the verification test is the reorder's acceptance
gate — run after every prompt change. The ledger's savings row is the
reorder's value, measured.

**Pass criterion:** cache hits on the second call; the savings row in
the ledger; the minimum-length floor documented.

## 3. The routing ladder (from 03-model-routing)

**Task:** implement rungs 1–2; run the battery; measure cost and quality
per rung; the promotion decision (rules → classifier) written with data.

**Worked approach:** rung 1 is free and instant — it earns its keep on
the obvious cases first. The classifier only sees fall-throughs; its
accuracy on the borderline band is the promotion criterion.

**Pass criterion:** rungs 1–2 green on the battery; the promotion
decision cited with numbers.

## 4. Threshold calibration (from 04-threshold-calibration)

**Task:** run both models on the eval set; build the delta table; find
the weak-safe band; set the threshold; verify no regression on
weak-routed cases.

**Worked approach:** the band is *measured* (delta ≈ 0 cases) and
*characterized* (what makes those cases weak-safe) — the threshold is
the band's boundary, and the verification re-run is the proof.

**Pass criterion:** the calibration table committed; weak-routed cases
hold quality; the threshold in the router config.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Prefix reorder + audit 100% | audit results | 3 |
| Cache verified in billing | verification test | 3 |
| Routing ladder measured | rung table | 4 |
| Calibrated threshold, no regression | calibration table | 4 |
| Pin note (caching + routing) | pin note | 2 |

**Pass bar:** 14/16 to proceed to file 05 (production hardening). The
calibration (4-pointer) is the routing's honesty — thresholds without
measured bands are vibes with decimals.

## Pitfalls recap

- Variable content in the prefix — one timestamp kills the cache; the
  audit catches it before the bill.
- Weak-model answers on hard queries — the asymmetry principle: the
  uncertain case goes to strong.
- Savings assumed from the pricing table — the `cached_tokens` field is
  the verification; measure it.