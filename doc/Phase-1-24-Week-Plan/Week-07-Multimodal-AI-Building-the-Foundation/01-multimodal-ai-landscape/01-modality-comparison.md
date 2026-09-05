# Modality Comparison — Representation, Cost, Tasks, Model Families

**What you'll learn:** the concrete per-modality tradeoffs (not vibes) that
decide what your capstone can realistically ingest, store, and index.

## 1. The comparison table, filled with numbers

The parent file gave you the qualitative table. Here is the quantitative
version, measured on a ~1-hour corpus slice (the kind you will actually own):

| Property | Text | Image | Audio | Video |
|---|---|---|---|---|
| Unit of work | 1 doc (~500 words) | 1 frame @ 720p | 30 s clip @ 16 kHz | 30 s @ 24 fps |
| Raw size | ~3 KB | ~1.5 MB PNG / ~150 KB JPEG | ~1 MB PCM16 | ~50–500 MB (codec) |
| Tokens after prep | ~650 | 197 (ViT-B/32 patches) | 3,000 mel frames | 1,500 (12 sampled frames × 125) |
| Encoding cost (CPU) | ~1 ms | ~80 ms | ~120 ms | ~2.5 s |
| Encoding cost (GPU) | ~0.2 ms | ~3 ms | ~8 ms | ~80 ms |
| Embedding size | 384–1536 floats | 512 floats (CLIP) | 512–1280 floats | 512 floats/frame or 768 pooled |
| Semantic density | very high | medium | low–medium | low (per frame) |
| Typical failure | long-doc truncation | OCR-heavy screenshots | crosstalk, music beds | temporal causality |

Two takeaways that drive everything downstream:

1. **Video is not "images at scale."** A 30 s clip is 720 frames; only ~12
   survive useful sampling. The other 708 are a storage decision, not a
   modeling input.
2. **Audio embeddings are sparse in meaning.** A music bed carries almost no
   retrievable semantics; speech transcripts (Week 08/ASR) carry most of it.
   Budget accordingly.

## 2. Representation inside the model

```python
# Same corpus, four encoders — one interface, wildly different internals.
from transformers import AutoTokenizer, AutoModel, CLIPProcessor, CLIPModel

tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
txt_ids = tok("Q3 revenue rose 12% driven by cloud.", return_tensors="pt")
# -> input_ids [101, ...]: discrete IDs, vocab ~30k, sequence length = words*1.3

clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
# image -> 224x224x3 float tensor, normalized with fixed mean/std,
# split into 14x14 patches of 7x7 pixels = 196 patch tokens + [CLS]
```

The point: a token count of 650 vs 197 vs 3000 means your retrieval index,
batch sizes, and cost projections must be per-modality. A single
"documents are ~500 tokens" assumption is wrong in three of four modalities.

## 3. Task families per modality

| Task family | Text | Image | Audio | Video |
|---|---|---|---|---|
| Retrieval | dense/BM25 | CLIP image→text | text→audio (rare) | frame→text |
| Classification | intent, topic | scene, NSFW | speaker, genre | action |
| Generation | LLM | diffusion | TTS | (via frames + LLM) |
| Structured extraction | NER, tables | OCR, detection | ASR, diarization | ASR + keyframes |

For the capstone, the retrieval row is the only mandatory one — but the
extraction row is what makes your RAG answers *grounded* (OCR for scanned
PDFs, ASR for meeting recordings, keyframes for slide decks saved as video).

## 4. Model families you will actually touch

- **Text:** MiniLM/E5/BGE encoders (Week 04), any chat LLM (Weeks 01–03).
- **Image:** CLIP (contrastive image-text), SigLIP (improved loss), Donut/TrOCR (OCR-as-model).
- **Audio:** Whisper (ASR), CLAP (contrastive audio-text, the "CLIP for sound").
- **Video:** frame sampler + CLIP (what you will build), plus dedicated video encoders (X-CLIP) if you outgrow it.

Rule of thumb for the capstone: **prefer a contrastive dual encoder (CLIP/CLAP)
whenever a modality must meet text in embedding space.** That is the seam
your RAG index needs; everything else is a preprocessing problem.

## Exercises

1. A 2-hour lecture recording (video, 1080p, 24 fps, with slides) enters your
   pipeline. Compute the raw size at 8 Mbps and the *useful* token count after
   12-frame sampling + ASR transcript (~9,000 words). Which modality carries
   the semantics? Which carries layout?
2. You must retrieve "the moment the speaker shows the architecture diagram."
   Design the query path: which embedding, which unit (frame vs clip), and
   what the ground truth unit is in your manifest.
3. Estimate CPU encoding time for indexing 500 images, 200 audio clips, and
   50 videos with the costs in §1. Decide: batch on CPU overnight, or GPU?

## Pitfalls

- Quoting token counts without naming the model — ViT-L/14 uses 256 patches, not 197.
- Treating video duration as compute driver; sampled frames, not seconds, set the cost.
- Assuming audio embeddings can answer "what did they say" — they answer "what did it sound like."

## Resources

- CLIP paper §3 (contrastive pretraining), Radford et al. 2021.
- SigLIP (Zhai et al. 2023) — sigmoid loss vs softmax contrastive.
- CLAP (Wu et al. 2022) — audio-text contrastive pretraining.
