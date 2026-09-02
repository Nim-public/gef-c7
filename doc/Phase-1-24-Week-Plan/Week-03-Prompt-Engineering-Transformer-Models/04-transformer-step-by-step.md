# 04 — Transformers Step-by-Step

> Week 3 index: [README.md](README.md)

**Session 2 topic:** *Transformers: Tokenizers, Embeddings, Attention Mechanisms, Transformers step-by-step.*

---

## What you'll learn

- The full pipeline: text → tokens → embeddings → attention → prediction
- Self-attention computed **by hand** on a 4-token sentence
- Why Q/K/V split exists (and what breaks without it)
- Multi-head attention, residual connections, and the decoder's causal mask
- A working ~30-line attention implementation you can run and trace

## 0. The pipeline in one picture

```
"The cat sat" ─► tokenizer ─► [464, 1872, 3332]         (Week 1)
                      └─► embedding matrix ─► 3×d vectors   (learned lookup)
                                 └─► N × transformer blocks (attention + FFN)
                                        └─► softmax over vocab ─► next token
```

Every part below is a stage of that picture.

## 1. Tokens → embeddings

Recall Week 1: token IDs are arbitrary integers — `464` is not "less than" `1872`. The model's first learned layer is an **embedding table**: `E ∈ R^(vocab_size × d_model)`, one learned row per token ID.

```python
import torch, torch.nn as nn

d_model = 16
emb = nn.Embedding(50257, d_model)         # GPT-2-sized table
ids = torch.tensor([[464, 1872, 3332]])
x = emb(ids)                               # (1, 3, 16) — the tokens are now vectors
```

`d_model` = the model's "width": GPT-2 small uses 768, Qwen2.5-0.5B uses 896. Add **positional encoding** (learned or RoPE in modern models) so the model can tell word order — attention itself is order-blind.

## 2. Self-attention by hand (4 tokens, 3 dims)

The idea in one sentence: **each token asks "who should I look at?" and mixes in what it finds, weighted by relevance.**

Worked on `"the cat sat down"` with tiny 3-d vectors (numbers invented to be followable):

```python
import numpy as np

x = np.array([                     # 4 tokens × d=3 (after embedding + position)
    [1.0, 0.0, 1.0],   # the
    [0.0, 2.0, 1.0],   # cat
    [1.0, 1.0, 0.0],   # sat
    [0.5, 0.5, 0.5],   # down
])
```

### Step 1 — project to Queries, Keys, Values

Three learned weight matrices make three *different* views of each token:

```python
Wq = np.array([[1,0,0],[0,1,0],[0,0,1]])   # toy: identity (real ones are learned)
Wk = np.array([[1,0,0],[0,1,0],[0,0,1]])
Wv = np.array([[2,0,0],[0,2,0],[0,0,2]])   # values scaled — "what I contribute"

Q, K, V = x @ Wq, x @ Wk, x @ Wv
```

- **Query**: what this token is looking for
- **Key**: what this token advertises/contains
- **Value**: what this token actually passes along if attended to

Why not use `x` directly? Because "how I should be found" (K), "what I'm seeking" (Q), and "what I give you" (V) are three different roles — one matrix can't play all three. (Collapsing Q=K makes every token attend to itself most; Q=K=V makes attention a smearing average. Exercise 3 tests this.)

### Step 2 — scores: how relevant is every key to every query

```python
scores = Q @ K.T / np.sqrt(3)              # scaled dot-product: (4, 4)
# √d scaling: keeps dot products from blowing up softmax as d grows
```

Row `i` = token i's attention over all tokens. Look at row for `"sat"`: which key scores highest? (In real models, verbs attend hard to their subjects — that's the grammar+semantics discovery, learned, not programmed.)

### Step 3 — softmax rows → attention weights

```python
def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

A = softmax(scores)                        # each row sums to 1.0
```

### Step 4 — mix values

```python
out = A @ V                                # (4, 3): each token = weighted mix of all values
```

That's **it** — self-attention is Q·Kᵀ → softmax → ×V. Every "transformer magic" article is elaborating these four lines.

## 3. The full attention function (~15 lines)

