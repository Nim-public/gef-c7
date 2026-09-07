# Raw-Audio Encoders — wav2vec2 / HuBERT Frame Embeddings

**What you'll learn:** encoders that skip the spectrogram entirely, what
their frame-level embeddings buy for retrieval, and the masking objective
that trained them.

## 1. The frontend difference

```python
from transformers import Wav2Vec2Model, Wav2Vec2FeatureExtractor
import torch, librosa

fx = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base")
mdl = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")

x, _ = librosa.load("data/raw/audio/meeting01.wav", sr=16_000, mono=True)
inputs = fx(x[: 30 * 16_000], sampling_rate=16_000, return_tensors="pt")
with torch.no_grad():
    out = mdl(**inputs)
h = out.last_hidden_state                     # (1, 1499, 768) frame embeddings
print(h.shape)                                # 30 s × ~50 Hz frame rate
```

| Stage | Spectrogram models (Whisper) | Raw-waveform (wav2vec2) |
|---|---|---|
| Input | log-mel (80×3000) | float32 PCM (480k samples) |
| Frontend | fixed mel filterbank | learned conv stack (7-conv) |
| Frame rate | 100/s | ~50/s (stride 320) |
| Pretraining | ASR supervision | self-supervised masking |

The conv frontend learns its own filterbank — including bands a fixed mel
prior might waste. The cost: no human-readable spectrogram for your lab
ritual; the benefit: features tuned to speech statistics, not to hearing.

## 2. Masking pretraining, in one picture

```text
wave ──▶ conv ──▶ [z_1 ... z_T] ──(mask 25–50%)──▶ transformer ──▶ predict masked z's
                       │
                       └─ quantized targets (wav2vec2) / cluster targets (HuBERT)
```

wav2vec2 masks latent features and predicts *quantized* targets (Gumbel-
softmax codebook); HuBERT masks and predicts *cluster ids* of unmasked
features (like BERT's tokens, discovered not given). Both produce a stack
whose hidden states encode phonetic content at every frame — the property
retrieval exploits.

## 3. Frame embeddings for retrieval: the pooling decision

Frame-level vectors (1499×768 for 30 s) are too many to index; the pooling
choice defines your audio unit:

| Pooling | Vector | Good for | Loses |
|---|---|---|---|
| mean over time | 768 | "what was said overall" | when it was said |
| max over time | 768 | keyword-ish salience | context |
| windowed mean (e.g., 10 s) | 3×768 | coarse localization | precision |
| none (index frames) | 1499×768 | exact moment retrieval | 1500× index cost |

For the capstone: mean-pool per 30 s unit for the *audio* index, and let
ASR (Week-09) carry localization — the same division of labor as
[`../../Week-07-Multimodal-AI-Building-the-Foundation/01-multimodal-ai-landscape/04-the-modality-gap.md`](../../Week-07-Multimodal-AI-Building-the-Foundation/01-multimodal-ai-landscape/04-the-modality-gap.md)
prescribed.

## 4. Fine-tune-free usage and its limits

Frozen wav2vec2 embeddings retrieve *speech content* queries ("the part
where they discuss budget") reasonably and *paralinguistic* queries ("the
angry moment") poorly — self-supervised speech features are phone-oriented.
CLAP (contrastive audio-text) inverts this: great for sound events, weak on
content. The capstone audio stack is therefore often **both**: wav2vec2/HuBERT
for content-adjacent retrieval + ASR text doing the heavy lifting.

## Exercises

1. Frame-rate check: encode a known 30 s clip; confirm ~1499 frames and
   derive the stride (480000/1499 ≈ 320 samples).
2. Pooling ablation: mean vs max pooling on 10 clips; rank retrieval against
   5 hand-written content queries; report which pooling wins and by how much.
3. Layer choice: extract hidden states from layers 4, 8, 12; for each, run
   the same 10-query retrieval; report which layer best matches your queries
   (mid layers often beat the last for non-ASR tasks).

## Pitfalls

- Feeding int16 audio (or non-normalized floats) — wav2vec2 expects zero-mean unit-variance-ish floats; the feature extractor normalizes, raw numpy does not.
- Mean-pooling *with padding* — batch padding leaks into embeddings; mask-aware pool or fixed-length windows.
- Expecting semantic (word-level) similarity from acoustic embeddings — they encode sounds and phones; semantics arrive via ASR text.

## Resources

- Baevski et al. 2020 (wav2vec 2.0) §2–3; Hsu et al. 2021 (HuBERT).
- HF `Wav2Vec2Model` docs — hidden-state access, layer outputs.
