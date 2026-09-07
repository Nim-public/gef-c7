# Late Fusion — Ensembles, Calibration, Graceful Degradation

**What you'll learn:** fuse at the *decision* level: separate encoders and
heads, combined by rules or learned weights — the deployment pattern that
degrades gracefully when a modality disappears.

## 1. The three combination rules, implemented

```python
import numpy as np

def late_fuse(scores: dict[str, np.ndarray], weights: dict[str, float],
              rule: str = "weighted") -> np.ndarray:
    """scores: per-modality class probabilities, e.g. {'text': (C,), 'image': (C,)}."""
    live = {m: s for m, s in scores.items() if s is not None}
    if rule == "weighted":
        w = {m: weights[m] for m in live}
        tot = sum(w.values())
        return sum(w[m] * live[m] for m in live) / tot
    if rule == "mean":
        return sum(live.values()) / len(live)
    if rule == "rank":                       # rank fusion (RRF), score-free
        rrs = []
        for m in live:
            order = np.argsort(-live[m])
            ranks = np.empty_like(order); ranks[order] = np.arange(1, len(order) + 1)
            rrs.append(1.0 / ranks)
        return sum(rrs)
    raise ValueError(rule)
```

| Rule | Needs | Robust to | Use when |
|---|---|---|---|
| mean | nothing | scale drift (sort of) | quick baselines |
| weighted | tuned weights | nothing — weights encode trust | calibrated models |
| rank (RRF) | nothing | score-scale mismatch | mixed encoders, the Week-07 gap fix |

Rank fusion's superpower: it never compares probability scales across
modalities — exactly the failure mode the modality-gap file predicted.

## 2. Calibration: the prerequisite for weighted fusion

Weighted fusion of *uncalibrated* scores multiplies nonsense. Reliability
diagram + temperature scaling:

```python
def ece(conf: np.ndarray, correct: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    total = len(conf); err = 0.0
    for i in range(bins):
        m = (conf > edges[i]) & (conf <= edges[i + 1])
        if m.any():
            err += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return float(err)

def temperature_scale(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / T
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()
```

Fit `T` on held-out data (minimize ECE/NLL), *per modality head*. A model
that says 0.9 and is right 0.7 of the time poisons any weighted sum.

## 3. Graceful degradation as an architecture property

Late fusion degrades *by construction*: a modality going missing removes one
score dict entry and the rest still answer. Early fusion needed the zero-
imputation policy; cross-attention needs a learned missing-token trick. The
deployment matrix:

| Failure | Early | Cross-attn | Late |
|---|---|---|---|
| One modality offline | accuracy drop (learned zeros) | drop (unless trained for it) | clean: renormalize weights |
| One modality *degraded* (noisy) | silent contamination | contaminated tokens | contained to its score |
| New modality added | retrain everything | new cross-attn path | new head, new weight |

The capstone demo lesson: late fusion is what you demo when you cannot
guarantee every modality's uptime. Weight renormalization on failure:

```python
def reweight_on_failure(weights: dict[str, float], failed: set[str]) -> dict[str, float]:
    live = {m: w for m, w in weights.items() if m not in failed}
    tot = sum(live.values())
    return {m: w / tot for m, w in live.items()}       # renormalize, don't crash
```

## 4. Late vs early vs intermediate — the honest summary

| Criterion | Early | Intermediate | Late |
|---|---|---|---|
| Interaction depth | shallow (input) | deep (per-layer) | none |
| Data needed | low | high | low |
| Missing-modality | policy hack | trained trick | free |
| Debuggability | high | low (maps lie) | highest |
| Capstone fit | baselines | VLM internals | RAG orchestrator |

The capstone's actual fusion is *late*: your orchestrator retrieves from a
text index and an image index, rank-fuses, and hands a combined context to
the LLM — you have been building late fusion since Week 04 without naming it.

## Exercises

1. Implement ECE for three synthetic heads (overconfident, underconfident,
   calibrated); the calibrated one must score < 0.02.
2. Fit temperature T on a synthetic head's held-out logits; show ECE before
   and after; state T's direction for an overconfident head (T > 1).
3. Rank-fusion drill: fuse a text RAG hit-list and an image RAG hit-list for
   10 queries; compare R@1 of rank fusion vs naive score fusion — score
   fusion must lose when scales mismatch (make them mismatch on purpose).

## Pitfalls

- Weighted fusion with uncalibrated heads — calibrate first, or weights are meaningless numbers.
- Rank fusion ties (equal scores) — average their ranks or jitter; ties are common with duplicate units.
- "Graceful degradation" tested only with a missing modality — also test the *noisy* modality (§3); containment is the harder property.

## Resources

- Guo et al. 2017 (calibration, temperature scaling).
- Cormack et al. 2009 (Reciprocal Rank Fusion — the 60-line paper that works).
