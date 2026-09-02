# 02 — Encoding Audio & Video

> Week 8 index: [README.md](README.md)

**Session 1 topics:** *Overview of audio and video encoding techniques (Spectrograms, Recurrent Neural Networks, 3D CNNs).*

---

## What you'll learn

- The waveform → spectrogram pipeline, with the math demystified
- Mel scaling and log compression — why every audio model uses them
- Raw-audio encoders (wav2vec 2.0/HuBERT) vs spectrogram CNNs
- RNNs as sequence encoders — the pre-transformer standard, and their limitation
- Video encoding: frame-based pipelines, 3D CNNs, and temporal modeling

## 1. Audio: from pressure to an image

Audio is a 1-D continuous signal (air pressure over time). Models read it as a 2-D *image*: time × frequency.

### Spectrogram (STFT)

The Short-Time Fourier Transform chops audio into windows and FFTs each — a frequency breakdown per time slice:

```
frames:  audio[n] × window → FFT → |magnitude|²   → columns of the spectrogram
n_fft = 400 (25 ms @ 16 kHz), hop = 160 (10 ms) — the classic frame settings
```

### Mel + log — the model-facing view

```python
import librosa
import numpy as np

wav, sr = librosa.load("speech.wav", sr=16000, mono=True)     # W7-02's resample rule

mel = librosa.feature.melspectrogram(y=wav, sr=sr, n_fft=400, hop_length=160, n_mels=80)
log_mel = np.log(mel + 1e-6)                                   # compress dynamic range
print(log_mel.shape)                                           # (80, T) — a 1-channel image
```

- **Mel scale** — 80–128 triangular filters spaced like human frequency perception (linear at low Hz, log at high)
- **log** — sound loudness is logarithmic; without it, loud moments swamp everything
- These exact 80-mel log features are **Whisper's input** (W2-04) — you now know what goes into that `WhisperFeatureExtractor`

### Two encoder families

| Family | Input | Examples | Notes |
|---|---|---|---|
| Spectrogram CNNs | log-mel "images" | Whisper encoder, AST | reuse the image toolbox (file 01) |
| Raw-waveform | samples | wav2vec 2.0, HuBERT | conv feature extractor learns its own filterbank |

```python
from transformers import AutoProcessor, AutoModel

proc = AutoProcessor.from_pretrained("facebook/wav2vec2-base")
enc = AutoModel.from_pretrained("facebook/wav2vec2-base")
inputs = proc(wav, sampling_rate=16000, return_tensors="pt")
out = enc(**inputs)
print(out.last_hidden_state.shape)     # (1, T', 768) — one embedding per ~20ms frame
```

Frame-level outputs matter: speaker diarization, sound-event detection, and audio retrieval (Week 9) pool them differently.

## 2. RNNs — sequence encoding before attention

Recurrent networks process tokens one at a time, carrying a hidden state — the pre-2017 sequence standard, and the "before" picture that makes attention's value concrete:

```python
rnn = nn.LSTM(input_size=64, hidden_size=128, batch_first=True)
out, (h_n, c_n) = rnn(torch.randn(1, 50, 64))
print(out.shape, h_n.shape)            # (1, 50, 128) per-step | (1, 1, 128) final state
```

- LSTM/GRU gates let gradients survive many steps (vs vanilla RNN's vanishing gradients, W3-03)
- Still reasonable for streaming/low-latency edge audio; **but**: strictly sequential (no parallelism) and long-range information decays — the two failures attention fixed (W3-04)
- In 2026 you'll meet RNNs mainly as history: know the shape, skip the depth

## 3. Video encoding — images + time

Three strategies, in increasing sophistication:

### a. Frame-based (the default for RAG)

Sample N frames (W7-02), encode each with a 2D encoder, pool temporally:

```python
frame_embs = vit(frame_batch).pooler_output        # (N, 768)
video_emb = frame_embs.mean(0)                      # (768,) — mean-pool over time
```

Cheap and good for *what's in the video*; blind to motion/order (fine for catalog/search, bad for actions).

### b. 3D CNNs — convolving over time too

3D kernels (e.g., 3×3×3) slide over height, width **and time** — learning motion features directly (C3D/I3D lineage). Cost grows with temporal depth; used as action-recognition backbones. PyTorch: `nn.Conv3d(3, 64, kernel_size=(3,3,3))` — same math, one extra axis.

### c. Video transformers (ViViT-class)

Frames → patch tokens → **spatio-temporal attention** (tubelet embedding: spatio-temporal patches as tokens) — the ViT recipe extended with a time axis; token counts explode (196 × frames), hence aggressive frame sampling/tubelet pooling.

## 4. Choosing encoders for Week 9 (the practical table)

| Asset | Encoder | Output |
|---|---|---|
| Images (products, slides) | CLIP image encoder (W2-04) | 512-d, text-aligned |
| Diagrams/scanned docs | CLIP or Donut/OCR+text | per use case |
| Audio (calls, meetings) | Whisper ASR → **text pipeline**; or wav2vec2 embeddings | text / 768-d |
| Video | keyframes → CLIP per frame (temporal pool) | 512-d per keyframe |

The Whisper observation is the workhorse: **ASR converts audio into the text modality you already retrieve well** (Week 9 pattern 1). Raw audio embeddings only when tone/speaker/non-speech matters.

## Exercises

1. Spectrogram detective: generate a 440 Hz sine, 1 kHz sine, and white noise (numpy); plot the three log-mel spectrograms. Explain each pattern via the STFT.
2. Hop-length sweep: same audio at hop 160 vs 640 — how do time resolution and T change? What's the trade?
3. wav2vec2 vs Whisper: embed the same clip both ways; check shapes. Which gives one vector per utterance vs per frame, and what would you pool for retrieval?
4. RNN vanishing demo: train the W3-03 sine-fitter with a vanilla `nn.RNN` over a 200-step sequence vs the LSTM. Compare loss curves.
5. Video budget: 8 keyframes of 224×224 through CLIP — token/cost math vs one 3D-CNN pass over 16 frames. When is frame-pooling the right call?

## Pitfalls

- **Silence isn't empty** — trim leading/trailing silence (VAD) or embeddings encode "microphone hum"
- **Mixed sample rates across a corpus** — resample once at ingest, record `sr` in metadata (W7-01)
- **Stereo flattened wrong** — mono conversion averages channels; phase-critical audio needs care
- **Frame sampling destroying temporal labels** — action/event questions need ordered frames, not a mean-pool
- **RNN nostalgia in production** — transformers/SSMs have replaced them for encoding; don't build new sequence encoders on vanilla RNNs

## Resources

- librosa [spectrogram docs](https://librosa.org/doc/latest/generated/librosa.feature.melspectrogram.html) + the "mel scale" explainer in its tutorial gallery
- Whisper paper §2 (log-mel input spec — now readable end to end)
- Baevski et al., *wav2vec 2.0* (raw-audio SSL, skim §1) · Hsu et al., *HuBERT*
- Christopher Olah, *Understanding LSTM Networks* — the classic gating visualization
- ViViT paper (Arnab et al., 2021) — video tokenization, §3.1
