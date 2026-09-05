# The Modality Gap — From Abstract Warning to Capstone Inventory

**What you'll learn:** what "the modality gap" concretely means in embedding
space, the four ways it shows up in a RAG system, and how the capstone
modality inventory turns each one into a scheduled task.

## 1. The gap, measured not asserted

Contrastive models like CLIP align modalities into *shared* space, but the
clouds of image and text embeddings sit in different subregions of it. The
gap is measurable:

```python
import numpy as np

img = np.load("data/embeddings/clip-vit-b32/matrix-img.npy")   # (Ni, 512)
txt = np.load("data/embeddings/clip-vit-b32/matrix-txt.npy")   # (Nt, 512)

def centroid_cos(a, b):
    a, b = a.mean(0), b.mean(0)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

print("cross-modal centroid cos:", centroid_cos(img, txt))     # e.g. 0.55
print("within-text centroid cos:", centroid_cos(txt, txt))     # e.g. 0.93
```

Typical numbers: within-modality cosine ~0.8–0.95, cross-modality ~0.2–0.6.
Two consequences:

1. **Do not threshold cosines across modalities** with a value tuned
   within-modality (e.g., "sim > 0.8 means duplicate").
2. Retrieval still works because ranking is *relative* — the right image
   scores highest among images for that query, even at 0.55 absolute.

## 2. The four appearances of the gap in a RAG system

| Symptom | Root cause | Mitigation |
|---|---|---|
| "Image results feel random vs text results" | per-modality score scales differ | calibrate per modality (z-score or rank fusion) |
| "Charts/slides never retrieved" | OCR text absent; pixels only | add OCR sidecar text at ingest (file 02) |
| "Audio segment matched but useless" | music bed dominated the embedding | CLAP on bands or route through ASR first |
| "Same doc retrieved twice as text and image" | two units, one document | document-level grouping in the manifest |

The last column is the bridge to the rest of the week: every mitigation is a
**pipeline or manifest decision**, not a model swap.

## 3. The capstone modality inventory

The deliverable that makes the gap actionable. One table in your capstone
README, one row per modality you actually ingest:

| Field | Question it answers |
|---|---|
| Modality + unit | what is one retrieval unit (frame? 30 s clip? page?) |
| Count + raw size | what enters `data/raw/` |
| Encoder + dim | which model fills the embedding column |
| Preproc settings | what goes into `settings_json` |
| Text sidecar? | is there OCR/ASR/caption text to co-index |
| Gap risk | which symptom above is most likely |
| Owner of failure | which file in this week fixes it |

```python
INVENTORY = [
    {"modality": "text",   "unit": "page",   "encoder": "minilm-l6", "dim": 384,
     "sidecar": None,      "gap_risk": "long-doc truncation"},
    {"modality": "image",  "unit": "image",  "encoder": "clip-b32",  "dim": 512,
     "sidecar": "ocr",     "gap_risk": "unindexed charts"},
    {"modality": "audio",  "unit": "30s",    "encoder": "clip-b32(frame-fallback)", "dim": 512,
     "sidecar": "asr",     "gap_risk": "music-bed dominance"},
    {"modality": "video",  "unit": "12-frame clip", "encoder": "clip-b32", "dim": 512,
     "sidecar": "asr+ocr", "gap_risk": "temporal misalignment"},
]
```

## 4. Why the inventory precedes all pipeline work

Teams fail multimodal RAG in week 10 not because the models are weak, but
because unit definitions were implicit: someone indexed per-frame and someone
per-clip, so the eval in Week 12 compared incompatible retrieval units. The
inventory is a two-hour conversation that prevents a two-week debugging
spiral. Write it now; revise it after Week 08's ASR work changes audio units.

## Exercises

1. Measure the gap on any two embedding matrices you already have (Week 04
   text vs a few CLIP image vectors): centroid cosine within vs across.
2. Your demo retrieves a chart image for a text query, but the answer quotes
   the wrong series. Which inventory fields were wrong, and what changes?
3. Draft the inventory table for *your* capstone corpus with real counts from
   `data/raw/` (use `pandas` value counts on a quick directory scan).

## Pitfalls

- "Fixing" the gap by fine-tuning before checking OCR/ASR sidecars — 80% of gap symptoms are missing text, not bad embeddings.
- Comparing absolute cosine values across modalities in product code — they are not on a shared scale.

## Resources

- "Mind the Gap" analyses of CLIP modality gap (Liang et al. 2022).
- Reciprocal Rank Fusion — the rank-fusion baseline for mixed-modality search.
