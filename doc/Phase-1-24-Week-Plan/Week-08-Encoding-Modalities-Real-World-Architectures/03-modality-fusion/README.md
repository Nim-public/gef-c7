# Deep-Dive: Modality Fusion

Parent overview: [`../03-modality-fusion.md`](../03-modality-fusion.md)

Fusion is *where* modalities meet, and the choice is architectural. This
subfolder implements all three meeting points on small runnable systems,
stress-tests each with missing-modality ablations, and ends with the LLaVA
projection pattern — the fusion your RAG stack will actually use.

## File map

| File | What it covers |
|---|---|
| [`01-early-fusion.md`](01-early-fusion.md) | Concat classifiers, ablations, when early fusion wins |
| [`02-intermediate-fusion.md`](02-intermediate-fusion.md) | Cross-attention mechanics, maps, KV/Q framing |
| [`03-late-fusion.md`](03-late-fusion.md) | Ensembles, calibration, graceful degradation |
| [`04-llava-projection.md`](04-llava-projection.md) | Vision tokens into LLM context — the projection pattern |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-early-fusion.md` — the baseline everyone forgets to beat.
2. `02-intermediate-fusion.md` — the mechanism inside every VLM.
3. `03-late-fusion.md` — the deployment-safe default.
4. `04-llava-projection.md` — modern multimodal LLM input, in code.

## Prerequisites

- [`../01-encoding-text-images/`](../01-encoding-text-images/) — the encoders being fused.
- [`../02-encoding-audio-video/03-rnn-sequence-encoding.md`](../02-encoding-audio-video/03-rnn-sequence-encoding.md)
  — sequence context for cross-attention.
