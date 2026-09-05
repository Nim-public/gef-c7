# Fusion Ablation Lab — Missing-Modality Robustness on Real Data

**What you'll learn:** run the early-fusion ablation from file 03 on *your*
pairs: quantify what each modality contributes, and where the demo breaks
when a sidecar is missing.

## 1. The experimental setup

Two-tower retrieval scored per query — the "classifier" is the retrieval
system itself, and the ablation removes towers:

| Setting | Query side | Corpus side | Question |
|---|---|---|---|
| full | text + OCR text | image embeddings + OCR index | ceiling |
| no-OCR | text only | image + OCR index | how much did sidecar text help? |
| no-image-emb | text + OCR | text index only | what do image embeddings add? |
| noisy-OCR | text + OCR with 30% corruption | full | robustness to bad sidecars |

```python
import numpy as np

def retrieval_r1(q: np.ndarray, c: np.ndarray, gt: np.ndarray) -> float:
    q = q / np.linalg.norm(q, axis=1, keepdims=True)
    c = c / np.linalg.norm(c, axis=1, keepdims=True)
    ranks = (np.argsort(-(q @ c.T), axis=1) == gt[:, None]).argmax(axis=1) + 1
    return float((ranks <= 1).mean())

def ablate(q_full, c_full, mode: str) -> float:
    if mode == "no-OCR":
        return retrieval_r1(q_full[:, :384], c_full[:, :384], GT)   # text half
    if mode == "no-image-emb":
        return retrieval_r1(q_full[:, 384:], c_full[:, 384:], GT)
    if mode == "noisy-OCR":
        qn = q_full.copy()
        flip = np.random.default_rng(0).random(len(qn)) < 0.3
        qn[flip, 384:] = 0                                          # kill sidecar
        return retrieval_r1(qn, c_full, GT)
    return retrieval_r1(q_full, c_full, GT)
```

(The concat here is a *stand-in* for late fusion — the point is the
ablation methodology, which transfers to any fusion scheme.)

## 2. Reading the table like an engineer

Expected outcome shape on chart-heavy corpora:

| Setting | R@1 | Read |
|---|---|---|
| full | 0.55 | ceiling with sidecars |
| no-OCR | 0.35 | −20 pts: sidecar text is load-bearing for charts |
| no-image-emb | 0.40 | −15: image embeddings carry the visual queries |
| noisy-OCR | 0.48 | degradation is *partial* — graceful, not fatal |

Two engineering conclusions follow: (1) the OCR sidecar is worth more than
another encoder upgrade — prioritize Week 09's sidecar work; (2) missing
sidecars degrade but do not collapse — the manifest's `sidecar_status`
flags are sufficient deployment handling.

## 3. The robustness curve (beyond one corruption rate)

```python
for rate in [0.0, 0.1, 0.3, 0.6, 1.0]:
    # 0.0 = full, 1.0 = sidecar fully absent
    ...  # measure R@1 at each rate
```

Plot R@1 vs corruption rate: the curve's shape tells you whether your
fusion *averages* (linear decay) or *short-circuits* (cliff). A cliff means
the fused head over-trusts one pathway — rebalance before the demo, not
during it.

## Exercises

1. Run the 4-cell ablation on your pairs with the real sidecar plan; write
   the table with the interpretation column filled.
2. Robustness curve at 5 corruption rates; identify linear vs cliff shape.
3. Cross-check with Week 07: your inventory's gap-risk column predicted
   which modality would fail — did the ablation agree? Note agreements and
   surprises in the decision memo.

## Pitfalls

- Ablating by *zeroing embeddings* without renormalizing — zeros distort cosine geometry; None-with-renormalization is the honest missingness.
- Corruption applied to test *and* train-style artifacts symmetrically — corrupt only the query side (sidecar absence is a query-time reality).
- Reading ablation deltas as causal "value of the modality" — they are value *in this fusion scheme*; a better fusion changes the deltas.

## Resources

- Your fusion implementations: [`../03-modality-fusion/`](../03-modality-fusion/).
- Week-07 inventory: the gap-risk predictions this lab tests.
