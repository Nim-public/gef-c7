# Geometry Lab — ResNet vs ViT on Your Domain

**What you'll learn:** compare two image encoders *on your corpus* using
geometry probes — mean cosine, anisotropy, neighbor structure — and turn the
numbers into an encoder choice.

## 1. Extract both embedding sets

```python
import numpy as np, torch
from PIL import Image
from transformers import (CLIPModel, CLIPProcessor,
                          ResNetForImageClassification, AutoFeatureExtractor)

paths = sorted(str(p) for p in __import__("pathlib").Path(
    "data/processed/images-224").glob("*.jpg"))[:50]

clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
cproc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
rnet = ResNetForImageClassification.from_pretrained("microsoft/resnet-50")
rfx = AutoFeatureExtractor.from_pretrained("microsoft/resnet-50")

def clip_embed(paths):
    inp = cproc(images=[Image.open(p) for p in paths], return_tensors="pt")
    with torch.no_grad():
        return clip_model.get_image_features(**inp).numpy()

def resnet_embed(paths):
    inp = rfx(images=[Image.open(p) for p in paths], return_tensors="pt")
    with torch.no_grad():
        out = rnet.resnet(**inp).pooler_output.squeeze(-1).squeeze(-1)
    return out.numpy()
```

## 2. The three geometry probes

```python
def geometry(E: np.ndarray) -> dict:
    En = E / np.linalg.norm(E, axis=1, keepdims=True)
    S = En @ En.T
    off = S[~np.eye(len(S), dtype=bool)]
    return {
        "dim": E.shape[1],
        "offdiag_mean_cos": float(off.mean()),          # anisotropy: lower = spread
        "offdiag_std": float(off.std()),
        "top5_nn_mean": float(np.sort(off, axis=1)[:, -5:].mean()),  # local density
    }
```

| Probe | Reads as | Healthy value |
|---|---|---|
| offdiag mean cos | anisotropy (hubness risk) | < 0.5 (CLIP often ~0.6–0.7 — known) |
| offdiag std | spread of similarities | higher = more discriminative space |
| top5 NN mean | local neighborhood tightness | domain-dependent; compare across encoders |

## 3. The comparison that matters: neighbor agreement

Same 50 images: are the two encoders' top-5 neighbors the same images?

```python
def topk_neighbors(E: np.ndarray, k: int = 5) -> np.ndarray:
    En = E / np.linalg.norm(E, axis=1, keepdims=True)
    S = En @ En.T
    np.fill_diagonal(S, -2)
    return np.argsort(-S, axis=1)[:, :k]

agree = np.mean([len(set(a) & set(b)) / 5
                 for a, b in zip(topk_neighbors(Ec), topk_neighbors(Er))])
print(f"top-5 neighbor agreement: {agree:.2f}")
```

Interpretation: high agreement (>0.4) → encoders see the same structure;
pick by cost. Low agreement → they specialize differently; consider *both*
in your index (dual-encoder late fusion, fusion file 03) — that result is
the rare genuine upgrade.

## Exercises

1. Run all three probes for CLIP-B/32 and ResNet-50 on your 50 images;
   tabulate; annotate which encoder's space is more spread.
2. Neighbor agreement at k ∈ {1, 5, 20}: plot agreement vs k — disagreement
   at high k means the spaces encode different *notions of similarity*.
3. Domain stress: rerun on your 10 most OCR-heavy screenshots; if CLIP's
   neighborhood structure degrades (probe values shift), note it in the
   decision memo's "revisit if" list.

## Pitfalls

- Comparing geometry across *raw* vs L2-normalized embeddings — always normalize before cosines (the probe itself normalizes; raw stats mislead).
- 50 images is a *probe*, not an eval — report as a screening, never as a final number.
- ResNet pooler choice (`pooler_output` vs logits) — logits are classification-shaped; use the pooled feature map for geometry.

## Resources

- "Representation degeneration" / anisotropy literature (Gao et al. 2019) — what offdiag mean cos measures.
- Your parity-tested processed images — the only valid input here.
