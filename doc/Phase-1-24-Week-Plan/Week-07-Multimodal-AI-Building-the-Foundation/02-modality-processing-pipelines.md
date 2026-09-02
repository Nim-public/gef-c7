# 02 — Modality Processing Pipelines

> Week 7 index: [README.md](README.md)

**Session 1 topics:** *Individual Modality Processing: Text Processing Pipeline, Image Processing Techniques, Audio Processing Methods, Preprocessing Challenges.*

---

## What you'll learn

- A concrete pipeline per modality: load → clean → transform → tensor
- The normalizations models actually expect (and the silent failures when you skip them)
- Video frame handling as an explicit sampling decision
- The preprocessing challenges checklist used for every dataset this month

## 1. Text pipeline (recap — you've done this)

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
ids = tok(clean_text(raw_text), truncation=True, max_length=512)["input_ids"]
```

Clean (W1-02) → normalize (NFKC) → tokenize → truncate. Multimodal-specific notes: captions are short (no chunking), OCR'd text is noisy (§5), and code-switched/mixed-language captions stress single-language tokenizers.

## 2. Image pipeline

```python
from PIL import Image, ImageOps
import numpy as np

IMAGENET_MEAN, IMAGENET_STD = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])

def load_image(path, size=224):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)          # EXIF rotation trap — see §5
    img = img.convert("RGB")                     # kill alpha/palette modes
    img = ImageOps.fit(img, (size, size))        # center-crop-resize
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - IMAGENET_MEAN) / IMAGENET_STD   # normalize with the MODEL's stats
    return arr.transpose(2, 0, 1)                # HWC -> CHW (torch convention)
```

Every step exists because of a failure mode:

| Step | Prevents |
|---|---|
| `exif_transpose` | photos rotated 90° (phone cameras store rotation as metadata) |
| `convert("RGB")` | 4-channel PNGs/16-bit images crashing the model |
| `fit` to fixed size | models demand fixed input; naive resize distorts aspect |
| model-specific mean/std | double-normalization or none — silent quality loss |

Augmentations (train-time only): flip, color jitter, random crop — `torchvision.transforms`. Eval-time: deterministic transforms, always (leakage/debugging).

The alternative that skips all of it: model-specific **processors** (CLIP's `CLIPProcessor`, ViTImageProcessor) — same math, packaged. Use them in Week 8+; know the manual version first (exercise 1).

## 3. Audio pipeline

```python
import librosa
import numpy as np

TARGET_SR = 16000

def load_audio(path, duration_s=30.0):
    wav, sr = librosa.load(path, sr=TARGET_SR, mono=True, duration=duration_s)
    wav = librosa.util.normalize(wav)                     # loudness → comparable scale
    mel = librosa.feature.melspectrogram(
        y=wav, sr=TARGET_SR, n_fft=400, hop_length=160, n_mels=80)
    log_mel = np.log(mel + 1e-6)                          # log compresses dynamic range
    return wav, log_mel                                   # (T,), (80, T')
```

Why each transform:

- **Resample to 16 kHz mono** — every mainstream audio model (Whisper, wav2vec) expects it; mixed sample rates are the audio equivalent of mixed encodings
- **Log-mel spectrogram** — audio is pressure over time; models read *time × frequency* images. The mel scale approximates human frequency perception; `log` tames the loudness range. Shape becomes (n_mels, time) — literally an image, so audio models are often CNNs on spectrograms (file W8-02)
- **Whisper's own features**: 80-mel log-mel, 30-second windows with padding/trim — using its feature extractor (`WhisperFeatureExtractor`) instead of hand-rolling avoids subtle mismatches

Audio traps: stereo→mono silently averaging content, MP3 priming silence, variable `sr` across a corpus, clipping (normalize), non-speech noise dominating mel energy.

## 4. Video pipeline

Video = images + time. The central decision is **frame sampling**:

```python
import cv2

def sample_frames(path, n_frames=8):
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idxs = np.linspace(0, total - 1, n_frames, dtype=int)     # uniform sampling
    frames = []
    for i, idx in enumerate(idxs):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok:
            frames.append(load_image_array(frame))            # reuse §2 (BGR→RGB!)
    cap.release()
    return frames                                             # (n_frames, 3, H, W)
```

- **Uniform sampling**: cheap, covers the clip, misses brief events
- **Keyframe/shot detection**: scene-change based; better content coverage, more compute
- **Dense (every frame)**: only offline; storage and compute explode (§3 table, W7-01)
- Remember OpenCV is **BGR** — the classic silent bug when mixing with PIL pipelines

## 5. Preprocessing challenges (the shared checklist)

| Challenge | Text | Image | Audio | Video |
|---|---|---|---|---|
| **Scale variance** | lengths | resolutions | loudness | resolutions/fps |
| **Noise** | OCR/typos | compression, blur | hum, crosstalk | motion blur |
| **Format zoo** | encodings | CMYK/16-bit/EXIF | sr/codec/container | codecs, variable fps |
| **Missing pieces** | empty fields | corrupt files | silence | dropped frames |
| **Determinism** | easy ✓ | transforms must be seeded | resamplers differ | decoder version differences |

Two rules that save weeks: **(1) deterministic preprocessing for evaluation** (same input → same tensor, always — no random augs at eval), and **(2) validate post-preprocessing, visually** — save a few processed tensors back to images/spectrograms and *look* at them. Most "the model is bad" moments this month are preprocessing bugs.

## Exercises

1. Implement `load_image` above, then verify against `CLIPProcessor` on the same file: run both through CLIP (W2-04) and compare embedding cosine (>0.999 = your pipeline is equivalent).
2. Audio: load one WAV at its native sr and at 16k; plot both waveforms + mel spectrograms. Explain the difference with the sampling theorem in one sentence.
3. Video: sample 8 frames from any mp4 three ways (uniform, 25%, 50% start-offset). What content does each miss?
4. Preprocessing audit: run your whole Week-4 corpus of images through `image_record()` (file 01) — report the format zoo you find (modes, sizes, EXIF rotations).
5. Determinism test: process the same file twice with and without augmentation; assert equality where it's required.

## Pitfalls

- **EXIF rotation ignored** — a third of phone photos in any scraped set are stored rotated
- **BGR vs RGB mixing** — OpenCV reads BGR; PIL expects RGB; models trained on one fail *subtly* on the other
- **Double normalization** — processor already normalizes; your manual pass stacks a second mean/std
- **Resampling without anti-aliasing** — aliasing injects fake frequencies into spectrograms
- **Fixing preprocessing after eval** — if preprocessing changes, embeddings change → re-index everything (Week 9 consequence; write preprocessing versions into metadata)

## Resources

- torchvision [transforms docs](https://pytorch.org/vision/stable/transforms.html) + [models](https://pytorch.org/vision/stable/models.html) (preprocessing tables per model)
- librosa [API](https://librosa.org/doc/latest/index.html) and the melspectrogram primer in its examples gallery
- HF [image processing](https://huggingface.co/docs/transformers/preprocessing) & [audio](https://huggingface.co/docs/transformers/tasks/audio_classification) task guides
- OpenCV-Python [video tutorials](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html)
