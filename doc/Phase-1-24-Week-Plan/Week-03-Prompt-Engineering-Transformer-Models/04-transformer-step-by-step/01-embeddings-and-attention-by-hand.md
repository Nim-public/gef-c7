# 04.1 — Attention by Hand

> Subfolder index: [README.md](README.md) · Parent: [../04-transformer-step-by-step.md](../04-transformer-step-by-step.md)

---

## What you'll learn

- The four attention steps computed on a 4-token sentence, every number shown
- Why Q/K/V are three different projections
- The √d scaling, derived

## 1. Setup: the tokens as vectors

```python
import numpy as np

# 4 tokens × d=3 (post-embedding, post-position)
x = np.array([
    [1.0, 0.0, 1.0],   # "the"
    [0.0, 2.0, 1.0],   # "cat"
    [1.0, 1.0, 0.0],   # "sat"
    [0.5, 0.5, 0.5],   # "down"
])
```

## 2. Step 1 — project to Queries, Keys, Values

```python
Wq = np.eye(3)                      # toy: identity (real ones are learned)
Wk = np.eye(3)
Wv = 2 * np.eye(3)                  # values scaled — "what I contribute"

Q, K, V = x @ Wq, x @ Wk, x @ Wv
```

- **Query** — what this token is looking for
- **Key** — what this token advertises
- **Value** — what this token contributes if attended to

The three-way split is the architecture's core insight: one vector can't simultaneously ask, advertise, and deliver. (The ablation — Q=K, or Q=K=V — is file 02's exercise.)

## 3. Step 2 — scores: the dot products

```python
scores = Q @ K.T / np.sqrt(3)       # (4, 4)
print(np.round(scores, 2))
```

Entry [i][j] = how relevant token j is to query i, scaled by √d. **The √d scaling**: without it, dot products grow with dimension — `exp(50)` saturates softmax to one-hot and kills gradients. With scaling, scores stay in a manageable range.

Hand-check one entry: scores[0][1] = (1·0 + 0·2 + 1·1)/√3 = 1/1.732 ≈ 0.577 — "the" attending to "cat".

## 4. Step 3 — softmax rows to weights

```python
def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))    # the stability trick
    return e / e.sum(axis=-1, keepdims=True)

A = softmax(scores)
print(np.round(A, 2))
# every ROW sums to 1.0 — a probability distribution over "who to look at"
```

Row 0 ("the") might be [0.35, 0.30, 0.20, 0.15] — "the" spreads attention; row 1 ("cat") concentrates on itself and "sat". The pattern is learned, not programmed.

## 5. Step 4 — mix the values

```python
out = A @ V                          # (4, 3)
```

Each output token is a weighted average of all tokens' values. "sat" becomes part-itself, part-"cat", part-"the" — the contextual mixing that makes "bank" in "river bank" different from "bank account" (file 01.4's contextual embeddings, mechanically explained).

## 6. The full hand-trace, summarized

```python
scores = Q @ K.T / np.sqrt(d)   →   A = softmax(rows)   →   out = A @ V
```

Three lines. Everything else in a transformer is bookkeeping around them: multi-head (parallel attention with different projections), residuals (stability), FFN (per-token processing), and the causal mask (decoder variant, file 02).

## Exercises

1. Hand-compute all 16 scores; verify row-wise softmax sums to 1.
2. Change Wv to identity — recompute `out`; compare with the 2I version — which "carries more information"?
3. The Q=K ablation: set Q=K (no separate query projection) — how do the attention weights change? (Every token attends to itself most.)
4. The Q=K=V ablation — show that `out` becomes a blurred average where all rows are similar.
5. Position-sensitivity: swap tokens 1 and 2 in `x` *without* positional encoding — show that attention output is permutation-covariant (order-blind), proving why position embeddings exist.

## Pitfalls

- **Forgetting √d scaling** — softmax saturates, gradients vanish (file 02's fix)
- **Softmax across the wrong axis** — rows (per query), not columns; axis=-1 with row vectors
- **Hand-verification skipped** — the by-hand numbers are the ground truth for debugging the implementation
- **Toy projections that hide the real structure** — identity Wq/Wk makes attention look trivial; add random learned matrices to see real routing
- **Confusing attention output with probabilities** — `A` rows sum to 1 (weights over inputs); `out` rows are value mixtures, not probabilities

## Resources

- W3-04 parent (the full block), W1-01 (tokenization — the input side)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — the visual companion
- Karpathy, *Let's build GPT* — §2's toy at full scale
