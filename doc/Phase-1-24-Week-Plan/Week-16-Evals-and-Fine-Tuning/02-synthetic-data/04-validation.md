# Validation — Labels, Diversity, Leakage, Distribution

**What you'll learn:** the synthetic-data battery: label verification,
diversity measurement, leakage checks, and distribution comparison —
the four gates every synthetic batch passes before it joins the eval or
training set.

## 1. The four gates

| Gate | Checks | Tool |
|---|---|---|
| labels | gold/expected values correct | hand-check 10% + spot LLM check |
| diversity | variants are spread, not echoed | embedding-space spread or dedup rate |
| leakage | no eval-case text in training data (or vice versa) | n-gram overlap audit |
| distribution | synthetic matches the target mix | the persona grid's coverage + stats |

```python
def validate_batch(batch: list[dict], eval_set: list[str]) -> dict:
    return {
        "label_sample_ok": hand_sample_ok(batch, rate=0.1),
        "dedup_rate": 1 - len(dedupe(batch)) / len(batch),
        "leakage_hits": ngram_overlap(batch, eval_set, n=8),
        "coverage": coverage_report(batch, GRID),
    }
```

The battery is the W7 validation gates' synthetic edition — the same
gate philosophy (validate before serving) applied to generated data.
A batch failing any gate is regenerated or quarantined, not patched.

## 2. The label gate (the human's 10%)

| Check | Method |
|---|---|
| expected value correct | hand-check |
| the "attack" would fool a defender | red-team plausibility |
| the paraphrase preserves the need | the variation-axes contract |

The 10% hand-sample is the labeled data's ground truth anchor — labels
that fail the sample fail the batch. The plausibility check is the
red-team edition: an attack no attacker would send teaches nothing.

## 3. The leakage audit (the subtle killer)

```python
def ngram_overlap(synthetic: list[str], heldout: list[str], n: int = 8) -> int:
    heldout_ngrams = {gram(h, n) for h in heldout}
    hits = 0
    for s in synthetic:
        hits += sum(1 for g in ngrams(s, n) if g in heldout_ngrams)
    return hits
```

| Leak | Direction | Damage |
|---|---|---|
| eval text in training data | eval → train | inflated eval scores |
| training text in eval cases | train → eval | memorization masquerades as skill |
| same source doc in both | either | the W10 held-out rule |

The n-gram overlap audit runs between synthetic batches and every
existing set — direction matters (both ways are damage), and 8-gram
overlap is the standard sensitivity. Hits quarantine the offending
items, not the batch.

## Exercises

1. Run the four gates on one expansion batch (from file 01); produce the
   validation report; regenerate on any failure.
2. Leakage drill: deliberately copy one eval case into the synthetic
   batch; the audit must catch it — the gate proven by its target.
3. Distribution drill: compare synthetic vs real query length/class
   distributions; the persona grid's weights should make them close —
   the grid's validation.

## Pitfalls

- Synthetic data validated by "the model wrote it, it looks right" —
  the four gates exist because generation is confident, not correct.
- Diversity measured by count instead of spread — 100 echoes are one
  query; the embedding spread is the measure.
- Leakage found and patched per-case — the audit runs per batch; per-
  case patches rot.