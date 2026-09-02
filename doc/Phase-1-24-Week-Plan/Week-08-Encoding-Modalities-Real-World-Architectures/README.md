# Week 8 — Encoding Modalities & Real-World Architectures

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 24 Oct, 7–10 PM IST (Session 1) · Sun 25 Oct, 7–10 PM IST (Session 2) · Office Hours Thu 29 Oct, 7–8 PM IST

**Practice build:** [06-practice-encoding-lab.md](06-practice-encoding-lab.md)

---

## Why this week matters

Week 7 taught you to *handle* multimodal data; this week teaches you how models *encode* it and how encoders are combined into the architectures you'll deploy — CLIP, BLIP, diffusion, and the fusion patterns behind every VLM. Week 9 then uses these encoders as RAG components. This is the theory-dense week of the multimodal arc; every concept here is exercised by code you run.

## What you will be able to do after this week

- [ ] Trace an image through a CNN (convolution, pooling, feature hierarchy) and a ViT (patches as tokens)
- [ ] Explain audio encoding: spectrograms/mel, raw-audio encoders, and Whisper's input
- [ ] Describe video encoding: frame-based, 3D CNNs, temporal pooling
- [ ] Implement and compare early / intermediate / late fusion with code
- [ ] Walk through CLIP's contrastive loss on paper and run cross-modal retrieval
- [ ] Explain BLIP's three objectives and when to use CLIP vs BLIP
- [ ] Describe the diffusion pipeline's components (VAE, U-Net/DiT, text conditioning, scheduler)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-encoding-text-images.md](01-encoding-text-images.md) | Text encoders recap; CNNs and ViTs | 3–4 h |
| 2 | [02-encoding-audio-video.md](02-encoding-audio-video.md) | Spectrograms, raw-audio encoders, video frames, 3D CNNs | 3 h |
| 3 | [03-modality-fusion.md](03-modality-fusion.md) | Early/intermediate/late/hybrid fusion + the LLaVA pattern | 3 h |
| 4 | [04-clip-blip-architectures.md](04-clip-blip-architectures.md) | Contrastive learning, CLIP math, BLIP objectives | 3–4 h |
| 5 | [05-diffusion-architectures.md](05-diffusion-architectures.md) | Forward/reverse process, latent diffusion, text conditioning | 2–3 h |
| 6 | [06-practice-encoding-lab.md](06-practice-encoding-lab.md) | Cross-modal encoding lab + encoder choice note | 3 h |

## Environment setup

Week 7's stack plus:

```powershell
pip install diffusers safetensors accelerate
```

## Self-check before Week 9

1. A 224×224 image in a ViT with 16×16 patches: how many tokens, and what's the memory implication for video with 8 frames?
2. Why does a CNN generalize better from less data than a ViT on small datasets? (One word from Week 3, one property of convolutions.)
3. Your deployment loses the image stream 10% of the time. Which fusion strategy survives — and why?
4. In CLIP's similarity matrix (N images × N texts), what does the diagonal mean, and what does the loss do to off-diagonal entries?
5. Why does Stable Diffusion generate 512×512 images cheaply while pixel-space diffusion of the same size is prohibitive?
