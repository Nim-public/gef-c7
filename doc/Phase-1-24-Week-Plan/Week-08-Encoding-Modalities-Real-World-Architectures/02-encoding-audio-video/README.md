# Deep-Dive: Encoding Audio & Video

Parent overview: [`../02-encoding-audio-video.md`](../02-encoding-audio-video.md)

This subfolder builds the audio and video encoding stacks with labs you can
run on your own clips: spectrograms computed step by step, raw-waveform
encoders and what their frame embeddings buy you, RNNs as the pre-attention
baseline (and why they lost), and the three video strategies ranked for a
RAG capstone.

## File map

| File | What it covers |
|---|---|
| [`01-spectrogram-labs.md`](01-spectrogram-labs.md) | STFT/mel/log hands-on with librosa, parameters that matter |
| [`02-raw-audio-encoders.md`](02-raw-audio-encoders.md) | wav2vec2/HuBERT frame embeddings, masking pretraining |
| [`03-rnn-sequence-encoding.md`](03-rnn-sequence-encoding.md) | LSTM/GRU mechanics, limits, why attention replaced them |
| [`04-video-encoding.md`](04-video-encoding.md) | Frame pooling, 3D CNNs, tubelet tokens — with costs |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-spectrogram-labs.md` — see what the encoder sees.
2. `02-raw-audio-encoders.md` — the modern audio embedding source.
3. `03-rnn-sequence-encoding.md` — the historical baseline, still everywhere.
4. `04-video-encoding.md` — pick your capstone video strategy.

## Prerequisites

- [`../../Week-07-Multimodal-AI-Building-the-Foundation/02-modality-processing-pipelines/02-audio-pipeline.md`](../../Week-07-Multimodal-AI-Building-the-Foundation/02-modality-processing-pipelines/02-audio-pipeline.md)
  — the 16 kHz mono contract.
- [`../01-encoding-text-images/01-text-encoder-template.md`](../01-encoding-text-images/01-text-encoder-template.md)
  — the four-stage template applied here.
