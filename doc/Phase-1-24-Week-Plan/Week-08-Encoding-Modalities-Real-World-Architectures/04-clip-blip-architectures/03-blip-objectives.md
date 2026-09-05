# BLIP Objectives — ITC, ITM, LM, and Capabilities

**What you'll learn:** the three heads inside BLIP-family models, what each
trains, and which capability each unlocks — the map from objectives to the
jobs your capstone can hire them for.

## 1. Three objectives, one backbone

| Head | Full name | Task | Direction | Unlocks |
|---|---|---|---|---|
| ITC | Image-Text Contrastive | align in shared space (CLIP-style) | both | retrieval embeddings |
| ITM | Image-Text Matching | binary: does this pair match? (with hard negatives) | pair-level | reranking, VQA-style scoring |
| LM | Language Modeling | generate caption from image | image→text | captioning, VQA-as-generation |

```python
from transformers import BlipProcessor, BlipModel, BlipForConditionalGeneration
import torch
from PIL import Image

proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
img = Image.open("data/processed/images-224/fig3.jpg").convert("RGB")

# Head 3 (LM): captioning
cap = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
inputs = proc(img, return_tensors="pt")
ids = cap.generate(**inputs, max_new_tokens=30)
print(proc.decode(ids[0], skip_special_tokens=True))

# Head 1 (ITC): retrieval embeddings
model = BlipModel.from_pretrained("Salesforce/blip-image-captioning-base")
with torch.no_grad():
    feats = model.get_image_features(pixel_values=inputs["pixel_values"])
```

## 2. ITM: the head CLIP does not have

ITM scores a *pair*: cross-attention fuses image tokens with text tokens and
a linear head outputs "match". Trained with **hard negatives** — captions
from *similar* images in-batch — which is exactly the failure case of raw
cosine retrieval. The capstone pattern this enables:

```text
retrieve top-K by ITC cosine (cheap, global) → rerank top-K by ITM (expensive, precise)
```

This retrieve-then-rerank is the same shape as BM25→reranker in text RAG
(Week 05), and it works because ITM *sees the pair* rather than comparing
two independent embeddings.

## 3. Capability-to-job mapping

| Capstone job | Head | Why |
|---|---|---|
| index all images for retrieval | ITC | cheap, one vector per unit |
| fix "close but wrong" top-10 | ITM | pair-level scoring with hard-negative training |
| auto-caption images lacking text sidecars | LM | generates the OCR/ASR-adjacent text |
| VQA over your images | LM with prompt | "question: ... answer:" generation |
| zero-shot classification | ITC + prompts (file 02) | no head needed |

Cost note: ITC is one forward per unit; ITM is K forwards per query (rerank
only); LM is autoregressive (the expensive one — reserve for offline
sidecar generation, not query time).

## 4. BLIP-2 in one paragraph (the bridge to VLMs)

BLIP-2 freezes both towers and trains a small **Q-Former**: 32 *learned
query tokens* cross-attend into the frozen image encoder, then interface
with a frozen LLM. Where LLaVA (file 04 of fusion) pastes 576 tokens into
context, Q-Former *compresses* vision to 32 tokens first — cheaper context,
more machinery. The lineage matters: BLIP (train all) → BLIP-2 (bridge
frozen towers) → LLaVA (project + tune) — three answers to "how much vision
does the LLM need to see?"

## Exercises

1. ITC vs CLIP embeddings: compute retrieval R@1 on your mini-benchmark with
   BLIP-ITC and CLIP embeddings; the winner is corpus-dependent — report and
   hypothesize why (caption-heavy vs keyword queries).
2. ITM reranking drill: take the top-10 ITC hits for 10 queries; score each
   pair with an ITM-capable model (or a pair-scoring head you wire); compare
   R@1 before/after rerank — expect +1 rank improvement on hard pairs.
3. LM captioning for sidecars: caption 20 sidecar-less images; spot-check 5
   against the actual images (validation-by-eye); record which captions are
   OCR-wrong (numbers, labels) — that failure list motivates a dedicated OCR
   pass instead of LM captioning for charts.

## Pitfalls

- Using captioning output (LM) as *ground truth* text for retrieval — model captions are plausible, not factual; label them as synthetic in the manifest.
- ITM reranking the whole corpus — it is K× the cost of retrieval; rerank top-K only, K ≤ 20.
- Comparing BLIP vs CLIP on zero-shot classification — BLIP's ITC space differs; run your own pairs, never cross-paper numbers.

## Resources

- Li et al. 2022 (BLIP) §3 (the three objectives, bootstrapped captions).
- Li et al. 2023 (BLIP-2) §3 (Q-Former).
