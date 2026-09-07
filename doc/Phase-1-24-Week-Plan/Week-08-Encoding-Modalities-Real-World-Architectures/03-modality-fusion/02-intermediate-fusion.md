# Intermediate Fusion — Cross-Attention Mechanics and Maps

**What you'll learn:** the mechanism inside every modern VLM: one modality's
queries over another's keys/values. Implement it on small tensors, read the
attention map, and know its cost model.

## 1. The Q/K/V framing, stated once

```text
cross_attention(Q = text_tokens, K = V = image_patches)
   → each text token "asks": which patches are relevant to me?
   → output: text tokens updated with image content (text is the residual stream)
```

The *direction* is the design decision: text→image (text queries image)
injects visual grounding into language; image→text does the reverse. BLIP2's
Q-Former and LLaVA-style projection (file 04) are both answers to "which
direction, and with how many queries?"

## 2. Cross-attention on tensors you can verify

```python
import numpy as np

def softmax(x, axis=-1):
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)

def cross_attention(Q, K, V, Wq, Wk, Wv):
    """Q: (Nq, d), K/V: (Nk, d) -> (Nq, d) plus the attention map."""
    q, k, v = Q @ Wq, K @ Wk, V @ Wv
    scores = q @ k.T / np.sqrt(q.shape[-1])          # (Nq, Nk)
    A = softmax(scores)                               # rows sum to 1
    return A @ V, A

# text tokens ask about image patches:
Nq, Nk, d = 6, 12, 32
Q, K, V = (np.random.randn(n, d) * 0.5 for n in (Nq, Nk, Nk))
out, A = cross_attention(Q, K, V, np.eye(d), np.eye(d), np.eye(d))
print(A.sum(axis=1).round(6))          # each row sums to 1.0
print(A.shape)                          # (6, 12): 6 text tokens × 12 patches
```

With identity projections the map is readable directly: `A[i, j]` = how much
text token *i* attends to patch *j*. In trained models the map is
distributed across heads — but the row-stochastic property and the (Nq, Nk)
shape are invariants you can always test.

## 3. Reading attention maps without lying to yourself

Attention maps are *suggestive*, not explanations. Two honest uses:

| Use | How | Caveat |
|---|---|---|
| Sanity check | object-word pair lights up the object's patches | correlation only |
| Failure triage | uniform map = pathway collapsed; single-column map = patch 0 starved | shows *symptoms* |

```python
def map_diagnostics(A: np.ndarray) -> dict:
    return {
        "entropy_mean": float(-(A * np.log(A + 1e-9)).sum(-1).mean()),
        "max_col_share": float(A.max(axis=1).mean()),
    }
```

(Delete the typo'd line when copying — the dict should close after the
second key. High entropy ≈ diffuse attention; a cap that dominates one
column across all rows ≈ a dead/identity pathway.)

## 4. The cost model

Cross-attention cost is `Nq × Nk × d` per head — *not* the self-attention
`N²`, because queries and keys have different lengths. For LLaVA-scale
inputs: 576 image tokens (ViT-L/14 @ 336²) as K/V into a 4k-token text
stream = 2.3M pairs per head — cheap relative to the LLM's self-attention.
This asymmetry is *why* VLMs inject vision via cross-attention/projection
rather than image self-attention over the whole sequence.

## Exercises

1. Direction drill: swap Q and K/V roles; verify the output shape changes
   meaning (patches now query text) and that accuracy on a synthetic
   grounding task flips accordingly.
2. Entropy drill: build three maps (uniform, one-hot, learned-looking) and
   compute `map_diagnostics`; write the diagnostic table you would use to
   triage a real model.
3. Cost check: compute cross-attention FLOPs for (4k text × 576 image ×
   1024 × 32 heads) vs the LLM's self-attention (4k²); the ratio justifies
   the design — put the two numbers in your week notes.

## Pitfalls

- Reading maps as ground truth ("the model looked at the cat") — attention ≠ explanation; treat as one signal among several.
- Scaling scores by 1/√d forgotten — with d=32 the scores are ±5-ish either way, but at d=1024 softmax saturates and maps become one-hot.
- Averaging maps across heads before checking per-head behavior — one dead head hides in a healthy average.

## Resources

- Vaswani et al. 2017 §3.2 (attention as Q/K/V); Lu et al. 2019 (ViLBERT — cross-attention for vision-language, the pattern's origin).
- Attention-map cautionary results (Jain & Wallace 2019, "Attention is not Explanation").
