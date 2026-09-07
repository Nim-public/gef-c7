# CLIPScore — Semantic Caption Evaluation, Implemented

**What you'll learn:** the reference-free caption metric: encode image and
caption with CLIP, rescale, and read the number correctly — including the
rescaling constant everyone copies without knowing why.

## 1. The formula

For image v and candidate caption c:

```text
CLIPScore(v, c) = w · max(cos(c, v), 0)        with w = 2.5
```

That is the entire metric (Hessel et al. 2021). The `w = 2.5` rescale exists
only to stretch the cosine range into a friendlier 0–5 band; it carries no
deep meaning. `max(·, 0)` clamps anti-correlated pairs to zero.

```python
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

@torch.no_grad()
def clipscore(image_path: str, caption: str) -> float:
    img = Image.open(image_path).convert("RGB")
    inputs = proc(text=[caption], images=img, return_tensors="pt", padding=True)
    out = model(**inputs)
    img_emb = out.image_embeds[0]
    txt_emb = out.text_embeds[0]
    img_emb = img_emb / img_emb.norm(dim=-1, keepdim=True)
    txt_emb = txt_emb / txt_emb.norm(dim=-1, keepdim=True)
    cos = float(img_emb @ txt_emb)
    return 2.5 * max(cos, 0.0)
```

## 2. Interpretation bands (measured, not folklore)

| CLIPScore | Typical reading |
|---|---|
| < 1.5 | wrong or unrelated caption |
| 1.5–2.0 | related, major details missing/wrong |
| 2.0–2.5 | decent caption; typical human caption ≈ 2.2–2.4 |
| > 2.5 | strongly aligned; > 3.0 often means caption echoes image *dominant* tokens |

The "> 3.0" band is the trap: captions that string together image-class
nouns ("a dog a dog on a grass grass") inflate CLIPScore. Semantic metrics
reward lexical overlap with the *embedding*, which is not the same as a good
caption — hence the pairing rule in §4.

## 3. The two-variant trap: `image_embeds` vs `image_features`

`model(**inputs)` gives you *projected* embeddings (`image_embeds`,
`text_embeds`) — the ones CLIPScore uses. `get_image_features()` returns the
same projected space, but `get_input_features()`/last_hidden_state do **not**
— they are pre-projection. Cosines computed across the wrong spaces look
plausible and are garbage. The sanity check:

```python
# same image, caption copied verbatim from its ground-truth pair:
s_gt = clipscore(PAIR["image"], PAIR["caption_gt"])
s_xor = clipscore(PAIR["image"], "an unrelated sentence about tax law")
assert s_gt > s_xor + 0.5, "embedding space or projection is wrong"
```

Run this once per session; it catches wrong-layer embeddings, wrong
processor, and accidentally comparing `image_embeds` to *hidden states*.

## 4. Pairing rule: CLIPScore + BLEU (+ human spot check)

| Metric | Sees | Blind to |
|---|---|---|
| BLEU | n-gram overlap with references | synonyms, semantics |
| CLIPScore | image-caption semantics | reference style, grammar, detail ordering |
| Human | everything | (expensive) |

The failure each catches in the other: a caption can copy reference n-grams
while describing the wrong image (BLEU high, CLIPScore low); or be fluent
and semantically right while sharing no n-grams (CLIPScore high, BLEU 0).
Report both plus 10 human-rated samples per eval run — that triple is the
minimum honest caption evaluation.

## 5. Reference-free vs reference-based: when each applies

- **Your capstone generations** (LLM-written captions, Week 12+):
  reference-free (CLIPScore) — you have no ground truth for *your* images.
- **Benchmark eval** (COCO): reference-based (BLEU/CIDEr) — five human
  captions exist per image; ignoring them throws away signal.
- **Both, always, when both exist.** The correlation between CLIPScore and
  human judgment is decent on common objects and weak on counting, text
  rendering, and spatial relations — exactly where captions matter for RAG.

## Exercises

1. Implement `RefCOCOEval` that takes (image, [5 refs], candidate) and
   returns BLEU-4 + CLIPScore in one dict; run on 20 COCO pairs.
2. Measure the noun-echo inflation: write a "a X on a Y" caption from the
   image's top CLIP text prompts; compare its CLIPScore to the human
   caption's. Quantify the gap on your 20 pairs.
3. Adversarial pair check (§3) on your encoder; then deliberately break it
   by comparing `image_features` to `text_embeds`-pre-projection and record
   how the assert catches it.

## Pitfalls

- CLIPScore comparisons across different CLIP models — the space changes; the *number* is not comparable.
- Averaging CLIPScore over clips where the caption refers to speech, not visuals — the metric will "fail" correctly; scope it to visual captions.
- Skipping `max(cos, 0)` — negative cosines leak in and drag means down invisibly.

## Resources

- Hessel et al. 2021, "CLIPScore: A Reference-free Evaluation Metric for Image Captioning" §2 (w=2.5).
- CLIP model card: embedding/feature API differences.
