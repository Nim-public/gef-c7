# Audio Pipeline — Resample, Mel Spectrograms, Whisper Features

**What you'll learn:** why audio pipelines fail silently (sample-rate drift,
wrong normalization), the mel spectrogram as *the* intermediate, and the
exact feature contract Whisper expects.

## 1. The audio pipeline is a contract, not a recipe

Every model downstream consumes audio in one canonical form; your job is to
deliver that form and nothing else. For Whisper:

```text
raw (any rate/codec) → decode to float32 → mono → resample to 16 kHz
→ log-Mel spectrogram: n_fft=400, hop=160, n_mels=80, 30 s windows
```

Break one clause and the model still runs — producing confident garbage.

## 2. Resampling done right

```python
import numpy as np

def to_float32_mono(path: str) -> tuple[np.ndarray, int]:
    """Decode any container to float32 mono. Uses soundfile; falls back gracefully."""
    import soundfile as sf
    data, sr = sf.read(path, dtype="float32", always_2d=True)
    mono = data.mean(axis=1)                     # stereo -> mono by averaging
    return mono, sr

def resample_to_16k(x: np.ndarray, sr: int) -> np.ndarray:
    if sr == 16_000:
        return x
    import scipy.signal as sig
    g = 16_000 / sr
    n_out = int(np.ceil(len(x) * g))
    return sig.resample_poly(x, up=16, down=sr // np.gcd(sr, 16_000))[:n_out]
```

Rules that prevent classic bugs:

- **Decode to float32, never int16.** int16 math overflows on add/mean.
- **Mono by averaging channels** (not first-channel) — voice on the right
  channel is common in interview recordings.
- **Resample with a polyphase filter** (`resample_poly`), not naive linear
  interpolation — naive resample adds aliasing you cannot hear but the model can.

## 3. Mel spectrograms: what the model actually sees

```python
import numpy as np

def log_mel(x: np.ndarray, sr: int = 16_000, n_fft: int = 400,
            hop: int = 160, n_mels: int = 80) -> np.ndarray:
    import scipy.signal as sig
    _, _, S = sig.stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft - hop,
                       window="hann", padded=True)
    S = np.abs(S) ** 2                            # power
    # mel filterbank (simplified; use librosa.filters.mel in practice)
    import librosa
    mel_fb = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_mels)
    mel = mel_fb @ S
    log_spec = np.log10(np.maximum(mel, 1e-10))
    log_spec = np.maximum(log_spec, log_spec.max() - 8.0)   # floor: max-8dB
    return (log_spec + 1.0) / 4.0                 # Whisper's normalization
```

Read the normalization line twice: Whisper clamps the dynamic range to
`max − 8 dB` *of the current clip*, then rescales to ≈[−1, 1]. Consequence:
**normalization is relative**, so a quiet recording and a loud one map to the
same range — good — but a *clip with only silence + one click* gets its click
amplified to full scale. Trim silence before feature extraction.

## 4. The Whisper feature contract via the processor

```python
from transformers import WhisperProcessor
import librosa

proc = WhisperProcessor.from_pretrained("openai/whisper-base")
x, sr = librosa.load("data/raw/audio/meeting01.mp3", sr=16_000, mono=True)
x = x[: 30 * 16_000]                    # exactly 30 s: 480,000 samples
inputs = proc(audio=x, sampling_rate=16_000, return_tensors="pt")
feats = inputs.input_features          # shape (1, 80, 3000)
assert feats.shape[-1] == 3000         # 30 s * 100 frames/s — the contract
```

Shapes are the parity check for audio, mirroring §2 of the image file: if
`input_features` is `(1, 80, 3000)`, your 16 kHz mono pipeline is right;
`(1, 80, 2999)` means a rounding drift in resampling that will pad with
silence and slightly degrade every prediction.

## 5. A practical pipeline function

```python
def prepare_audio(path: str, max_s: float = 30.0) -> np.ndarray:
    x, sr = to_float32_mono(path)
    x = resample_to_16k(x, sr)
    # trim leading/trailing silence at -40 dBFS
    import librosa
    x, _ = librosa.effects.trim(x, top_db=40)
    n_max = int(max_s * 16_000)
    if len(x) > n_max:                        # chunk, don't truncate mid-word
        chunks = [x[i:i + n_max] for i in range(0, len(x) - n_max + 1, n_max)]
    else:
        chunks = [x]
    return chunks                             # list of ≤30 s float32 arrays
```

## Exercises

1. Prove the resample bug: take a 44.1 kHz sine sweep, resample with linear
   interpolation vs `resample_poly`, and compare the spectrograms above
   8 kHz (pre-alias vs post-alias content).
2. Feed Whisper `input_features` of shape `(1, 80, 2999)` — what error or
   behavior do you observe? Then pad and re-run. Record the difference in
   transcripts of the last word.
3. Split a 5-min meeting clip into 30 s windows two ways: hard cut vs
   overlap-by-2 s. Count how many sentence boundaries land inside a cut in
   each scheme (use the transcript timestamps).

## Pitfalls

- `librosa.load` default sr=22050 — the default silently violates the contract; always pass `sr=16_000`.
- Normalizing audio to [-1,1] yourself *before* the processor — double normalization skews the log-Mel floor.
- Treating `.m4a`/`.opus` as "audio" without checking `soundfile` support — install ffmpeg-backed `soundfile` or convert first.

## Resources

- Whisper paper §2 (audio representation) and `feature_extractor_config.json` on the Hub.
- `librosa.effects.trim` and `resample_poly` docs.
