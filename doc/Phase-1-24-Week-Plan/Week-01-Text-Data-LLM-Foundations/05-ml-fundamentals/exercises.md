# Exercises — ML Fundamentals

> Subfolder index: [README.md](README.md) · Parent: [../05-ml-fundamentals.md](../05-ml-fundamentals.md)

Expanded labs. Shared fixture: the ticket dataset from file 04 (grow it to 150 examples) plus the synthetic regression set from file 02.

---

## E1 — The task decision workshop (file 01)

1. Take 10 product ideas from your own notes; classify each as classification/regression/generation/ranking; state the metric and the data each needs.
2. For your capstone: write the task statement for the *baseline* and for the *LLM solution* — note where the tasks differ.
3. Data-ingredients audit: for each of the three ingredients (x, y, distribution), name one way your current data violates the assumption.

**Worked approach:** exercise 2's "where the tasks differ" row is the routing decision (W15-04) in embryo.

## E2 — Gradient descent mastery (file 02)

1. Divergence hunting on the bowl: binary-search the smallest diverging LR; verify the `2/L` bound analytically.
2. Three optimizers on Rosenbrock: SGD, SGD+momentum, Adam — 2000 steps each, same init; plot loss curves and trajectories; rank with reasons.
3. Schedule A/B: constant vs warmup+cosine, identical everything else — final loss comparison.
4. Stochastic noise experiment: mini-batches of 8 with noise — does the noisy path find a better minimum than full-batch? (Connect to regularization.)

**Worked approach:** exercise 2 is the flagship — three optimizer paths on one contour plot is the image that makes W3-03's §5 permanent.

## E3 — Evaluation forensics (file 03)

1. Confusion-matrix arithmetic: 10 hand-computed metric sets from raw matrices — no sklearn until you've verified your own numbers.
2. Threshold economics: for the ticket router, price false positives (reviewer time) and false negatives (churn risk); find the cost-optimal threshold from the sweep table.
3. The leakage trio: build one dataset demonstrating each leakage kind (feature, preprocessing, temporal) — show inflated vs honest scores side by side.
4. Calibration audit: reliability diagram (10 bins) for the ticket classifier — is 0.8 confidence actually 80% right?

**Worked approach:** exercise 2's cost-optimal threshold is the bridge between ML metrics and product decisions — the skill W15-04's routing calibration reuses.

## E4 — Text classification to production (file 04)

1. Learning curve: accuracy vs training size (25/50/100/150 examples) — where does it flatten? What does that predict for "just add data"?
2. Error taxonomy: every test-set error labeled with one of the four classes (vocabulary gap / mixed intent / annotation inconsistency / ambiguous) — fix the largest class and re-measure.
3. Calibration + threshold: reliability diagram, then the cost-optimal threshold from E3-2 — wire both into the deployment contract.
4. Classical-vs-LLM table: accuracy, p50/p95 latency, $/1k tickets — the full W1-05 §5 table with your measurements.
5. Regression variant: predict ticket resolution time (hours) from text — same pipeline, different loss/metric; note where the pipeline shape changes.

**Worked approach:** exercise 4 is the capstone's evidence table — the classical baseline is the bar the LLM path must clear, and the table is how you prove it cleared.

## Self-assessment

- Can you compute precision/recall/F1 from a raw confusion matrix without sklearn?
- Can you diagnose overfitting from two loss curves in under a minute?
- Can you state your model's deployment contract (input, output, confidence, version) from memory?
