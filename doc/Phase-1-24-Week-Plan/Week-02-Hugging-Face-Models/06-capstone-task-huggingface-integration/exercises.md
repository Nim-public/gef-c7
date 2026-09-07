# Exercises — Capstone Task: HF Integration

> Subfolder index: [README.md](README.md) · Parent: [../06-capstone-task-huggingface-integration.md](../06-capstone-task-huggingface-integration.md)

Labs that complete the W2-06 deliverable: task selection evidence, the pinned model, the mini-eval, and the integration seam.

---

## E1 — Selection evidence pack (files 01/02)

1. The matrix: 5 candidate tasks scored on the five criteria; winner + eliminations documented.
2. The protocol run: filter → shortlist 3 → widget tests → harness run → pin; every step's artifact saved.
3. The ladder walk: introduce one failure; document which rung of the fallback ladder resolves it (file 02 §4).

**Worked approach:** the elimination reasons are the review artifact — one sentence per loser, written at selection time, not reconstructed later.

## E2 — The mini-eval build (file 03)

1. 20 cases across the four kinds; rubric written before any model runs.
2. Three models through the eval; per-kind pass table; the winner selected by numbers.
3. Regression integration: the eval as pytest (file 03 §4); a deliberate model swap caught by the suite.

**Worked approach:** exercise 3 makes the eval a *gate* — the W15-02 hosted dataset or a local pytest run both qualify; what matters is that it runs without a human remembering.

## E3 — The seam certification (file 04)

1. Contract-first implementation: dataclass + docstring written first; code fills it.
2. Edge-case conformance: empty, 10k-char, non-English, emoji-only — each matches the documented behavior.
3. Provenance test: same input → same provenance; revision bump → provenance changes (and nothing else).
4. Monitoring conformance: the JSONL schema matches W10-04; a simulated week loads into the W16-01 eval format.

**Worked approach:** exercise 3 is the auditability proof — provenance is what turns "the model said X" into "model M rev R said X on input H at time T", which is what production demands.

## E4 — The full deliverable review (W2-06 §6's rubric, self-scored)

| Criterion | Score 0-5 | Evidence |
|---|---|---|
| Task selection + matrix |  |  |
| Model pin + shortlist documentation |  |  |
| Mini-eval rigor (kinds, rubric-first, n) |  |  |
| Integration seam (contract, provenance, monitoring) |  |  |
| Failure analysis (taxonomy + actions) |  |  |
| Production hooks (logs, versions, degradation path) |  |  |

Target: ≥4 average. Anything below 3 gets a named fix before the mentor session.

## Self-assessment

- Can you state your task, model, revision, eval version, and pass rate — from memory?
- Can you name the failure class that dominates your mini-eval, and the action it triggered?
- Can a teammate integrate your component using only the contract docstring and README?
