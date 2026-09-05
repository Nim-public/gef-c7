# Spectrogram Labs — STFT, Mel, and Log by Hand

**What you'll learn:** compute each stage of the audio→image conversion on
a synthetic signal where you can verify every number, and learn the
parameter set that changes everything.

## 1. STFT on a signal you control

```python
import numpy as np, librosa

sr = 16_000
t = np.arange(2 * sr) / sr                       # 2 seconds
# 440 Hz for 1 s, then 880 Hz — a boundary you can see in the spectrogram
x = np.concatenate([np.sin(2 * np.pi * 440 * t[:sr]),
                    np.sin(2 * np.pi * 880 * t[sr:])]).astype(np.float32)

S = np.abs(librosa.stft(x, n_fft=400, hop_length=160))   # (201, 200)
print(S.shape)   # 201 freq bins × 200 time frames
```

The two parameters and their consequences:

| Parameter | Value here | Meaning | Trade-off |
|---|---|---|---|
| `n_fft` | 400 (25 ms) | frequency resolution: 16000/400 = 40 Hz/bin | bigger → finer freq, blurrier time |
| `hop_length` | 160 (10 ms) | frames per second: 16000/160 = 100 | smaller → more frames, more compute |

Whisper's choice (400/160, 80 mels) is not sacred — it is a resolution/SQLite
cost point. Change `n_fft` to 2048 and speech consonants smear; shrink to
160 and pitch becomes ambiguous.

## 2. Mel scale — the human-frequency compression

```python
mel_fb = librosa.filters.mel(sr=sr, n_fft=400, n_mels=80)
mel = mel_fb @ S                                  # (80, 200): the "image"
```

The mel filterbank is a (80, 201) matrix of triangular filters, linear below
1 kHz, logarithmic above. Verify its shape intuition:

```python
# triangle centers, first few and last few, in Hz
centers = librosa.mel_frequencies(n_mels=80, fmin=0, fmax=8000)
print(centers[:5].round(1), centers[-5:].round(1))
# [ 31.6  104.  176.  248.  320.8] [7040. 7280. 7520. 7760. 8000.]
```

Linear spacing (~72 Hz) at the bottom, ~240 Hz at the top: speech formants
live in the dense region, which is why the mel scale *is* the right prior.

## 3. Log — because loudness is logarithmic

```python
log_mel = np.log10(np.maximum(mel, 1e-10))
```

Without the log, a +20 dB shout dominates everything and a whisper
disappears — speech information lives in *ratios*. This single line is why
models trained on linear-power spectrograms underperform: not taste,
information geometry.

## 4. Reading your own audio

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
img = librosa.display.specshow(log_mel, sr=sr, hop_length=160,
                               x_axis="time", y_axis="mel", ax=ax)
fig.colorbar(img, ax=ax); fig.savefig("reports/spectrogram-lab.png", dpi=120)
```

The lab ritual: pick 3 clips from `data/raw/audio/` — speech, music, silence
— and note, on the plot: where the energy is, where 16 kHz Nyquist cuts off,
and what a "music bed" looks like (broadband horizontal stripes) versus
speech (formant tracks + pauses). This is the visual grounding for every
audio retrieval decision later.

## Exercises

1. Boundary localization: from `S`, find the frame index where 440→880 Hz;
   compare with the true boundary (1.0 s = frame 100) — off by at most a
   window (400/160 = 2.5 frames of smear).
2. Resolution drill: recompute with `n_fft=2048`, `hop=160`; find the same
   boundary. Write the two frame-smears down and explain them.
3. Mel-drill: compute `mel_fb` row sums for bins 0–5 and 75–79; connect the
   magnitudes to the filter shapes you saw.

## Pitfalls

- Confusing `n_fft` (window) with `hop_length` (frame advance) — they are independent; only their ratio sets frame rate.
- Plotting power instead of log-power — you will "see nothing" and conclude the clip is broken.
- Forgetting `fmax=8000` (Nyquist) when comparing filterbanks across `sr` — the default `fmax=sr/2` silently changes with your sample rate.

## Resources

- librosa STFT/mel docs; `librosa.mel_frequencies` for the scale itself.
- Whisper paper §2 (audio rep) — same parameters, different framing.
