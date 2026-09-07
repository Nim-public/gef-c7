# 04.2 — The Attention Function

> Subfolder index: [README.md](README.md) · Parent: [../04-transformer-step-by-step.md](../04-transformer-step-by-step.md)

---

## What you'll learn

- The ~15-line attention implementation with masking
- The causal mask: construction, application, verification
- The ablations: Q=K, Q=K=V, no-scaling — each one's failure mode

## 1. The implementation

```python
import torch, torch.nn as nn

def attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = Q @ K.transpose(-2, -1) / d_k ** 0.5     # scaled dot-product
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float("-inf"))
    return torch.softmax(scores, dim=-1) @ V

class SelfAttention(nn.Module):
    def __init__(self, d_model, d_k):
        super().__init__()
        self.Wq, self.Wk, self.Wv = (nn.Linear(d_model, d_k, bias=False)
                                     for _ in range(3))

    def forward(self, x, mask=None):
        return attention(self.Wq(x), self.Wk(x), self.Wv(x), mask)

x = torch.randn(1, 4, 16)                    # (batch, seq, d_model)
out = SelfAttention(16, 8)(x)
print(out.shape)                             # (1, 4, 8)
```

## 2. The causal mask

```python
seq = 4
causal = torch.tril(torch.ones(seq, seq))    # lower-triangular 1s
# [[1,0,0,0],
#  [1,1,0,0],
#  [1,1,1,0],
#  [1,1,1,1]]

out_causal = SelfAttention(16, 8)(x, mask=causal)
# "sat" now sees only "the cat sat" — position 3+ masked to -inf → zero weight
```

The mask semantics: `mask == 0` positions get `-inf` scores → zero probability after softmax. The future is *structurally* invisible — the decoder's training guarantee (next-token prediction can't cheat, W3-04).

Bidirectional (BERT-style) encoders skip the mask: every token sees every other. Same module, one flag.

## 3. The ablations (each breaks something specific)

| Ablation | What breaks |
|---|---|
| `Q = K` (drop the split) | every token attends mostly to itself — no routing |
| `Q = K = V = x` (no projections) | attention is a fixed similarity smear — nothing learned |
| no √d scaling | softmax saturates on large logits — gradients vanish |
| no causal mask (in a decoder) | training sees the future; generation degenerates |

Each ablation is a 1-line change with a diagnosable behavioral consequence — the experiment set that proves each component's necessity.

## 4. Multi-head (the parallel attention units)

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.h = n_heads
        self.d_k = d_model // n_heads
        self.Wq, self.Wk, self.Wv = (nn.Linear(d_model, d_model, bias=False)
                                     for _ in range(3))
        self.Wo = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x, mask=None):
        B, S, _ = x.shape
        q = self.Wq(x).view(B, S, self.h, self.d_k).transpose(1, 2)   # (B,h,S,dk)
        k = self.Wk(x).view(B, S, self.h, self.d_k).transpose(1, 2)
        v = self.Wv(x).view(B, S, self.h, self.d_k).transpose(1, 2)
        out = attention(q, k, v, mask)                                 # (B,h,S,dk)
        return self.Wo(out.transpose(1, 2).reshape(B, S, d_model))     # concat + project
```

Multi-head = n independent attention patterns computed in parallel, concatenated, and projected. Head 0 might track syntax, head 3 coreference, head 7 positions — the diversity emerges from training, not design.

## Exercises

1. Mask verification: with the causal mask, assert `A[2, 3] == 0` (position 2 can't see 3) and `A[2, 2] > 0`.
2. The scaling ablation: remove √d_k on 64-dim heads with large logits — plot the softmax entropy per step; watch it collapse.
3. Head specialization hunt: train a tiny 2-head model on a copy task; inspect per-head attention patterns — do the heads differ?
4. Multi-head ablation: n_heads ∈ {1, 2, 4, 8} at fixed total width — quality vs heads; find the sweet spot for a small task.
5. The BERT-vs-GPT flip: same module, mask on/off — verify the attention patterns differ exactly in the upper triangle.

## Pitfalls

- **Masking after softmax** — `-inf` must enter the scores *before* softmax; post-masking leaks future information
- **view/transpose confusion in multi-head** — the reshape must split d_model into (heads, d_k) contiguously; wrong order scrambles heads
- **Bias in projections** — attention projections conventionally omit bias; including it is not wrong but changes parameter counts (W16-04's census)
- **Testing attention without masks when the model needs one** — a decoder evaluated bidirectionally produces impossible "understanding"
- **Ignoring head pruning research** — some heads are removable post-training; head count ≠ all-useful

## Resources

- W3-04 parent (the by-hand version), W13 (graphs over sequences — different abstraction, same attention)
- [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) — the paper as runnable code
- Bertivasius, *Effective Transformer* (GitHub) — attention-pattern visualizations on real models
