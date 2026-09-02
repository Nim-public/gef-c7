# Week 7 — Multimodal AI: Building the Foundation

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 17 Oct, 7–10 PM IST (Session 1) · Sun 18 Oct, 7–10 PM IST (Session 2) · Office Hours Thu 22 Oct, 7–8 PM IST

**Practice build:** [06-practice-multimodal-explorer.md](06-practice-multimodal-explorer.md)

---

## Why this week matters

Your capstone so far reads text and tables. Real enterprises also have *images* (products, scans, diagrams), *audio* (calls, meetings), and *video* — and Weeks 7–9 build the multimodal arc: foundation (this week), encoders/architectures (Week 8), and multimodal RAG applications with LanceDB + Gradio (Week 9). This week is about the data layer: what multimodal data looks like, how it's processed, aligned, and evaluated.

## What you will be able to do after this week

- [ ] Define multimodal AI and explain why modality heterogeneity is the core problem
- [ ] Compare text/image/audio/video on representation, preprocessing cost, and typical tasks
- [ ] Build processing pipelines for all four modalities with correct normalization
- [ ] Load popular multimodal datasets and write custom PyTorch Dataset/DataLoader classes
- [ ] Align cross-modal pairs (temporal sync, cross-modal validation, missing-data policy)
- [ ] Evaluate captioning/retrieval with BLEU and CLIPScore, and name the main benchmarks

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-multimodal-ai-landscape.md](01-multimodal-ai-landscape.md) | Definitions, modality comparison, metadata handling | 2 h |
| 2 | [02-modality-processing-pipelines.md](02-modality-processing-pipelines.md) | Text/image/audio/video pipelines + preprocessing traps | 3–4 h |
| 3 | [03-multimodal-datasets-dataloaders.md](03-multimodal-datasets-dataloaders.md) | Datasets tour, custom Dataset classes, DataLoaders | 3–4 h |
| 4 | [04-data-alignment-synchronization.md](04-data-alignment-synchronization.md) | Temporal alignment, cross-modal validation, missing data | 2–3 h |
| 5 | [05-evaluation-metrics-benchmarks.md](05-evaluation-metrics-benchmarks.md) | BLEU, CLIPScore, retrieval metrics, benchmark tour | 2 h |
| 6 | [06-practice-multimodal-explorer.md](06-practice-multimodal-explorer.md) | Dataset explorer + alignment audit (practice) | 3 h |

## Environment setup

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install transformers datasets pillow
pip install librosa soundfile          # audio
pip install matplotlib pandas tqdm
```

A webcam/phone mic helps for the practice exercises, but all labs run on bundled/downloadable samples (no GPU needed).

## Self-check before Week 8

1. Why can't you one-size preprocess all modalities — give one modality-specific trap each for image, audio, video.
2. Your dataset has 10k image-caption pairs but 300 images have no caption. What are your three options, and what does each do to training/eval validity?
3. BLEU-4 = 0.42 on captions — what does that number *not* tell you, and which semantic metric complements it?
4. What breaks first if you shuffle frames independently of their audio track? (Answer with the word "alignment" in the sentence.)
5. For your capstone: which modalities exist in your data today, and which one would you add first — why?
