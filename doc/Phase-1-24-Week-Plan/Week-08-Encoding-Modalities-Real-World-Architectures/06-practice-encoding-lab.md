# 06 — Practice: Cross-Modal Encoding Lab

> Week 8 index: [README.md](README.md) · **Due: before Week 9 (by 31 Oct)**

*(No formal task row in the schedule for Week 8 — this lab is the recommended hands-on. It produces the encoder decision note your Week 9 build depends on.)*

---

## 1. Deliverable

```
encoding-lab/
  lab.ipynb             # or lab.py — the experiments below
  encoders.py           # thin wrappers: encode_image / encode_text / encode_audio
  similarity_report.md  # matrices, retrievals, findings
  encoder_decision.md   # the capstone encoder choice + justification
```

Demo: one image query, ranked top-5 across a mixed corpus (images + captions + audio transcripts) — with a similarity matrix heatmap.

## 2. Experiments

### A. Geometry comparison (file 01)

Encode 10 images with **both** ResNet-18 (torchvision) and ViT-base (HF). For 3 hand-picked similar pairs + 3 dissimilar pairs, compute cosine under each encoder. Table: which encoder separates *your* domain better? (Pinned revisions, `eval()` + `no_grad` — file 01's pitfalls list.)

### B. CLIP contrastive matrix (file 04)

5 images × 5 captions → `logits_per_image` heatmap. Verify: diagonal dominance where pairs are true. Then compute R@1/5/10 with file 07-05's `retrieval_metrics`. Compare against Week 7's CLIPScore exercise — same embeddings, two different metrics.

### C. Prompt-ensemble (file 04)

Zero-shot classification of 5 images with 1 vs 5 prompt templates. Record confidence shifts and any prediction flips.

### D. Fusion ablation (file 03)

Train `EarlyFusionClassifier` on your image+text embeddings for a 3-class task (or synthetic). Eval with image zeroed / text zeroed / both present. Report the degradation ordering.

### E. Audio bridge (file 02)

One audio clip → Whisper transcript + wav2vec2 embedding. Show: text-pipeline retrieval (transcript through your Week 4 search) vs raw-audio-embedding retrieval. Note which queries each serves.

## 3. The encoder decision note (`encoder_decision.md`)

Answer, for your capstone:

1. **Which modalities** does Week 9's RAG need? (from Week 7's inventory)
2. **Encoder per modality** — repo id, embedding dim, revision, license
3. **Fusion plan** — early (concat into one index) / late (separate indexes + RRF, W4-04) / projection (LLaVA-style VLM) — and why
4. **Preprocessing pin** — processor version, mean/std, sampling strategy (the W7-02 determinism rule)
5. **Open risks** — negation, counting, domain shift (with one probe result from A–D each)

## 4. Rubric

- [ ] All five experiments run on real data (≥10 assets), pinned revisions
- [ ] Similarity matrices rendered (heatmap or table) and interpreted
- [ ] Fusion ablation numbers present with the degradation ordering
- [ ] Encoder decision note complete with risks + probes
- [ ] Wrappers (`encoders.py`) reuse processors correctly (no manual normalization bugs — file 01)
- [ ] Everything reproducible from a fresh venv (requirements listed)

## 5. Stretch

- Swap the CLIP backbone (`clip-vit-base-patch32` → `laion/CLIP-ViT-B-32-laion2B-s34B-b79K`, file W2-04) — does your domain's retrieval improve? One-line findings.
- Implement the 4×4 CLIP loss with one wrong pairing (file 04 ex. 1) and visualize which entries the loss punishes.
- SigLIP quick test (`google/siglip-base-patch16-224`): same matrix, same retrieval — worth the swap?

Bring the encoder decision note to Office Hours (29 Oct) — Week 9 starts building the multimodal RAG on *your* choice, and the first question will be "why this encoder?"
