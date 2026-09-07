# 04.1 — CLIP & Zero-Shot Vision

> Subfolder index: [README.md](README.md) · Parent: [../04-modern-models.md](../04-modern-models.md)

---

## What you'll learn

- CLIP's dual-encoder output, consumed three ways
- Zero-shot classification with prompt engineering
- Raw embeddings for region retrieval (the W9-02 preview)
- The failure catalog: counting, negation, fine-grained differences

## 1. Three ways to consume CLIP

```python
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# A) classification — labels compete (softmax):
inputs = proc(text=["a photo of a car", "a photo of a bicycle"],
              images=img, return_tensors="pt", padding=True)
out = model(**inputs)
probs = out.logits_per_image.softmax(-1)             # (1, n_labels)

# B) retrieval embeddings — independent, comparable:
img_emb = out.image_embeds / out.image_embeds.norm(dim=-1, keepdim=True)
txt_emb = out.text_embeds / out.text_embeds.norm(dim=-1, keepdim=True)

# C) similarity score — one pair (CLIPScore, W7-05):
score = float((img_emb @ txt_emb.T).item())
```

| Consumption | Output | Use |
|---|---|---|
| softmax classification | competing labels | closed-set categorization |
| normalized embeddings | indexable vectors | retrieval, dedup, clustering (W9-02) |
| pairwise score | 0–1 similarity | caption evaluation, filtering |

## 2. Prompt engineering for CLIP

The prompt-ensemble trick (W8-04) with measurable effect:

```python
TEMPLATES = ["a photo of a {}.", "a bad photo of a {}.", "a cropped photo of a {}.",
             "a close-up photo of a {}.", "an origami {}."]   # the paper's 80, abbreviated

def ensemble_probs(img, labels):
    prompts = [t.format(l) for l in labels for t in TEMPLATES]
    out = model(**proc(text=prompts, images=img, return_tensors="pt", padding=True))
    sims = out.logits_per_image.reshape(len(labels), len(TEMPLATES))
    return sims.mean(-1).softmax(-1)                # average per label, then normalize
```

Ensembling averages out template quirks — measured gains of 2–5 points on hard classes. The labels themselves matter more: "a photo of a mechanical keyboard, with keys" beats "keyboard".

## 3. The failure catalog (test, don't trust)

| Failure | Example | Why |
|---|---|---|
| **Counting** | "two dogs" vs "three dogs" | no numerical grounding |
| **Negation** | "a photo with no car" | CLIP matches surface tokens |
| **Fine-grained** | two similar product models | embedding resolution |
| **Compositionality** | "red cube on blue sphere" | binds attributes weakly |
| **Text in images** | OCR-like reading | weak text rendering sensitivity |

Each failure gets a probe in the exercises — and each maps to a mitigation: detection models for counting (W20-01), OCR for text (E4-02), fine-grained classifiers for products.

## 4. Region-level CLIP (the W9 bridge)

CLIP on *crops* extends it to localization: detect regions (W20-01 DETR/SAM) → embed each crop → each region becomes an indexable asset with its own embedding. The W9-02 multi-vector table (text_vec + image_vec) then indexes regions and whole images side by side — retrieval can return "the region of image 7 that matches this query".

## Exercises

1. Zero-shot sweep: 10 product images × 5 labels — confusion analysis; which confusions are visual (similar products) vs prompt (label wording)?
2. Ensemble A/B: single template vs 5-template ensemble on the hardest 3 images — measure the flip rate.
3. Negation probe: "a photo with no X" scoring — quantify the failure (W8-04's catalog, your data).
4. Region embeddings: crop 5 detected regions (W20-01) and embed each — build a mini region-retrieval demo over 20 images.
5. Cross-model CLIP: base vs `laion/CLIP-ViT-B-32-laion2B-s34B-b79K` on the same 10 images — which handles your domain better? (The W5-02 bake-off, vision edition.)

## Pitfalls

- **CLIP for text-in-images** — it's weak at reading; OCR (E4-02) for anything textual
- **Similarity ≠ relevance** — CLIP scores are uncalibrated across prompts; within-prompt rankings only
- **Processor mismatch** — CLIPProcessor's resize/normalize must match the model's training; manual preprocessing shifts embeddings
- **Image size sensitivity** — CLIP resizes to 224²; small objects in large images vanish
- **Batch padding text** — `padding=True` with `text=[...]` matters; unpadded batches misalign

## Resources

- Radford et al., *CLIP* (W8-04's source) — §3.1.1 prompt engineering
- HF [zero-shot image classification](https://huggingface.co/docs/transformers/tasks/zero_shot_image_classification)
- [OWL-ViT](https://huggingface.co/docs/transformers/model_doc/owlvit) — open-vocabulary detection (the detection upgrade, W20-01)
- W20-01 (detection/segmentation) — the localization partner
