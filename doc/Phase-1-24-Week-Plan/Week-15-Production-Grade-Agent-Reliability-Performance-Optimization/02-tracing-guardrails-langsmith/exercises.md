# Exercises — Tracing, Guardrails & LangSmith

Expanded set with worked approaches. The deliverable: hosted tracing
with a send policy, the eval set mirrored and reconciled, the
moderation/PII layers battery-tested, and the scrubber at the export
boundary.

## 1. Hosted tracing (from 01-langsmith-setup)

**Task:** enable tracing on the dev project; run 5 eval tasks; verify
full trees; complete the hosted↔store mapping table.

**Worked approach:** the mapping table is the merge's hosted edition —
every LangSmith field paired with its W10 store counterpart. Unmapped
fields are either noise (do not send) or gaps (add to the store).

**Pass criterion:** 5 runs hosted and mapped; the project split verified
(dev ≠ prod views).

## 2. Hosted evaluations (from 02-datasets-evaluations)

**Task:** upload the eval set as a dataset; run a hosted evaluation;
reconcile against the local harness; the drift drill (edit one case).

**Worked approach:** the reconciliation is the mirror rule's proof —
hosted scores must match local scores within tolerance, and the drift
drill shows what divergence looks like before it matters.

**Pass criterion:** scores reconcile within tolerance; the drift drill
flags the edited case.

## 3. Guardrail layers (from 03-platform-guardrails)

**Task:** wire moderation (layer 1) and the PII detector (layer 2); run
the layer-attribution battery; measure added latency per layer.

**Worked approach:** the attribution table is the layering's proof —
each case names its firing layer. The latency table prices the layers;
gate-worthy content only (the triage rule).

**Pass criterion:** 4/4 battery cases with correct layer attribution;
latency costs in the ledger.

## 4. Trace hygiene (from 04-trace-hygiene)

**Task:** wire the scrubber at the export boundary; the retention
rotation; the sampling policy (prod mode); all three drills.

**Worked approach:** the hygiene drills are the hygiene rules as tests —
the PII plant, the rotation, the sampling measurement. The local trace
stays full-fidelity; only the export is clean.

**Pass criterion:** exported traces clean, local detailed; rotation
works; ~20% sampling with 100% failure coverage.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Hosted tracing mapped to the store | mapping table | 3 |
| Eval set mirrored + reconciled | reconciliation test | 4 |
| Guardrail layers attributed | battery + latency table | 4 |
| Hygiene: scrub, retention, sampling | three drills | 4 |
| Send-policy page | reports/send-policy.md | 2 |

**Pass bar:** 14/18 to proceed to file 03 (inference optimization). The
hygiene drills (4-pointer) are the privacy deliverable — what leaves
your machine is a policy, not a default.

## Pitfalls recap

- Tracing left on with default settings — full corpus content leaves;
  the send-policy is not optional.
- Two eval sets growing independently — the mirror rule and the
  reconciliation job are the guard.
- Sampling that drops failures — failures are the signal; the outcome-
  based rule overrides the rate.