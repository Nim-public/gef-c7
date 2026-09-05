# Deep-Dive: Modality Processing Pipelines

Parent overview: [`../02-modality-processing-pipelines.md`](../02-modality-processing-pipelines.md)

The overview showed each modality's happy path. Here we go past it:
processor-parity checks that catch silent mismatches, an audio pipeline built
around Whisper's exact feature contract, a video pipeline with honest decode
costs and keyframe strategy, and determinism drills so your runs are
reproducible byte-for-byte.

## File map

| File | What it covers |
|---|---|
| [`01-image-pipeline.md`](01-image-pipeline.md) | Load → EXIF → convert → normalize, with processor parity checks |
| [`02-audio-pipeline.md`](02-audio-pipeline.md) | Resample, mel spectrograms, Whisper feature contract |
| [`03-video-pipeline.md`](03-video-pipeline.md) | Frame sampling, decode costs, keyframes vs uniform |
| [`04-preprocessing-determinism.md`](04-preprocessing-determinism.md) | Seeded augs, validation-by-eye, byte-level reproducibility |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-image-pipeline.md` — the template all other pipelines copy.
2. `02-audio-pipeline.md` — the modality where "close enough" breaks models.
3. `03-video-pipeline.md` — sampling as a first-class pipeline decision.
4. `04-preprocessing-determinism.md` — the shared checklist for all three.

## Prerequisites

- [`../01-multimodal-ai-landscape/`](../01-multimodal-ai-landscape/) —
  representation levels and manifest conventions.
- Week 02 conventions for `transformers` processors.
