# Exercises — Practice: Cross-Modal Encoding Lab

Stretch tasks and the self-review rubric. Every lab writes a committed
report; the rubric grades the reports, not the screenshots.

## 1. Geometry lab hardening (Experiment A stretch)

**Task:** add a bootstrap confidence interval to each geometry probe:
resample the 50 embeddings 100× (with replacement), recompute probes,
report the 95% CI — the difference between "0.61 vs 0.55" and "0.61 ±0.03
vs 0.55 ±0.04".

**Worked approach:** `rng.choice(n, n, replace=True)` per bootstrap; the CI
tells you whether the two encoders' probes are *distinguishable* at n=50 —
usually they are not, which is itself the finding that prevents overfit
decoder choices to noise.

**Pass criterion:** CIs reported; any decision resting on a within-CI delta
is flagged as provisional.

## 2. Matrix diagnostics as a test (Experiment B stretch)

**Task:** promote the matrix diagnostics to a test: near-duplicate captions
and diagonal margin below a threshold must fail the suite — the eval
harness refusing to grade a broken benchmark.

**Worked approach:** thresholds from *your* data's healthy range (run once
on a known-good corpus, use ±3σ); the test runs on every corpus change and
fails loudly before a meaningless R@1 ever reaches a report.

**Pass criterion:** the test catches an injected duplicate and an injected
mis-pairing.

## 3. Ablation with the real sidecar plan (Experiment D stretch)

**Task:** replace the stand-in concat with your actual planned fusion (rank
fusion over two indexes); rerun the 4-cell ablation; compare conclusions
with the stand-in's.

**Worked approach:** rank fusion changes the *scale problem* (fusion file
03) — expect the OCR-sidecar delta to shrink if your text index was
already strong. The comparison table (stand-in vs real fusion) is the
honest version of "fusion choice matters".

**Pass criterion:** both tables committed; the conclusion line names which
delta survived the fusion swap.

## 4. Decision memo stress test (Experiment E stretch)

**Task:** have the memo read by the Week-10 persona (agent designer): can
they pick tool-call budgets from your costs table alone? If any field is
missing (p95 latency, memory ceiling), add it.

**Worked approach:** the costs table needs the *tail*, not the mean —
measure 20 queries and report p50/p95; agents chain calls, and tails
compound.

**Pass criterion:** costs table carries p95; the memo states the machine
the numbers were measured on.

## 5. Self-review rubric (grade before the week ends)

| Criterion | Evidence | Points |
|---|---|---|
| Geometry probes with CIs | reports/geometry-lab.md | 3 |
| CLIP matrix + 4 metrics, both directions | reports/clip-matrix.md | 3 |
| Ablation on real sidecar plan + robustness curve | reports/fusion-ablation.md | 4 |
| Decision memo: numbers traceable, triggers, costs p95 | doc/capstone/encoder_decision.md | 4 |
| Suite: reproducibility + matrix-diagnostics tests green | tests/ | 2 |

**Pass bar:** 13/16 to proceed to Week 09. The ablation (4-pointer) is the
week's highest-value artifact — it is the first *deployment-shape* evidence
in the program.

## Pitfalls recap

- CIs computed without fixing the RNG seed per bootstrap — irreproducible intervals; seed them.
- Rubric graded from memory instead of from committed reports — regenerate and re-read, every time.
- Memo updated without re-running the labs it cites — numbers and reports must share a git commit.
