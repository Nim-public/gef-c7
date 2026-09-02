# 04 — CLIP & BLIP: The Real-World Multimodal Architectures

> Week 8 index: [README.md](README.md)

**Session 2 topics:** *Real-World Multimodal Architectures. CLIP: Image-text alignment through encoders and contrastive loss. BLIP: Use of generative and contrastive objectives for multimodal tasks.*

---

## What you'll learn

- CLIP's contrastive training objective — the math, on paper and in code
- Zero-shot classification and retrieval as *consequences* of that objective
- BLIP's three objectives (ITC, ITM, LM) and what capabilities each buys
- Decision guide: CLIP vs BLIP vs VLMs for each capstone job

## 1. CLIP: contrastive alignment end-to-end

**Architecture** (W2-04 previewed usage; here's the machine): two towers — a ViT image encoder and a transformer text encoder — projecting into a **shared embedding space** where matching image-text pairs land close.

**Training**: on ~400M web pairs, for a batch of N pairs compute the N×N cosine matrix; the diagonal is positive, everything else negative. Loss (symmetric cross-entropy over rows and columns — the InfoNCE form):

```
L_img→txt = -log( exp(sim(i,i)/τ) / Σ_j exp(sim(i,j)/τ) )        (and same for txt→img)
τ = learned temperature that sharpens the distribution
```

Hand-run the 2×2 case:

```python
import numpy as np

def clip_loss_2x2(sims: np.ndarray, tau: float = 0.07) -> float:
    # rows: images; cols: texts; diagonal = true pairs
    e = np.exp(sims / tau)
    l_i2t = -np.mean(np.log(np.diag(e) / e.sum(axis=1)))
    l_t2i = -np.mean(np.log(np.diag(e) / e.sum(axis=0)))
    return (l_i2t + l_t2i) / 2

print(clip_loss_2x2(np.array([[0.9, 0.1], [0.1, 0.8]])))   # good alignment -> low loss
print(clip_loss_2x2(np.array([[0.4, 0.4], [0.4, 0.4]])))   # no structure   -> high loss
```

Why the objective *creates* the capabilities: pulling true pairs together and pushing 2(N−1) false pairs apart per batch forces the space to organize by *meaning* — which is why zero-shot classification (labels as texts, W2-04) and retrieval (file W7-05's R@k) work without any task-specific training.

The **prompt-ensemble trick** from the paper: score against 80 prompt templates ("a photo of a {}", "a bad photo of a {}"…) and average — a free accuracy bump that survives in every CLIP-style system.

Limits you must know (test, don't trust): counting, negation, fine-grained differences (two similar products), and compositionality ("the *black* dog *left* of the red car").

## 2. CLIP in code — similarity matrix + retrieval

```python
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

images = [Image.open(p) for p in paths]                 # N images
texts  = ["a photo of a gpu", "a photo of a cpu", ...]  # M labels/captions

inputs = proc(text=texts, images=images, return_tensors="pt", padding=True)
with torch.no_grad():
    out = model(**inputs)
sims = out.logits_per_image / 100.0                     # (N, M) scaled similarities
print(sims.softmax(dim=-1))                             # zero-shot classification rows
```

`logits_per_image` is that N×M matrix — everything CLIP does falls out of it (classification: rows; retrieval: columns; CLIPScore: the diagonal, W7-05).

## 3. BLIP: generative + contrastive objectives in one model

CLIP only *ranks*; it can't write a caption or answer a question. **BLIP** (Bootstrapped Language-Image Pretraining) trains one architecture (MED: multimodal encoder-decoder) with **three objectives**:

| Objective | Mechanism | Capability bought |
|---|---|---|
| **ITC** (image-text contrastive) | CLIP-style alignment of the pair | retrieval, embedding quality |
| **ITM** (image-text matching) | binary head: does this text describe this image? (+ hard negatives) | fine-grained grounding, reranking |
| **LM** (language modeling) | caption generation from the image | captioning, VQA-style generation |

Three objectives, three heads, shared encoders — that's the "generative and contrastive objectives" of the schedule. BLIP-2 adds the **Q-Former**: a small bridging transformer that distills a frozen ViT into ~32 query tokens for a frozen LLM — the parameter-efficient ancestor of today's VLM designs.

```python
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering

cap = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
cproc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
inputs = cproc(image, return_tensors="pt")
out = cap.generate(**inputs, max_new_tokens=30)
print(cproc.decode(out[0], skip_special_tokens=True))

vqa = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
vproc = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
qa = vproc(image, "What color is the car?", return_tensors="pt")
print(vqa.generate(**qa, max_new_tokens=10)[0].tolist() and vproc.decode(vqa.generate(**qa, max_new_tokens=10), skip_special_tokens=True))
```

## 4. Decision guide: which model for which job

| Job | Pick | Why |
|---|---|---|
| Search/rank image corpus by text | **CLIP** | embeddings, fast ANN, built for it |
| Score image-caption fit (eval, W7-05) | **CLIP** (CLIPScore) | calibrated by contrastive training |
| Describe images in words | **BLIP/VLM** | LM objective needed |
| Answer questions about an image | **BLIP-VQA or a VLM** | grounding + generation |
| Filter misaligned pairs at ingest | **BLIP ITM** | trained *specifically* to say "no match" |
| Complex reasoning over image + long context | **VLM** (Qwen-VL, GPT-4V-class) | instruction-following + LLM reasoning |

CLIP and BLIP compose (Week 9's pattern 1 + 2): CLIP retrieves candidates, BLIP/VLM reads and describes them.

## Exercises

1. Implement `clip_loss_2x2` from scratch (done), then extend to 4×4 with one wrong pairing (image 2 paired with text 3) — show the loss increase localized to those rows/columns.
2. Prompt-ensemble test: classify 5 images with 1 template vs 5 templates. Measure mean confidence gap; when does ensembling flip a prediction?
3. ITM reranking: CLIP-retrieve top-10 captions for one image, then BLIP-ITM (`BlipForITM`-style head) rescore them. Does the gold caption move up? (This is exactly Week 5's reranking, cross-modally.)
4. Negation probe (W2-04's known weakness): score `"a photo with no dog"` vs a dog image with CLIP. Then BLIP-VQA: `"Is there a dog?"`. Which model family handles negation better — why?
5. Architecture sketch: draw (ASCII) the BLIP MED showing where ITC/ITM/LM heads attach. Label the data flow for each objective's training pass.

## Pitfalls

- **CLIP for anything generative** — it has no decoder; captions/VQA need BLIP/VLM
- **`logits_per_image` misread as probabilities** — it's a scaled logit; softmax only for *closed-set* classification
- **Batch size illusion in the loss** — CLIP's power scales with *training* batch negatives; your 2×2 hand example is pedagogy, not training
- **BLIP-captioning then trusting captions as ground truth** — captions carry model hallucinations; spot-check against source images (W7-05 discipline)
- **Base-size expectations** — `base` CLIP/BLIP are screening tools; production ranking quality needs `large`/SigLIP-class or domain fine-tuning

## Resources

- Radford et al., *Learning Transferable Visual Models From Natural Language Supervision* (CLIP) — §2.3 (the loss) + §3.1.1 (prompt engineering)
- Li et al., *BLIP: Bootstrapping Language-Image Pre-training* — §3 (MED + the three objectives), §3.3 (CapFilt)
- Li et al., *BLIP-2* — the Q-Former bridge (skim figures)
- HF task guides: [image captioning](https://huggingface.co/docs/transformers/tasks/image_captioning), [zero-shot image classification](https://huggingface.co/docs/transformers/tasks/zero_shot_image_classification)
