# CNN vs ViT — Inductive Bias, Data Hunger, Compute Trade-offs

**What you'll learn:** the honest version of the comparison: what each
architecture assumes, when each wins *at your data scale*, and what that
means for capstone encoder selection.

## 1. The assumption gap, stated precisely

| Property | CNN | ViT |
|---|---|---|
| Locality | built in (3×3 kernels) | learned (or never) |
| Translation equivariance | built in (weight sharing) | emergent via augmentation |
| Long-range context | grown by depth (rf) | global at layer 1 |
| Data needed | ~1M images to shine | ~14M+ (JFT) to beat CNNs; collapses on 10k |
| With strong augmentation | catches up | still data-hungry below ~100k |

Inductive bias = assumptions baked in. CNNs bake in locality+sharing: right
for natural images, and nearly free knowledge. ViT bakes in nothing: it must
*learn* locality from data — hence ImageNet-1k ViT-Loose vs CNN gap, closed
by scale or by distillation (DeiT: ViT trained on ImageNet with a CNN
teacher + heavy augmentation).

## 2. The two relevant numbers: pretraining size and your corpus

| Your fine-tune data | Recommended encoder | Why |
|---|---|---|
| < 1k images/labels | frozen pretrained (either) + linear head | no training at all; pick by embedding quality |
| 1k–50k | DeiT-style ViT or ResNet50, light FT | augmentation + bias both help |
| > 100k | ViT-B with strong pretraining | data regime where ViT's flexibility pays |

For the capstone, you will *fine-tune nothing*: both encoders run frozen,
which moves the comparison to **embedding-space geometry** on your domain —
measurable, not arguable (practice file 06 does exactly this).

## 3. Compute: FLOPs and memory, honestly

| Model | Params | FLOPs/image (224²) | Tokens | Notes |
|---|---|---|---|---|
| ResNet-50 | 25M | ~4G | n/a (maps) | cheap, fast on all hardware |
| ViT-B/16 | 86M | ~17G | 197 | 4× ResNet compute |
| ViT-B/32 | 86M | ~4.4G | 50 | CLIP's choice: CNN-like cost |
| ViT-L/14 | 304M | ~61G | 257 | quality dial, 15× ResNet |

The token count drives everything: attention FLOPs scale with T², MLP FLOPs
with T·d². At T=197 the MLP dominates; at T=257+ attention starts to matter.
Practical capstone math: encoding 1,000 images with ViT-B/32 ≈ 4.4 TFLOP ≈
seconds on GPU, minutes on CPU — the numbers that decided Week 07's costs.

## 4. The decision procedure (not vibes)

1. **Frozen embeddings, your domain, 200 images:** compute retrieval R@1 for
   ResNet-50 vs ViT-B/32 embeddings (practice lab B). Pick the higher.
2. **If within 2 points:** pick by cost (B/32) or ecosystem (CLIP shares the
   text tower you need anyway).
3. **Fine-tuning actually planned** (>10k labeled): revisit with §2's table.
4. **OCR/screenshot-heavy corpora:** CNNs (conv, high-res feature maps) and
   hybrid ViTs (Swin) degrade less than pure ViT at fixed budget — verify
   on *your* screenshots before believing either.

The capstone tie-in: your corpus decides, not the internet's leaderboard.
A ViT-B/32 that retrieves slides perfectly is worth more than a paper-win.

## Exercises

1. Geometry drill: embed 20 images with ResNet-50 and ViT-B/32; for each,
   compute the mean pairwise cosine matrix and its off-diagonal mean —
   which space is more "spread" (anisotropy check)?
2. Data-hunger demo (optional, GPU): linear-probe both on 100 vs 1,000
   ImageNet-subset labels; plot the gap and compare with §1's table.
3. Cost table: compute encode wall time for your whole corpus on both
   encoders; factor in Week-07's processed-size numbers.

## Pitfalls

- Comparing architectures trained on different data (ResNet on ImageNet-1k vs ViT on JFT-3B) and calling it architecture — pretraining dominates.
- Reading ViT superiority from 2021+ papers without checking the compute budget column.
- Ignoring input resolution: ViT-B/16 at 384² is a different (better, pricier) model than at 224².

## Resources

- Dosovitskiy et al. 2020 (ViT) §4 and Fig. 5 (data-hunger curves).
- Touvron et al. 2021 (DeiT — CNN distillation closes the small-data gap).
- Liu et al. 2021 (Swin — hierarchical ViT, the CNN-informed middle ground).
