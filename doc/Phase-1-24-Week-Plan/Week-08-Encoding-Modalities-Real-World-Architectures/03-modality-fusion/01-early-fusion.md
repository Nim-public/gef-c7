# Early Fusion — Concat Classifiers and Missing-Modality Ablations

**What you'll learn:** fuse at the input (concat feature vectors), train the
strongest cheap baseline in multimodal ML, and measure exactly how much it
depends on each modality — the ablation habit that saves capstones.

## 1. The baseline in 20 lines

```python
import numpy as np

class ConcatClassifier:
    """Early fusion: concat feature vectors, one linear head."""

    def __init__(self, dims: dict[str, int], n_classes: int, lr: float = 0.1):
        self.d = sum(dims.values())
        self.order = sorted(dims)                       # deterministic concat order
        self.offsets = np.cumsum([0] + [dims[m] for m in self.order])
        self.W = np.zeros((self.d, n_classes)); self.b = np.zeros(n_classes)
        self.lr = lr

    def _fuse(self, feats: dict[str, np.ndarray | None]) -> np.ndarray:
        x = np.zeros(self.d, dtype=np.float32)
        for i, m in enumerate(self.order):
            if feats.get(m) is not None:
                x[self.offsets[i]:self.offsets[i + 1]] = feats[m]
        return x                                        # zeros where missing

    def fit_step(self, feats, y: int):
        x = self._fuse(feats)
        logits = x @ self.W + self.b
        p = np.exp(logits - logits.max()); p /= p.sum()
        p[y] -= 1.0                                     # softmax grad
        self.W -= self.lr * np.outer(x, p); self.b -= self.lr * p
        return -np.log(p[y] + 1e-9)
```

Nothing here is deep — that is the point. A tuned concat baseline answers
"does fusion help at all?" before any cross-attention is justified.

## 2. The missing-modality ablation, formalized

The zeros-where-missing line above is a *policy*; ablation is how you learn
its cost:

| Setting | Input | Question answered |
|---|---|---|
| Full | all modalities | ceiling |
| text-only | image = None | per-modality value |
| image-only | text = None | ditto |
| zeroed | image → zeros vector | does the model *use* presence, or content? |

```python
def ablate(model, data: list[tuple[dict, int]], mode: str) -> float:
    acc = n = 0
    for feats, y in data:
        f = dict(feats)
        if mode == "text-only":   f["image"] = None
        elif mode == "image-only": f["text"] = None
        elif mode == "zeroed":     f["image"] = np.zeros_like(f["image"])
        logits = model._fuse(f) @ model.W + model.b
        acc += int(logits.argmax() == y); n += 1
    return acc / n
```

**Zeroed vs None is the diagnostic that matters:** if accuracy with a
zero-vector image ≈ full accuracy, your model learned to ignore the image
pathway (dead fusion) — a silent failure that cross-attention fixes by
*construction* (queries without keys still attend to text).

## 3. When early fusion is the right answer

| Situation | Why early wins |
|---|---|
| Few training pairs (<1k) | one head, few params, no interaction modeling to overfit |
| Features already aligned (CLIP space both sides) | concat in shared space ≈ late fusion in expressiveness |
| Missing data is common | explicit zero/impute policy is inspectable |
| Latency budget | one matrix multiply |

## Exercises

1. Train the concat classifier on 100 synthetic pairs (two Gaussian clusters
   per modality, one modality noisy); ablate all four settings; the full
   model must beat text-only — verify and explain why.
2. Dead-path drill: train with image features *shuffled* across pairs; the
   ablation table should show full ≈ text-only. This is what dead fusion
   looks like before you waste a GPU week on it.
3. Policy drill: change zeros→mean-imputation for missing image features;
   measure ablation deltas on 20% synthetic missingness. Which policy
   degrades less, and what does that imply for your manifest's flags?

## Pitfalls

- Concat order depending on dict iteration — sort keys (done above) or every checkpoint differs run to run.
- Ablating with *random* features instead of zeros/None — measures noise injection, not modality value.
- Reading ablation deltas from a model trained *with* dropout on inputs — dropout already regularizes missingness; the ablation is then optimistic.

## Resources

- Baltrušaitis et al. 2019, "Multimodal ML: A Survey" §3.1 (early fusion taxonomy).
- Your Week-07 manifest flags — the source of missingness for these ablations.