```python
import torch, torch.nn as nn

def attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = Q @ K.transpose(-2, -1) / d_k ** 0.5
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float("-inf"))
    return torch.softmax(scores, dim=-1) @ V

class SelfAttention(nn.Module):
    def __init__(self, d_model, d_k):
        super().__init__()
        self.Wq, self.Wk, self.Wv = (nn.Linear(d_model, d_k, bias=False) for _ in range(3))

    def forward(self, x, mask=None):
        return attention(self.Wq(x), self.Wk(x), self.Wv(x), mask)

x = torch.randn(1, 4, 16)                  # (batch, seq, d_model)
out = SelfAttention(16, 8)(x)
print(out.shape)                           # (1, 4, 8)
```

### The causal mask (why LLMs can't cheat)

In a decoder, token *i* must not see tokens > i (or training next-token prediction is trivially solved by looking at the answer):

```python
seq = 4
causal = torch.tril(torch.ones(seq, seq))   # lower-triangular: 1s on/below diagonal
out = SelfAttention(16, 8)(x, mask=causal)  # "sat" now sees only "the cat sat"
```

BERT-style encoders skip the mask (bidirectional); GPT-style decoders require it. Same module, one flag, two families of models (Week 2's file 03 drew this split).

## 4. The transformer block — attention + FFN + residuals

One block =

```text
x ─► LayerNorm ─► multi-head attention ─► (+) residual ─► LayerNorm ─► FFN (d→4d→d, GELU) ─► (+) residual ─► out
```

- **Multi-head**: run `h` attention units in parallel (different learned Wq/Wk/Wv), concat, project. Head 1 might learn syntax links, head 2 coreference, head 3 position patterns — diversity of "who looks at whom".
- **FFN**: per-token 2-layer MLP (often 4× width) — where most parameters and "facts" live
- **Residual (+) connections**: let gradients flow through 100+ layers untouched (fixes vanishing gradients, file 03)
- **LayerNorm**: keeps activations in a stable range

Stack `N` blocks (0.5B model ≈ 24 blocks × ~20M params each ≈ your 500M) → final LayerNorm → project to vocab logits → softmax → next-token distribution. Done: you've walked the entire LLM.

### Trace it on a real model

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")
print(model)
# count blocks:  24 transformer layers, hidden 896, vocab ~151k
# params: ~494M  — reconcile with the W1/W2 param-count formula from file 03
```

`print(model)` is the best free diagram in deep learning: read it layer by layer and name each piece's job.

## Exercises

1. Recompute the hand example with `Wv = I` instead of 2I. How do the mixed outputs change? Which version "carries more information"?
2. In the 4×4 attention matrix `A`, verify every row sums to 1. Apply the causal mask; which entries became 0, and what does each row now represent?
3. Ablations on the 15-line attention: (a) `Q=K` (drop separate Wk), (b) `Q=K=V=x` (no projections). Generate with a tiny model after each surgery if you can — but at minimum explain what each breaks.
4. Multi-head: run `SelfAttention(16, 4)` four times with different seeds, concat to (4,16). How does this differ from one `SelfAttention(16, 16)`?
5. Mask + inspect: tokenize `"the cat sat down because"` with Qwen, run `model(...)` on each prefix, and print top-3 next-token predictions per prefix. Watch prediction quality jump once "sat" appears — that's attention finding its subject.

## Pitfalls

- **Forgetting √d_k scaling** — softmax saturates, gradients vanish; a silent quality killer
- **Masking after softmax** — the `-inf` must go in *before* softmax, or probabilities leak to future tokens
- **`nn.Linear` includes a bias by default** — attention implementations usually disable it; know what your layers actually contain
- **Reading "attention is all you need" as "FFN is useless"** — ~2/3 of parameters live in the FFN blocks
- **Equating parameters with understanding** — trace shapes (`(1, 4, 16)`) at every step; shape errors are where beginners actually get stuck

## Resources

- Jay Alammar, *The Illustrated Transformer* — the standard visual walkthrough
- Karpathy, *Let's build GPT from scratch* — implements today's file in full, line by line
- 3Blue1Brown, *Attention in transformers, visually explained*
- The Annotated Transformer (Harvard NLP) — the paper as runnable code
- Vaswani et al., *Attention Is All You Need* — now readable end to end
