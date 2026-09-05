# ViT — Patches as Tokens, Token-Count Math, Position Embeddings

**What you'll learn:** the ViT's four stages through the template lens, the
token arithmetic that predicts your memory bills, and why position
embeddings are load-bearing.

## 1. Patching = tokenization for pixels

```python
import torch, numpy as np

def patchify(img: torch.Tensor, patch: int = 16) -> torch.Tensor:
    """(3, 224, 224) -> (196, 768): patches are the tokens."""
    C, H, W = img.shape
    P = patch
    n_h, n_w = H // P, W // P
    patches = img.reshape(C, n_h, P, n_w, P)      # cut both axes
    patches = patches.permute(1, 3, 0, 2, 4)       # (n_h, n_w, C, P, P)
    return patches.reshape(n_h * n_w, C * P * P)   # (196, 768)

img = torch.rand(3, 224, 224)
tokens = patchify(img)
print(tokens.shape)     # torch.Size([196, 768])
```

Token-count math, the table to internalize:

| Model | Patch | Grid | Tokens (+CLS) | Dim |
|---|---|---|---|---|
| ViT-B/16 | 16 | 14×14 | 197 | 768 |
| ViT-B/32 (CLIP) | 32 | 7×7 | 50 | 768 |
| ViT-L/14 (CLIP) | 14 | 16×16 | 257 | 1024 |
| SigLIP-B/16 | 16 | 14×14 | 197 | 768 |

Attention cost is O(T²): ViT-B/16 pays (197)² ≈ 39k pairs vs ViT-B/32's
(50)² ≈ 2.5k — a **16× attention cost** for 4× the patches. Patch size is
the resolution/compute dial, and CLIP's B/32 choice is a cost decision as
much as a modeling one.

## 2. The full stem: patch embed + CLS + positions

```python
import torch.nn as nn

class PatchEmbed(nn.Module):
    def __init__(self, dim: int = 768, patch: int = 16, img: int = 224):
        super().__init__()
        n_tokens = (img // patch) ** 2 + 1           # +CLS
        self.proj = nn.Conv2d(3, dim, kernel_size=patch, stride=patch)
        self.cls  = nn.Parameter(torch.zeros(1, 1, dim))
        self.pos  = nn.Parameter(torch.randn(1, n_tokens, dim) * 0.02)

    def forward(self, img: torch.Tensor) -> torch.Tensor:
        x = self.proj(img)                            # (B, 768, 14, 14)
        x = x.flatten(2).transpose(1, 2)              # (B, 196, 768)
        x = torch.cat([self.cls.expand(x.shape[0], -1, -1), x], 1)
        return x + self.pos                           # (B, 197, 768)
```

The elegance worth naming: patch embedding is a **convolution with
kernel=stride=patch** — one linear layer does the flatten+project, which is
also why ViT and CNN differ *only* in context mixing (attention vs
locality).

## 3. Position embeddings: why order is load-bearing

Attention is permutation-invariant — shuffle the 196 patches and attention
returns the same set. Without positional information, ViT is a bag of
patches. Consequences and failure drills:

| PE type | Learned (ViT) | Sinusoidal | RoPE |
|---|---|---|---|
| Fixed size? | tied to 224 | any size | any, relative |
| Zoom/shift generalization | poor (interpolated) | fair | good |
| Used by | original ViT, CLIP | ViT variants | modern LLMs/VLMs |

Drill: feed a 256×256 image to a 224-trained ViT-B/16 → 256 tokens hit a
197-row position table → hard error, not graceful degradation. Resize the
*position grid* (bicubic interpolation of the pos-embedding table) and it
runs — this is exactly what production VLMs do for variable resolution.

## 4. From ViT to CLIP's image tower

CLIP's vision encoder *is* this stem + transformer + pooled CLS patch,
projected to the shared 512-d space by a linear head (see
[`../04-clip-blip-architectures/`](../04-clip-blip-architectures/)). When
your Week-07 pipeline encodes 197 patches... it doesn't: it takes the CLS
patch's projected vector. That is why frame-level CLIP embeddings are cheap
and why patch-level retrieval needs the raw backbone, not the projected head.

## Exercises

1. Verify the O(T²) claim: time ViT-B/32 vs a simulated 14×14 grid at the
   same dim; compute the ratio and compare to 16×.
2. Position-drill: interpolate the pos table 197→257 and encode a 256×256
   image; compare CLS vector cosine vs the 224 version of the same image
   (expect high-but-not-1.0; explain the drop).
3. Param count: compute PatchEmbed's params (proj + pos + cls) for B/16 vs
   B/32; which dominates and why (pos table rows × dim).

## Pitfalls

- Quoting "196 tokens" for ViT-B/32 — it is 50; the two are constantly mixed in student notes.
- `nn.Conv2d(3, dim, patch, stride=patch)` with a stray padding — a 1-pixel pad silently changes the grid to 15×15.
- Interpolating position embeddings *bilinearly on the token axis* instead of reshaping to 14×14 first — spatial structure must be preserved.

## Resources

- ViT paper (Dosovitskiy et al. 2020) §3.1 — the stem is exactly this class.
- CLIP paper §2.3 (ViT-B/32 choice); timm `PatchEmbed` source for production form.
