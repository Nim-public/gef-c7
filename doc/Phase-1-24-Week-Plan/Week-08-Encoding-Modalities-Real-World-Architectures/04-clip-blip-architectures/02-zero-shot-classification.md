# Zero-Shot Classification — Prompt Ensembles, Logit Reading

**What you'll learn:** turn CLIP into a classifier with no training: prompt
ensembles, softmax-temperature traps, and the honest way to report zero-shot
numbers on your own classes.

## 1. The mechanics, with the one trap named

```python
import torch, torch.nn.functional as F
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

@torch.no_grad()
def zero_shot(image_path: str, class_names: list[str],
              templates: list[str] | None = None) -> dict[str, float]:
    templates = templates or ["a photo of a {}."]
    texts = [t.format(c) for c in class_names for t in templates]
    inputs = proc(text=texts, images=Image.open(image_path).convert("RGB"),
                  return_tensors="pt", padding=True)
    out = model(**inputs)
    img = F.normalize(out.image_embeds, dim=-1)          # (1, 512)
    txt = F.normalize(out.text_embeds, dim=-1)           # (K*T, 512)
    logits = (img @ txt.T).reshape(len(templates), -1).mean(0)   # ensemble mean
    probs = logits.softmax(dim=0)                        # ← trap lives here
    return {c: round(float(p), 4) for c, p in zip(class_names, probs)}
```

The trap: **softmax over cosines×(1/τ)**. CLIP's raw similarities live in
[−1, 1] with cross-modal spread ~0.1–0.35; softmax without the model's
logit scale (~100) is nearly uniform, with it is nearly one-hot. The
processor applies `logit_scale` internally in `get_logits` but *not* in a
manual `img @ txt.T` — you must decide (and document) your temperature.

## 2. Prompt ensembles: what they actually buy

CLIP's paper used 80 templates ("a bad photo of a {}.", "a cropped photo of
a {}.", …) — an average over the *prompt distribution* rather than a bet on
one phrasing:

| Prompt set | Typical zero-shot delta (ImageNet) | When it matters |
|---|---|---|
| 1 template | baseline | never wrong to try first |
| ~7 curated | +1–3 points | class names are rare words |
| 80 full | +3–5 | squeeze the last points |

```python
TEMPLATES = [
    "a photo of a {}.", "a blurry photo of a {}.",
    "a diagram of a {}.", "a screenshot of a {}.",
    "a photo of many {}.", "a photo of one {}.",
]
```

For capstone domains (slides, screenshots, diagrams), templates naming the
*genre* ("a screenshot of a {}") outperform generic photo templates — the
prompt distribution should match your corpus's visual distribution.

## 3. Reading the numbers honestly

| Symptom | Cause | Fix |
|---|---|---|
| All probs ≈ 0.25 on 4 classes | temperature too low (soft) | multiply logits by logit_scale (~100) |
| One class always ~0.99 | temperature too high, or class-name ambiguity | check text embedding norms per class |
| Long class name loses | prompt-length/token effects | equalize phrasing length across classes |
| Sensitive to "a/an" | CLIP's caption prior | keep ensembles; never trust single prompts |

Zero-shot on *your* classes also inherits CLIP's training distribution: it
knows "dog" deeply and "Q3 EBITDA" not at all. The capstone move: zero-shot
for coarse routing (which modality? which section?), few-shot or BM25+OCR
for the fine calls.

## 4. Zero-shot as retrieval's little sibling

Every zero-shot classifier is a retrieval call with K queries — which means
Week-07's retrieval metrics apply directly: build a small labeled eval set,
report accuracy *and* per-class confusion. The capstone eval harness
(`eval_retrieval.py`) and the zero-shot harness share the same pairs; do not
build two datasets for one corpus.

## Exercises

1. Temperature sweep: run zero-shot with logits scaled by {1, 10, 100};
   report the probability distributions — identify the scale that matches
   the model's internal logit_scale and note the qualitative change.
2. Ensemble ablation: 1 vs 7 templates on 20 labeled images from your
   corpus; report accuracy delta and per-class effects.
3. Class-name surgery: find the weakest class, rewrite its name into a
   caption-like phrase ("EBITDA margin" → "a slide showing EBITDA margin");
   measure the delta; write down whether it generalizes.

## Pitfalls

- Softmax over raw cosines reported as "confidences" — they are neither calibrated nor sharp; name the temperature every time.
- Ensembles averaged in *probability* space — CLIP averages logits before softmax (as in §1); mean-of-probs gives different (worse) numbers.
- Zero-shot accuracy quoted without the class list — the list *is* the model; two class lists are two different classifiers.

## Resources

- CLIP paper §3.1.4 (prompt engineering and ensembling, Table on template gains).
- Your Week-07 eval harness — reuse its pairs for zero-shot accuracy.
