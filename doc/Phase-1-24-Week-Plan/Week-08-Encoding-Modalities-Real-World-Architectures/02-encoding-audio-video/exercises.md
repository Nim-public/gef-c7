# Exercises — Encoding Audio & Video

Expanded set with worked approaches. Audio labs run on any clip in
`data/raw/audio/`; video drills reuse Week 07's sampled frames.

## 1. Spectrogram lab, extended (from 01-spectrogram-labs)

**Task:** build `scripts/spectro_lab.py`: given a clip, output a 2×2 figure
— waveform, linear-power STFT, mel, log-mel — with the 440/880 Hz boundary
frame marked on each panel. Save to `reports/spectrogram-lab.png`.

**Worked approach:** one `librosa.stft` call feeds three panels (linear, mel,
log-mel) — compute once, transform thrice. The boundary marker:
`frame = int(boundary_s * sr / hop)`; draw with `axvline`. The *smear*
visible in the four panels is the parameter lesson made visual.

**Pass criterion:** figure generated from repo-relative paths; boundary
line within ±3 frames of truth on the mel panel.

## 2. Frame-embedding drill (from 02-raw-audio-encoders)

**Task:** encode one clip's frames (wav2vec2-base); compute cosine of frame
0 vs frame T/2 and of frame T/2 vs T/2±1. Interpret: a speech clip should
show low distant-frame similarity and high adjacent-frame similarity.

**Worked approach:**

```python
h = out.last_hidden_state[0]              # (1499, 768), L2-normalize rows first
cos = lambda a, b: float(a @ b)
print(cos(h[0], h[749]), cos(h[749], h[750]))
```

Expect ~0.3–0.6 distant, ~0.9+ adjacent. Silence padding *inflates*
adjacent similarity — trim first (Week 07's audio pipeline).

**Pass criterion:** two cosines reported with the silence caveat checked.

## 3. RNN mechanics check (from 03-rnn-sequence-encoding)

**Task:** with the hand `lstm_step`, drive the cell with constant input and
gates fixed at (`f=0.5, i=0.5`): what is `c_t` after 10 steps, symbolically?
Verify numerically that `c` converges to `g` (the write value) — the
geometric series `c_t = g·Σ 0.5^k`.

**Worked approach:** `c_t = 0.5·c_{t-1} + 0.5·g` → `c_t → g` as t grows.
This *is* the gating insight in one line: gates interpolate between memory
and new content, and the interpolation *rate* is the gate value.

**Pass criterion:** numeric result within 1e-3 of `g` at t=10 (Σ 0.5^k ≈ 0.999).

## 4. Video pooling ablation (from 04-video-encoding)

**Task:** for one 12-frame sample: compute mean/max/concat-linear/temporal-
attention clip vectors; retrieve each against 5 text queries (CLIP text
tower); report R@1 per pooling on your 10-query set.

**Worked approach:** the concat+linear layer must be *trained or frozen at
identity-ish init* — with random init it is a random projection; document
that. Temporal-attention weights `softmax(t @ mean(t))` are self-computed;
note they are a heuristic, not trained attention.

**Pass criterion:** a 4-row results table in `reports/video-pooling.md` with
one interpretation sentence.

## 5. Capstone: audio+video encoder note (from all files)

**Task:** extend the Week 07 encoder decision memo with audio (wav2vec2 vs
CLAP vs ASR-text-only) and video (frame-pool vs temporal) picks, each with
the cost row from this week's tables and a "revisit if" trigger.

**Worked approach:** the audio row must answer the Week-07 inventory's
"sidecar pending" cell — if your pick is ASR-text-only for content, the
audio *embedding* row becomes optional and the settings simplify (one less
encoder to version). Write the consequence down explicitly.

**Pass criterion:** memo updated with two new rows + decisions traceable to
exercises 2–4's numbers.

## Pitfalls recap

- Spectrograms computed at `sr=22050` (librosa default) then fed to 16k models — the silent contract break; load with `sr=16_000` always.
- Pooling over *unnormalized* frame embeddings — mean of unnormalized vectors biases toward high-norm frames; normalize per frame first.
- RNN drills with random gate initialization — gates at 0.5 average are the only interpretable regime; force them before drawing conclusions.
