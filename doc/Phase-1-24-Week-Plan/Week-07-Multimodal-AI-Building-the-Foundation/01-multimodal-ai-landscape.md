# 01 — The Multimodal AI Landscape

> Week 7 index: [README.md](README.md)

**Session 1 topics:** *Introduction to Multimodal AI. Multimodal data representation: Datatype comparisons, metadata handling.*

---

## What you'll learn

- What makes a system "multimodal" — and why it's suddenly central
- A rigorous comparison of the four core modalities
- How multimodal data is represented (raw → features → embeddings) and stored
- Metadata handling: the provenance layer that makes multimodal datasets usable

## 1. Definitions

- **Modality**: a channel of information with its own structure — text, image, audio, video, plus tables, code, sensor streams
- **Unimodal model**: one input channel in, one out (Week 2's BERT: text → label)
- **Multimodal model**: consumes or produces ≥2 modalities, *jointly* — CLIP (image+text in, similarity out), Whisper (audio in, text out), VLMs (image+text in, text out), Stable Diffusion (text in, image out)

The joint part matters: stitching four separate unimodal systems with if-statements is not multimodal AI. Joint = shared representations, cross-modal attention, one model reasoning *across* channels (Week 8 builds these architectures).

## 2. Why multimodal, why now

- **Enterprise data is already multimodal**: product photos + specs, call recordings + transcripts, slide decks (text *and* layout *and* images), scanned PDFs (images that must become text)
- **Modality blind spots**: text-RAG cannot answer "find products like this photo"; the information exists, the pipeline can't see it
- **The enablers matured together**: ViT/CLIP (2020–21), Whisper (2022), LLaVA/GPT-4V-class VLMs (2023+), cheap multimodal embeddings — the same transformer recipe (Week 3) generalized to every channel

Where your capstone meets this: Weeks 9's multimodal RAG patterns all assume the *data foundation* built this week.

## 3. Modality comparison — the table to internalize

| | Text | Image | Audio | Video |
|---|---|---|---|---|
| Raw unit | characters/tokens | pixels (H×W×3) | samples (16k/s) | frames × pixels × time |
| Structure | sequential, discrete | 2-D grid | 1-D continuous | 3-D (2-D + time) |
| Typical encoder | transformer (W3) | CNN / ViT (W8) | CNN on spectrogram / wav2vec-class | 3D-CNN / frame+temporal (W8) |
| Embedding dims | 384–4096 | 512–1536 | 768–1024 | 512–1024 (pooled) |
| Preprocessing cost | low | medium (resize/normalize) | medium (resample/mel) | **high** (decode + frame sampling) |
| Data size (1 unit) | ~100s of bytes | ~100s of KB | ~1 MB/min | ~100 MB/min |
| Canonical tasks | classify/summarize/generate | classify/detect/caption/retrieve | ASR/speaker ID/retrieve | caption/retrieve/highlight |
| Representative model | BERT/GPT | ViT, CLIP-image | Whisper, wav2vec2 | ViViT-class, video-LLMs |

Key consequences:

- **Sequence length** explodes for images (196 ViT patches) and video (196 × frames) — this drives attention cost and why video models pool aggressively
- **Continuous vs discrete**: audio/video are continuous signals — sampling rate/fps *is* a modeling decision (information loss is irreversible)
- **Storage asymmetry**: 1 hour of meeting = ~10k words of transcript (60 KB) or ~100 MB audio — your RAG indexes the *transcript*; the audio stays on disk, referenced (Week 9 pattern)

## 4. Data representation: three levels

```text
raw (PNG bytes, WAV PCM, JSON text)
  └─► processed arrays (normalized tensors, mel-spectrograms)      [file 02]
        └─► embeddings (CLIP 512-d, Whisper 1024-d)                [file 03/Week 8]
```

Store all three *references*, not duplicates: raw on disk/object-store, processed arrays cached, embeddings in the vector DB (Week 9's LanceDB tables). Every artifact carries metadata.

## 5. Metadata handling

Metadata is what makes a folder of media into a *dataset*:

| Field | Why |
|---|---|
| `id` (stable) | joins across modalities + stores |
| `source` / `path` / `bytes_sha256` | provenance, dedup, cache-busting |
| `modality`, `mime`, `duration`/`dimensions` | routing, validation |
| `created_at` / `captured_at` | temporal alignment (file 04) |
| `permissions` / `pii_flags` | prefilter + compliance (W5-03) |
| capture context (device, language, channel) | model selection + eval slicing |

```python
from PIL import ExifTags
from pathlib import Path
import hashlib

def image_record(path: Path) -> dict:
    from PIL import Image
    img = Image.open(path)
    exif = {ExifTags.TAGS.get(k, k): v for k, v in (img.getexif() or {}).items()}
    return {
        "id": hashlib.sha1(path.read_bytes()).hexdigest()[:16],
        "path": str(path), "modality": "image",
        "width": img.width, "height": img.height, "mode": img.mode,
        "created_at": exif.get("DateTimeOriginal"),
        "bytes_sha1": True,
    }
```

The manifest pattern (JSONL, one record per asset — Week 1 file 04's format) is the backbone of every lab this month.

## 6. The modality gap (the problem the next 8 files solve)

Different modalities live in incompatible spaces: pixels aren't words. Multimodal AI is, at its core, **building bridges across the gap** — by pairing data for training (alignment, file 04), by projecting into shared spaces (CLIP, W8-04), or by translating (captions/ASR, W9). Keep the gap in mind; every technique this month is a bridge design.

## Exercises

1. Inventory *your capstone's* data by the §3 table: which modalities, volumes, formats. One paragraph in your capstone README.
2. Write `image_record()` above and run it over 10 images; add `audio_record()` for 2 WAV/MP3s (`soundfile.info` gives samplerate/duration).
3. Find one multimodal failure of your current RAG: a question whose answer exists only in an image/table-scan. Log it — it becomes Week 9's demo.
4. Compare storage: text transcript vs audio for the same 5-minute clip — bytes, and *what information each carries* (tone? pauses? sarcasm?).
5. Read one model card of a VLM (e.g., Qwen2-VL, LLaVA): which modalities in/out, what backbone encoders, what license?

## Pitfalls

- **Treating video as "images + text"** — temporal information (motion, order) is lost by frame-ignorant handling
- **Metadata without stable IDs** — alignment (file 04) becomes guesswork
- **Copying raw media into repos** — use manifests + object paths; git is not a media store
- **"Multimodal" = calling two APIs** — without shared representations or cross-modal reasoning, you built glue, not a multimodal system
- **Ignoring modality-specific privacy** — faces and voices are PII in ways text isn't; carry `permissions` from day one

## Resources

- Baltrušaitis et al., *Multimodal Machine Learning: A Survey and Taxonomy* — representation/alignment/fusion taxonomy (this file + files 03/04/08-03 follow it)
- HF [multimodal datasets collection](https://huggingface.co/datasets?modality=modality:image) — browse what exists
- 3Blue1Brown-style primers: how images/audio become tensors (any good recent VLM architecture blog, e.g., LLaVA writeups)
- PIL/Pillow [Exif docs](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) — metadata extraction
