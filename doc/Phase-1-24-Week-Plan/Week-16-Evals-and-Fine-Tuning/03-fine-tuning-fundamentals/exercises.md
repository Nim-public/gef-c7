# Exercises — Fine-Tuning Fundamentals

Expanded set with worked approaches. The deliverable: the SFT dataset
(governed, masked, audited), one training run with a defensible
best-pick, and the overfitting diagnosis.

## 1. The SFT dataset (from 01-sft-data)

**Task:** build 200 records from your logs and failure clusters; apply
the distribution table; validate with the W16-02 gates.

**Worked approach:** the dataset's format *is* the behavior — citations
in every assistant turn, refusals phrased like the deployment. The W16
validation gates (labels, diversity, leakage, distribution) run before
the GPU time.

**Pass criterion:** 200 records; distribution per §3's table; the
validation report green.

## 2. The tokenization audit (from 02-tokenization-loaders)

**Task:** apply the template; run the four loader checks (round-trip,
structure, tail integrity, length distribution); fix any mask bug.

**Worked approach:** the loader audit runs before every training run —
five minutes against hours. The tail-integrity check is the citation
survival assertion; truncation policy is the middle-out rule.

**Pass criterion:** 4/4 checks green; the truncation drill preserves
citations.

## 3. The training run (from 03-training-loop)

**Task:** run the loop with the §1 arguments; produce the eval curve;
`load_best_model_at_end` picks the checkpoint; commit the artifact trio.

**Worked approach:** the artifact trio (config, curve, eval results) is
the run's evidence — committed together, reproducible from the config
and seed.

**Pass criterion:** the curve produced; best-pick named; the trio
committed.

## 4. Overfitting diagnosis (from 04-overfitting-diagnosis)

**Task:** run the paraphrase probe on 10 training questions; run the
held-out gap per checkpoint; apply the decision rules.

**Worked approach:** the paraphrase collapse is the sharpest probe —
>20% quality drop on paraphrases means memorization. The held-out gap
per epoch is the systematic version of the same signal.

**Pass criterion:** the probes run; the decision rules applied; the
final checkpoint justified by the curve and the probes.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| SFT data: 200 records, governed | dataset + report | 4 |
| Tokenization: 4 audits green | audit tests | 3 |
| Training run: curve + best-pick + trio | artifacts | 4 |
| Overfitting: probes + decision rules | diagnosis | 4 |
| Pin note (run config, seeds) | pin note | 2 |

**Pass bar:** 15/18 to proceed to file 04 (LoRA/QLoRA). The overfitting
diagnosis (4-pointer) is the fine-tuning week's discipline — the eval-
during-training chart is where honesty lives.

## Pitfalls recap

- Fine-tuning on prompts without masking — the model learns to write
  prompts; the masking audit catches it.
- Tail-truncation deleting citations — the middle-out policy protects
  the behavior.
- Best-pick by training loss — eval performance picks the checkpoint;
  training loss always improves while overfitting.