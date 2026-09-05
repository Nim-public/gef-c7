# Video Encoding — Frame Pooling, 3D CNNs, Tubelet Tokens

**What you'll learn:** the three video strategies with their actual costs,
the pooling math that makes frame-level embeddings a *clip* embedding, and
the capstone-relevant decision between them.

## 1. Frame-based encoding: the default, and its pooling

You already encode frames (CLIP, Week 07). Making a *clip* vector is a
pooling decision:

| Pooling over 12 frames | Vector | Preserves | Loses |
|---|---|---|---|
| mean | 512 | static scene gist | motion, order |
| max | 512 | the one salient moment | distribution |
| concat + linear | 6144→512 | co-occurrence | still order-blind |
| temporal transformer | 512 | order, motion proxies | compute (T=12 attention) |

```python
import torch

def pool_frames(frame_embs: torch.Tensor, mode: str = "mean") -> torch.Tensor:
    """(12, 512) -> (512,)."""
    if mode == "mean":  return frame_embs.mean(0)
    if mode == "max":   return frame_embs.max(0).values
    if mode == "temporal-attention":
        w = torch.softmax(frame_embs @ frame_embs.mean(0), dim=0)
        return w @ frame_embs                       # learned-ish weighting
    raise ValueError(mode)
```

The honest limitation: any pooling *before* temporal modeling is
order-blind. "The slide appears, then is explained" and its reverse embed
identically with mean pooling — acceptable for slide decks, fatal for
procedure videos.

## 2. 3D CNNs — convolving over time too

```python
import torch.nn as nn

# 2D conv: sees (k, k) spatial. 3D conv: sees (kt, k, k) spacetime.
conv3d = nn.Conv3d(3, 64, kernel_size=(3, 3, 3), stride=(1, 2, 2), padding=(1, 1, 1))
clip = torch.rand(1, 3, 16, 112, 112)     # (B, C, T=16, H, W)
out = conv3d(clip)
print(out.shape)     # (1, 64, 16, 56, 56) — time kept (stride 1), space halved
```

Kernel (3,3,3) on a 16-frame clip: 27 weights learn *motion patterns*
("expanding edge" = zoom, "moving dark bar" = pan). Cost: 3D kernels on
full clips are ~16× the FLOPs of single frames — R(2+1)D and X3D factor the
cube into spatial+temporal stages to stay affordable. Limits: T=16 windows
see ~0.5 s of action; long-range structure still needs pooling or attention.

## 3. Video transformers — tubelets as tokens

ViViT/ViT-T: extract **t×h×w tubelets** (e.g., 2×16×16) — a token is a
*short spatiotemporal patch*, so tokens carry local motion:

| Model | Token = | T=16×112² clip | Tokens |
|---|---|---|---|
| ViViT-B (tubelet 2×16×16) | 2 frames × 16×16 px | 4×7×7 | 196 |
| Frame-level ViT-B/16 + pooling | 1 frame | 12×197 → pool | 2364 (encode) |

Tubelet attention is *spacetime* attention over 196 tokens — comparable
cost to a single image's ViT-B/16, with motion information the frame-pool
path lacks. The trade: pretrained checkpoints are scarcer and domain-narrow
(Kinetics-style actions) vs CLIP's web-scale image-text.

## 4. The capstone decision table

| Your video content | Strategy | Why |
|---|---|---|
| Slide decks, screencasts | frame sampling + CLIP (done, Week 07) | content is static; motion carries nothing |
| Lectures with demos | frame CLIP + ASR text | speech is the retrieval signal |
| Procedures/how-tos | + temporal transformer or R(2+1)D | order matters; pooling is order-blind |
| Action/sport | 3D CNN / ViViT | motion *is* the semantics |

For GEF C7's lecture-style corpus, **frame-based + ASR remains the right
answer**; the 3D/tubelet path earns its cost only when you have action-heavy
clips and labels to exploit them.

## Exercises

1. Pooling ablation: encode one 12-frame clip three ways (mean/max/
   temporal-attention); retrieve against 10 text queries; which pool wins
   for "the moment the diagram appears"?
2. Order-blindness drill: encode the clip and its time-reversed frame
   sequence with mean pooling — cosines must be ≈1.0; with a temporal
   transformer, they should diverge. Write the two numbers down.
3. Cost check: FLOPs for R(2+1)D-34 vs 12-frame CLIP-B/32 on one clip; the
   gap is your budget argument for/against motion modeling.

## Pitfalls

- Quoting ViViT costs at Kinetics clip lengths for your 30-min lectures — tubelet tokenization of 30 min is ~86k tokens; nobody runs that; segment first.
- 3D conv "understanding" long videos — T=16 windows only; anything longer is pooling, not understanding.
- Comparing frame-CLIP R@K to ViViT R@K trained on action labels — different tasks; retrieval of *content* vs classification of *actions*.

## Resources

- Carreira & Zisserman 2017 (R(2+1)D, I3D); Arnab et al. 2021 (ViViT) §3.
- X-CLIP (Ma et al. 2022) — CLIP-style video-text contrastive, the pragmatic middle.
