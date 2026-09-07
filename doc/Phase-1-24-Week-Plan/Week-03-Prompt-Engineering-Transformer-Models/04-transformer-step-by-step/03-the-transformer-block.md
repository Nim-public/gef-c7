# 04.3 — The Transformer Block

> Subfolder index: [README.md](README.md) · Parent: [../04-transformer-step-by-step.md](../04-transformer-step-by-step.md)

---

## What you'll learn

- The full block: attention + FFN + residuals + layer norm, assembled
- Pre-norm vs post-norm (and why pre-norm won)
- The FFN's role (where most parameters and "facts" live)
- Stacking blocks into a model; verifying against a real architecture

## 1. The block, assembled

```python
import torch, torch.nn as nn

class Block(nn.Module):
    def __init__(self, d_model=16, n_heads=4, d_ff=64):
        super().__init__()
        self.n1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads)     # file 02
        self.n2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(),
                                 nn.Linear(d_ff, d_model))

    def forward(self, x, mask=None):
        x = x + self.attn(self.n1(x), mask)      # attention sub-layer + residual
        x = x + self.ffn(self.n2(x))             # FFN sub-layer + residual
        return x
```

The residual pattern (`x + sublayer(x)`) is the stability mechanism: gradients flow through the identity path untouched (W3-03's vanishing-gradient fix), and each sub-layer only needs to learn the *delta*.

## 2. The FFN — where the parameters live

```
d_model=768 → d_ff=3072 → d_model:  768×3072×2 + biases ≈ 4.7M per FFN
attention projections: 4 × 768×768 ≈ 2.4M per block
→ the FFN holds ~2/3 of the parameters
```

The FFN is the per-token MLP — the "knowledge storage" layer (key-value memories in the literature). Attention *routes*; the FFN *computes and stores*. The W15-03 serving math (per-layer parameter counting) reconciles here.

## 3. LayerNorm — pre-norm vs post-norm

```python
# PRE-norm (modern, GPT-2+): norm BEFORE the sub-layer — gradients flow cleanly
x = x + self.attn(self.n1(x))

# POST-norm (original paper): norm AFTER the residual add — deeper stacks are unstable
x = self.n1(x + self.attn(x))
```

Pre-norm won because post-norm requires careful warmup at depth — the original transformer's post-norm needed learning-rate tricks that pre-norm eliminates. Your Qwen/GPT-class model is pre-norm throughout.

## 4. Stacking into a model

```python
class MiniGPT(nn.Module):
    def __init__(self, vocab, d_model=16, n_heads=4, n_layers=2, max_len=32):
        super().__init__()
        self.emb = nn.Embedding(vocab, d_model)
        self.pos = nn.Embedding(max_len, d_model)
        self.blocks = nn.ModuleList([Block(d_model, n_heads) for _ in range(n_layers)])
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab, bias=False)

    def forward(self, idx, mask=None):
        x = self.emb(idx) + self.pos(torch.arange(idx.size(1), device=idx.device))
        for b in self.blocks: x = b(x, mask)
        return self.head(self.ln_f(x))            # logits over the vocabulary
```

Tied weights (`head.weight = emb.weight`) save vocab-sized parameters — a real trick in small models. The forward is: embed → blocks → norm → logits. Next-token prediction = softmax over the last position's logits.

## Exercises

1. Parameter census per component: embeddings, per-block attention, per-block FFN, head — reconcile the total for MiniGPT and for Qwen-0.5B.
2. Residual ablation: remove the residual connections; train on the sin task — measure the degradation at 2 vs 4 blocks.
3. Pre-vs-post norm: implement both; train a 6-block model on the sin task — the deep-stack stability difference.
4. FFN-capacity probe: d_ff ∈ {1×, 2×, 4×} — quality vs parameters; find the knee for your task.
5. The weight-tying check: tie and untie `head.weight`/`emb.weight` on a small model — parameter and quality delta.

## Pitfalls

- **LayerNorm placement confusion** — pre-norm norms the *input* to each sub-layer; post-norm norms the *output* — mixing them breaks the residual flow
- **FFN mistaken for attention** — different roles: routing vs computation; both are load-bearing
- **Missing `mask` propagation through blocks** — every block's attention needs the same causal mask
- **Untying head/emb weights without re-learning** — the tied init is a warm start; untying needs re-training
- **Assuming blocks are interchangeable** — each block's weights are trained positionally; permuting them degrades the model (though some pruning research exploits similarity)

## Resources

- W3-04 parent (the by-hand build), W8-01 (ViT blocks — same pattern, images), W16-03/04 (training these blocks)
- Karpathy, *nanoGPT* — the minimal complete implementation to compare against
- W13-04 (the ablation methodology) — applies to blocks too
