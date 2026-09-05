# The CLIP Loss — The N×N Matrix by Hand and in Code

**What you'll learn:** contrastive pretraining as an N×N similarity matrix
with a diagonal of positives; compute the loss by hand on N=4, then in code,
and understand the temperature, the symmetric terms, and the batch-size
effect.

## 1. The matrix, hand-computed for N=3

Three image-text pairs. After L2-normalizing embeddings, cosine matrix
(rows = images, cols = texts):

```text
          t0      t1      t2
i0   [  0.90    0.10    0.20  ]     diagonal = matched pairs
i1   [  0.15    0.85    0.05  ]     everything else = negatives
i2   [  0.10    0.25    0.80  ]
```

For image i0, the softmax over its row (temperature τ=0.07, i.e. multiply
logits by 1/τ ≈ 14.3 before softmax): scores 0.90, 0.10, 0.20 → logits
12.86, 1.43, 2.86 → softmax ≈ [0.99995, 0.00002, 0.00008]. Loss(i0→t0) =
−log(0.99995) ≈ 0.00005. The model's job: make the diagonal win every row
*and every column* — that is why there are two losses.

## 2. The symmetric loss in code

```python
import torch, torch.nn.functional as F

def clip_loss(img_emb: torch.Tensor, txt_emb: torch.Tensor,
              temperature: float = 0.07) -> torch.Tensor:
    img = F.normalize(img_emb, dim=-1)              # (N, d)
    txt = F.normalize(txt_emb, dim=-1)
    logits = img @ txt.T / temperature              # (N, N) — the matrix
    targets = torch.arange(len(img))
    loss_i2t = F.cross_entropy(logits, targets)     # rows: each image picks its text
    loss_t2i = F.cross_entropy(logits.T, targets)   # cols: each text picks its image
    return (loss_i2t + loss_t2i) / 2

N, d = 3, 8
img = torch.tensor([[0.9, 0.1, 0.2, 0, 0, 0, 0, 0],
                    [0.1, 0.85, 0.05, 0, 0, 0, 0, 0],
                    [0.1, 0.25, 0.8, 0, 0, 0, 0, 0]], dtype=torch.float32)
loss = clip_loss(img, img.clone())   # toy: text embeddings = image embeddings
```

Why two cross-entropies: row-softmax (image→text) and column-softmax
(text→image) are *different tasks* — the matrix is not symmetric after
softmax. Batch size N is the number of negatives per example: N=32,768
(CLIP's batch) means 32,767 negatives per image; your fine-tune batch of 64
means 63 — the single biggest reason frozen CLIP embeddings outperform
fine-tuned-on-small-data ones.

## 3. The temperature, demystified

| τ | Effect on softmax | Training behavior |
|---|---|---|
| 1.0 | soft, near-uniform | slow learning, weak contrast |
| 0.07 (CLIP's learned init) | sharp | strong gradients on hard negatives |
| learned (CLIP trains it) | adapts scale | the logit scale param you see in configs |

In code, `logit_scale = exp(log_τ)` is a trained parameter (CLIP logs it ≈
100 ≈ 1/0.01). When you fine-tune contrastively, *start from the checkpoint's
logit scale* — resetting it to 1 silently destroys the sharpness.

## 4. Batch effects and the hard-negative structure

The N×N matrix teaches the subtle part: every *other* pair in the batch is a
negative, **including accidental ones** — (image of a dog, text about a dog)
from a different pair. With caption-dense datasets, false negatives are
common; with your capstone's 64-pair batches, a single duplicated caption
corrupts training. This is the direct ancestor of the Week-07 modality-gap
observations: contrastive spaces inherit their batches' statistics.

## Exercises

1. Hand-compute the full CLIP loss for the N=3 matrix above (both terms,
   τ=0.07), then verify with the code — your hand result must match to 1e-3.
2. False-negative drill: duplicate one text in a batch of 8 (identical
   captions, different images); show the target row becomes ambiguous and
   the loss floor rises. State the fix (drop exact duplicates before batching).
3. Temperature drill: compute the loss with τ ∈ {1.0, 0.07, 0.01} on the same
   matrix; plot loss vs τ and explain the monotonic direction.

## Pitfalls

- Forgetting `F.normalize` — cosines become unbounded dot products and τ's meaning changes silently.
- Averaging the two losses wrong (sum vs mean) — it is a constant factor, but it changes your LR tuning; CLIP uses the mean.
- Reporting your 64-batch fine-tune against CLIP's 32k-batch numbers — batch size is part of the method, not an implementation detail.

## Resources

- Radford et al. 2021 (CLIP) §2.2; the loss pseudocode in Fig. 1 is this file.
- Zhang et al. 2022 ("Understanding Deep Contrastive Learning" — false negatives).
