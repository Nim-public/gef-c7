# 01 — Encoding Text & Images

> Week 8 index: [README.md](README.md)

**Session 1 topics:** *Encoding Different Modalities: How text is encoded using tokenizers and Transformer-based models. How images are encoded using Convolutional Neural Networks (CNNs) or Vision Transformers (ViTs).*

---

## What you'll learn

- The text encoder pipeline you already know, restated as a *modality encoder* (for reuse)
- CNNs: convolution, pooling, and the feature hierarchy — computed by hand
- ViT: images as sentences of patches — the bridge to everything transformer-based
- CNN vs ViT: inductive bias, data hunger, and when to pick which

## 1. Text encoding, restated as the template

You've built this (W1-01, W3-04); now treat it as the *pattern* every modality encoder copies:

```text
raw signal ─► tokenize/patch ─► embed ─► transformer blocks ─► pooled representation
```

- Text: chars → tokens → token embeddings → transformer → `[CLS]`/mean-pooled vector
- Image: pixels → **patches** → patch embeddings → transformer → CLS vector (ViT)
- Audio: waveform → spectrogram patches → same (W8-02)

One recipe, four modalities. That's why the transformer "ate" multimodal AI.

```python
from transformers import AutoModel, AutoTokenizer
import torch

tok = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
enc = AutoModel.from_pretrained("distilbert/distilbert-base-uncased")
batch = tok("a man riding a horse", return_tensors="pt")
out = enc(**batch)
print(out.last_hidden_state.shape)      # (1, 6, 768) — one vector per token
print(out.last_hidden_state.mean(1).shape)  # (1, 768) — sentence embedding
```

## 2. CNNs — convolutions by hand

A convolution slides a small kernel over the image, computing local dot products — it learns *spatial* filters (edges → textures → parts → objects):

```
input 4×4:            kernel 2×2 (stride 1):
1 2 3 0               1 0
0 1 2 3               0 1
3 0 1 2
2 3 0 1               output[i,j] = sum(input[i:i+2, j:j+2] * kernel)
```

Output size: `(W − K + 2P)/S + 1` → (4 − 2 + 0)/1 + 1 = **3×3**. Compute one cell by hand (exercise 1).

```python
import torch, torch.nn as nn

conv = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)   # in-ch, out-ch, K
x = torch.randn(1, 3, 224, 224)
print(conv(x).shape)                       # (1, 8, 224, 224)? no — (1, 16, 224, 224)

feat = torch.nn.MaxPool2d(2)(conv(x))      # (1, 16, 112, 112) — downsample, keep strongest
```

Concepts that matter:

- **Pooling** shrinks spatial size, makes detection translation-tolerant
- **Channels grow** as spatial dims shrink (224×224×3 → 7×7×512 in ResNet) — spatial detail trades for semantic richness
- **Receptive field** grows with depth — deep neurons "see" most of the image
- **Skip connections** (ResNet): identity shortcuts past layers — the Week 3 residual idea, essential past ~20 layers

```python
from torchvision import models

resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
resnet.eval()
feats = torch.nn.Sequential(*list(resnet.children())[:-1])   # drop classifier
print(feats(torch.randn(1, 3, 224, 224)).flatten(1).shape)   # (1, 512) — an image embedding
```

## 3. ViT — the image as a sentence

**Patches are tokens.** Split 224×224 into 16×16 patches → 14×14 = **196 patches**; flatten each to 768 numbers (16×16×3); linear-project to d_model; prepend a learnable `[CLS]`; add position embeddings; run a standard transformer:

```
197 tokens ─► 12 transformer blocks ─► [CLS] = image embedding
```

```python
from transformers import ViTModel, ViTImageProcessor
from PIL import Image

proc = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
vit = ViTModel.from_pretrained("google/vit-base-patch16-224")
inputs = proc(images=Image.open("sample.jpg"), return_tensors="pt")
out = vit(**inputs)
print(out.last_hidden_state.shape)          # (1, 197, 768)
print(out.pooler_output.shape)              # (1, 768) — CLS embedding
```

The patch-math you must be able to do (recurring in video, W8-02):

```
tokens = (H/P) × (W/P) + 1
224/16 = 14 → 196 + 1 = 197
448×448 input → 28×28 → 785 tokens — attention cost grows quadratically!
```

## 4. CNN vs ViT — the honest comparison

| | CNN | ViT |
|---|---|---|
| Inductive bias | strong (locality, translation equivariance) | weak (must *learn* locality from data) |
| Small-data behavior | better out of the box | needs big data or heavy augmentation |
| Global context | only via depth/receptive field | every layer, all patches |
| Compute scaling | ~linear in pixels | quadratic in token count |
| Modern relevance | edge/mobile, detection backbones | the default for pretrained vision |

Practical rule for your capstone: use a *pretrained* encoder (CLIP/ViT/DINOv2-class) — you are embedding, not training vision from scratch. W2-02's rule applies: the encoder's *pretraining* decides your embedding quality.

## Exercises

1. Hand-compute the 3×3 convolution output above for the top-left cell and one more; verify with `nn.Conv2d` on a fixed kernel (`weight.data.fill_`, no bias).
2. Parameter count: `conv = nn.Conv2d(3, 64, 3, padding=1)` — how many weights + biases? (3×3×3×64 + 64 — verify in code.)
3. Receptive field trace: two stacked 3×3 convs — what input area does one output pixel see? Compare with one 5×5 conv (same area, fewer params — this is why stacks of small kernels won).
4. ViT token census: for `vit-base-patch16-224`, count embedding-table params (`patch_embed`), position embeddings, and total — reconcile ~86M.
5. Same image → two embeddings: ResNet-512d vs ViT-768d. Cosine between *two similar* images under each encoder. Which separates your domain better? (This feeds file 06's lab.)

## Pitfalls

- **Forgetting `eval()` + `torch.no_grad()`** on frozen encoders — dropout/noise degrades embeddings silently
- **Normalization mismatch** — each pretrained model ships its own mean/std (use its processor); ImageNet stats ≠ universal
- **Assuming ViT handles any resolution** — position embeddings are trained per resolution; odd sizes need interpolation
- **Quadratic attention blindness** — 4× the image ≈ 16× the attention cost (W7-01's video warning, now derivable)
- **Comparing embeddings across different encoders** — different spaces, meaningless cosine (W2-03's rule, again)

## Resources

- CS231n notes on convolutions — the canonical CNN primer
- Dosovitskiy et al., *An Image is Worth 16×16 Words* (ViT) — read §3.1 only
- Jay Alammar, *The Illustrated Transformer* (patch tokens are just tokens)
- torchvision [models docs](https://pytorch.org/vision/stable/models.html) — preprocessing tables per checkpoint
