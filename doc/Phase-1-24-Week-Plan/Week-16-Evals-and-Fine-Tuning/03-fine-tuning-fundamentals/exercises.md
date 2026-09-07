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

## 6. The fine-tuning pin note (the run's manifest)

**Task:** consolidate the fine-tuning stack in `reports/sdk-versions.md`:
the SFT data version, tokenizer audits, the run's args/seed, and the
overfitting record — one block.

**Worked approach:** the fine-tuning manifest follows the pin
discipline: the data version, the audits, the run config, and the
diagnosis record.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## 8. The fine-tuning review page

**Task:** write `reports/fine-tuning-review.md`: the SFT dataset's mix,
the tokenization audits, the training curve with the best-pick, and the
overfitting probes — the fine-tuning week's evidence page.

**Worked approach:** the page composes files 01–04 into one sheet: the
data's distribution, the loader audits, the run's curve and best-pick,
and the probes. The reviewer question — "why does this fine-tuned model
behave correctly?" — is answered by the page.

**Pass criterion:** the page answers the trust question in one read;
every number cites its artifact.

## 9. The rubric self-review (the week's final gate)

| Criterion | Evidence | Points |
|---|---|---|
| SFT data: 200 records, governed, gates green | dataset + report | 4 |
| Tokenization: four audits + startup gate | audit tests | 3 |
| Training: curve + best-pick + trio | artifacts | 3 |
| Overfitting: probes + decision rules | diagnosis | 3 |
| Pin note: run config, seeds, data version | pin note | 3 |

**Pass bar:** 15/18 to proceed to file 04 (LoRA/QLoRA). The diagnosis
probes (3-pointer) are the week's honesty check — they distinguish a
model that learned from one that memorized.