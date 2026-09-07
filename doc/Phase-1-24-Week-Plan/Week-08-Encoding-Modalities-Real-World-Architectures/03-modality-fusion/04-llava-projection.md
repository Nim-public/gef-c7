# The LLaVA Projection Pattern — Vision into LLM Context

**What you'll learn:** the pattern that made open VLMs possible: a frozen
vision encoder + a small projector + a frozen-or-tuned LLM. Implement the
data flow on small tensors, and understand why "vision as foreign language"
works.

## 1. The architecture in one diagram

```text
image ─▶ ViT (frozen) ─▶ patch tokens (576, 1024)
                          │
                     [projector: MLP]      ← the only trained part (stage 1)
                          ▼
         visual tokens (576, d_llm) ─┐
                                     ▼
   text tokens ────────────▶ LLM ──▶ "The image shows..."
```

LLaVA-1.5's recipe: CLIP ViT-L/14 @ 336² → 576 tokens → 2-layer MLP →
LLM token space; then instruction-tune the LLM (and optionally the
projector) on image-text conversations. The insight: **you do not need to
fuse inside a tower — you can *paste* vision into the context window.**

## 2. The projection, on small tensors

```python
import numpy as np

def llava_inject(text_ids: np.ndarray, vision_feats: np.ndarray,
                 W: np.ndarray, bos_slot: int = 1) -> np.ndarray:
    """Return the full token-id-independent embedding sequence for the LLM.
    text_ids: (T,) — placeholder ids; vision_feats: (576, d_v); W: (d_v, d_llm)."""
    vis = vision_feats @ W                          # (576, d_llm) — the 'translation'
    seq = np.concatenate([vis, text_embs[text_ids]], axis=0)   # vision first
    return seq                                      # LLM consumes embeddings, not ids

text_embs = np.random.randn(32000, 64) * 0.02       # the LLM's embedding table (toy d)
text_ids = np.array([5, 900, 12, 77, 3])
W = np.random.randn(128, 64) * 0.02
seq = llava_inject(text_ids, np.random.randn(576, 128), W)
print(seq.shape)    # (581, 64): 576 visual + 5 text embeddings
```

Two design details worth naming:

1. **Vision goes first** (after a system token): LLMs are causal — image
   tokens before text means every text token can attend to the image.
2. **No new attention machinery** — the LLM's self-attention does the
   "cross-attention" implicitly. That is the whole trick, and why it
   out-trained bespoke cross-attention towers at the time.

## 3. What stage-1 training actually optimizes

The projector `W` is trained so that visual tokens *land in the LLM's
embedding space usefully* — the loss is the LLM's next-token loss on
caption-like targets, with vision frozen. Practical consequences:

| Detail | Consequence |
|---|---|
| 576 tokens/ingest | a 4k context holds ~7 images; 8k holds ~14 — image context budget is a *token* budget |
| Projector trained on captions only | VLM answers "what is shown" well; counting/OCR vary by data mix |
| LLM frozen in stage 1 | vision cannot corrupt language ability — the safety property |

The token math from [`../01-encoding-text-images/03-vit-patch-tokens.md`](../01-encoding-text-images/03-vit-patch-tokens.md)
now pays off: 576 = 24² patches @ 14 px on 336². When you read "LLaVA
supports 672²", you know it is 4× the tokens (48² = 2304) and a 4× context
cost.

## 4. Why this matters for the capstone

Your RAG system's answer generator (Weeks 12+) can consume retrieved
*images* the same way: encode chart → project → paste before the question.
The engineering is exactly §2: embeddings in, sequence assembled, LLM
streams. The costs you must plan: 576 tokens per image is real context
budget — an image costs as much as ~450 words.

## Exercises

1. Assemble-order drill: inject vision *after* the text; explain (causal
   attention) why the LLM can no longer ground text tokens in the image.
2. Token budget: compute how many images fit in an 8k context with 2k
   reserved for text and 256 for the answer; then halve the resolution and
   recompute — write the two numbers as your demo's planning constraint.
3. Projector shape drill: given d_v=1024 (ViT-L) and d_llm=4096, compute the
   2-layer MLP param count at ratio 4 (LLaVA-1.5's `mm_projector`); compare
   with the LLM's params to see why "train only the projector" is cheap.

## Pitfalls

- Assuming visual tokens carry positional info from the *image* grid — they need it *in sequence order*; ViT pos-embeddings cover image positions, sequence order is just concatenation.
- Mixing `image_features` (pre-projection) with an LLaVA-style projector — project the *final* vision-tower output, or dimensions secretly mismatch.
- Forgetting image tokens consume context in *serving* too — batch limits and bills scale with 576-token images, not "one image".

## Resources

- Liu et al. 2023 (LLaVA) and 2024 (LLaVA-1.5) — architecture and training stages.
- Zhu et al. 2023 (MiniGPT-4) — the same pattern with a Q-Former-flavored projector.
