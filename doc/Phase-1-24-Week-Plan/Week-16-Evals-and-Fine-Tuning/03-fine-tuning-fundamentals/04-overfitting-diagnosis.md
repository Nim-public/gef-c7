# Overfitting Diagnosis — Eval-During-Training Discipline

**What you'll learn:** the diagnosis discipline: eval loss during
training, the divergence chart, the memorization probes, and the
decision rules for stopping — overfitting caught at step 75, not at
deployment.

## 1. The divergence chart

```text
loss
 │╲
 │ ╲  ╲        ← train loss keeps falling
 │  ╲   ╲
 │   ╲    ╲╲
 │    ╲_    ╲╲     ← eval loss rises from step 100
 │      ╲__   ╲╲
 └────────────────── steps
      25 50 75 100 125
        best checkpoint: step 75
```

| Signal | Diagnosis | Action |
|---|---|---|
| eval falls, train falls | healthy learning | continue |
| eval flattens, train falls | memorization starting | near the stop point |
| eval rises, train falls | overfitting | the best-pick was earlier |
| eval never improves | data/task mismatch | back to the data (file 01) |

The chart is the diagnosis — train loss falling while eval rises is
overfitting's signature, and `load_best_model_at_end` already holds the
pre-divergence checkpoint. The discipline is *evaluating during
training*, which makes the diagnosis possible at all.

## 2. The memorization probes (beyond loss curves)

| Probe | Method | Overfit signal |
|---|---|---|
| verbatim recall | ask the model to complete a training question | training answers regurgitated |
| paraphrase collapse | paraphrase a training question | quality collapses on the paraphrase |
| held-out gap | eval vs held-out slice (W16 file 01-04) | the gap widening per epoch |

```python
def paraphrase_probe(model, record: dict, paraphrase: str) -> float:
    orig = quality(model, record["messages"][1]["content"])
    para = quality(model, paraphrase)
    return orig - para            # a large drop = memorized, not learned
```

The paraphrase probe is the sharpest: a model that *learned* the
behavior answers the paraphrase equally; a model that *memorized*
collapses. The held-out slice (W16 file 01-04) is the systematic
version — the gap per epoch is the overfitting curve's second axis.

## 3. The decision rules (stop, keep, or revert)

| Situation | Rule |
|---|---|
| eval improves, no divergence | continue |
| eval flat for 2 evals | stop; use the best checkpoint |
| eval rising for 2 evals | stop; best-pick from before the rise |
| held-out gap > 0.1 | stop; reduce epochs or data-repeat |
| paraphrase collapse | the data is too thin — back to file 01 |

## Exercises

1. Train with eval every 25 steps; produce the divergence chart; the
   best checkpoint named by the curve.
2. Paraphrase drill: paraphrase 10 training questions; measure the
   collapse; if >20%, the model memorized — cut epochs and retrain.
3. Held-out drill: eval on the held-out slice per checkpoint; the gap
   per epoch is the second axis of the chart.