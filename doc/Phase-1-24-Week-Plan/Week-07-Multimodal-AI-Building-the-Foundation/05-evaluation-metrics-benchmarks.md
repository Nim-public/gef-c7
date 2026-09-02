# 05 — Evaluation Metrics & Benchmarks

> Week 7 index: [README.md](README.md)

**Session 1 topic:** *Evaluation Metrics and Benchmark: Vision-Language Metrics — BLEU, Semantic Evaluation — CLIP.*

---

## What you'll learn

- N-gram metrics (BLEU) — the math, done by hand, and their known weaknesses
- Semantic metrics: CLIPScore and embedding-based evaluation
- Retrieval metrics for cross-modal search (R@k)
- The benchmark landscape: which one measures which capability

## 1. Why generation metrics are tricky

Classification has one right answer; "write a caption for this photo" has infinite good ones. Metrics split into two camps:

- **Overlap metrics** (BLEU/ROUGE/METEOR/CIDEr): compare n-grams with *reference* texts — cheap, deterministic, weak on meaning
- **Semantic/model-based metrics** (CLIPScore, judge-LLM): compare *meaning* — closer to human judgment, costlier

## 2. BLEU — by hand

BLEU-n = geometric mean of modified n-gram precisions × brevity penalty (BP punishes short outputs):

```
p_n = (# n-grams in candidate matching reference, clipped) / (# n-grams in candidate)
BP  = 1 if len(c) > len(r)  else  e^(1 - len(r)/len(c))
```

Candidate: `"the cat sat on the mat"` · Reference: `"a cat is sitting on the mat"`

| n | candidate n-grams | clipped matches | p_n |
|---|---|---|---|
| 1 | the, cat, sat, on, the, mat (6) | the(1), cat(1), on(1), mat(1) = 4 | 0.667 |
| 2 | the cat, cat sat, sat on, on the, the mat (5) | the mat(1), on the(1) = 2 | 0.400 |

```python
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

ref = ["a cat is sitting on the mat".split()]
cand = "the cat sat on the mat".split()
print(sentence_bleu(ref, cand, smoothing_function=SmoothingFunction().method1))
```

Known weaknesses (know these for evals): ignores synonyms ("sofa" vs "mat" context), one reference only ≈ lucky matching, favors short/safe outputs despite BP, and correlates poorly with human judgment beyond ~2 refs. Use BLEU for *regression tracking*, judge quality by human/CLIPScore.

 Cousins you'll meet: **ROUGE-L** (longest common subsequence — summaries), **METEOR** (synonym/stem-aware), **CIDEr** (TF-IDF-weighted n-grams — captioning's classic metric).

## 3. Semantic evaluation with CLIP

**CLIPScore**: cosine similarity between CLIP's image embedding and the caption's text embedding (×2.5 by convention, for scale).

```python
from transformers import CLIPProcessor, CLIPModel
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def clipscore(image, caption: str) -> float:
    inputs = proc(text=[caption], images=image, return_tensors="pt")
    with torch.no_grad():
        out = model(**inputs)
    img_emb = out.image_embeds / out.image_embeds.norm(dim=-1, keepdim=True)
    txt_emb = out.text_embeds / out.text_embeds.norm(dim=-1, keepdim=True)
    return float((img_emb @ txt_emb.T).item())          # ~[-1, 1]; >0.3 usually "relevant"

print(clipscore(image, "a cat sitting on a mat"))        # generated caption's score
print(clipscore(image, "a stock photo of currency"))     # contrast case
```

Why semantic beats BLEU here: `"a sofa in the corner"` vs `"a couch at the side"` — zero n-gram overlap, high CLIPScore. The flip side: CLIPScore doesn't punish *fabricated* details that are semantically adjacent, so it complements, not replaces, overlap metrics.

**Cross-modal retrieval metrics** (CLIP's native eval): for each image among N, rank all N captions by similarity →

- **R@1 / R@5 / R@10** — is a correct caption in the top k? (and text→image direction)
- **MedR** — median rank of the correct match

```python
import torch

def retrieval_metrics(img_embs, txt_embs, ks=(1, 5, 10)):
    sims = img_embs @ txt_embs.T                     # (N, N)
    ranks = (sims.argsort(dim=1, descending=True) ==
             torch.arange(len(sims))[:, None]).nonzero()[:, 1]
    return {f"R@{k}": float((ranks < k).float().mean()) for k in ks} | \
           {"MedR": float(ranks.median())}
```

## 4. The benchmark landscape

| Benchmark | Modality | Measures |
|---|---|---|
| COCO Captions | image→text | captioning (BLEU-4/CIDEr + CIDEr-D) |
| Flickr30k / COCO retrieval | image↔text | R@1/5/10 both directions |
| VQAv2 / GQA | image+question→answer | VQA accuracy (10-annotator agreement rule) |
| MMMU / MM-Vet / MMBench | image+text | VLM reasoning (frontier evals) |
| AudioCaps / Clotho | audio→text | audio captioning (CIDEr/SPICE) |
| MSR-VTT / MSVD | video↔text | video retrieval/captioning |
| DocVQA / ChartQA | document images | OCR-free document understanding |

Reading discipline (same as Week 2's model cards): a benchmark score is a *screening* signal — your own 25-question harness (the Week 4 pattern, now with multimodal cases) remains the decision-maker.

## Exercises

1. Compute BLEU-1 and BLEU-2 by hand for the example above (show clipped counts); verify with NLTK (method1 smoothing off where possible).
2. Generate 2 captions for one image (BLIP from Week 2's file 03, or a model card demo) and rank them by CLIPScore. Do you agree with the ranking?
3. Build a mini retrieval set: 10 images × 3 captions each; compute R@1/5/10 with file 03's DataLoader + CLIP embeddings.
4. Adversarial CLIPScore: score `"a photo with no cat"` against a cat image. What happened — and what does that say about negation handling (the W2-04 weakness)?
5. Benchmark mapping: for your capstone, which benchmark-style eval would you clone (retrieval? captioning? VQA?) — write the 25-case outline.

## Pitfalls

- **BLEU as the only caption metric** — rewards safe, generic, short captions
- **CLIPScore across model versions** — scores aren't comparable across CLIP checkpoints; pin one evaluator
- **Retrieval eval without direction** — image→text and text→image are different tasks; report both
- **Comparing your score to leaderboard numbers** — different splits/preprocessing; only in-harness comparisons are valid
- **Judge models evaluated on their own outputs** — same warning as Week 5's Ragas; pin and separate

## Resources

- Papineni et al., *BLEU: a Method for Automatic Evaluation of Machine Translation* (2002) — the original
- Hessel et al., *CLIPScore* (2021) — the metric definition paper
- HF [evaluation-suite / metrics docs](https://huggingface.co/docs/evaluate/index) — BLEU/ROUGE/CIDEr implementations
- [VQAv2 explorer](https://visualqa.org) and COCO Captions site — see what tasks actually look like
