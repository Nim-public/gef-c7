# Video Pipeline — Frame Sampling, Decode Costs, Keyframes

**What you'll learn:** turn a video file into a defensible set of frames:
sampling strategies with measured decode costs, keyframe detection, and the
storage decision the parent file deferred.

## 1. The sampling decision matrix

| Strategy | What | Cost | Best for |
|---|---|---|---|
| Uniform | every Nth frame | cheapest | static slide-deck videos |
| Keyframe (I-frames) | codec scene anchors | cheap (index scan) | cuts, scene changes |
| Scene-detect | threshold on frame diff | medium (full decode) | lectures with transitions |
| Dense + pool later | decode all, sample in model | expensive | when unsure — pilot only |

For the capstone, **uniform + scene-detect hybrid**: uniform 12 frames for
coverage, scene-detect to add frames at slide changes. Deterministic,
documented, and cheap.

## 2. Decode costs, measured (the numbers that kill naive pipelines)

Measured on a 30 min 1080p 24 fps MP4 (43,200 frames), CPU decode:

| Approach | Frames touched | Wall time | Notes |
|---|---|---|---|
| `imageio` sequential read of all | 43,200 | ~9 min | full decode |
| `pyav` seek to 12 uniform PTS | 12 | ~4 s | seeks dominate |
| Keyframe index scan only | 0 decoded | ~1 s | metadata read |
| Scene-detect pass | 43,200 | ~10 min | full decode again |

Two lessons: **seek, don't read**, and run scene-detect once during ingest,
never at query time. Store the sampled frame paths in the manifest so
query-time cost is zero.

```python
import av, numpy as np, json
from pathlib import Path

def uniform_frames(path: str, n: int = 12, out_dir: Path | None = None):
    """Sample n frames at evenly spaced timestamps; optionally persist them."""
    with av.open(path) as container:
        dur = container.duration / av.time_base            # seconds (float)
        stream = container.streams.video[0]
        pts_ts = []
        frames = []
        for i in range(n):
            ts = dur * (i + 0.5) / n
            container.seek(int(ts / stream.time_base), stream=stream,
                           any_frame=False, backward=True)
            for frame in container.decode(stream):
                frames.append((ts, frame.to_image()))
                break                                       # first frame after seek
        for j, (ts, img) in enumerate(frames):
            if out_dir:
                out = out_dir / f"f{j:04d}.jpg"
                img.save(out, quality=90)
        return [{"t": round(ts, 2), "frame_idx": j} for j, (ts, _) in enumerate(frames)]
```

Persist the sampling record (`data/manifests/video-samples.json`) — the
*provenance of the sampling* is as important as the frames: which `n`, which
offset rule, which decode library version.

## 3. Keyframes: read the codec's opinion for free

```python
def keyframe_timestamps(path: str) -> list[float]:
    """I-frame positions: the codec already decided where scene changes are."""
    kfs = []
    with av.open(path) as container:
        for frame in container.decode(video=0):
            if frame.key_frame:
                kfs.append(float(frame.pts * frame.time_base))
    return kfs
```

I-frames cluster at cuts and slide changes because encoders spend keyframes
there. For slide decks, `keyframe_timestamps` is embarrassingly effective —
one I-frame per slide transition is common. Compare its output with
PySceneDetect on a 5 min clip; you will usually keep the free version.

## 4. Audio must survive the video pipeline

The classic miss: sampling frames for CLIP and throwing away the audio track.
For the capstone, the *speech* (ASR, Week 08) carries more retrievable
semantics than any 12 frames. Extract it during ingest:

```python
def extract_audio_track(path: str, out_wav: str) -> float:
    import av, soundfile as sf
    with av.open(path) as container:
        astream = container.streams.audio[0]
        chunks = []
        for frame in container.decode(astream):
            arr = frame.to_ndarray()                    # (channels, samples)
            chunks.append(arr.T if arr.shape[0] < 4 else arr.T)
        x = np.concatenate(chunks).astype("float32")
        if x.ndim > 1:
            x = x.mean(axis=1)
        sf.write(out_wav, x, int(astream.rate), subtype="PCM_16")
        return len(x) / astream.rate                    # duration seconds
```

(Resample to 16 kHz afterwards with §2 of the audio pipeline file.)

## Exercises

1. Benchmark the four sampling strategies on a real 10 min video: frames
   touched, wall time, and JPEG bytes written. Plot a bar chart and annotate
   the *surprise* (seek speed vs index scan).
2. Slide-deck drill: run uniform-12 and keyframe detection on a lecture
   video. For each strategy, count how many distinct slides appear in the
   sample. Which missed slides, and what parameter fixes it?
3. Write `sample_with_audio(path)` that returns frames *and* the 16 kHz mono
   audio array, asserting duration agreement within 0.5 s between container
   metadata and decoded audio length.

## Pitfalls

- `container.duration` in `av.time_base` units (microseconds), not seconds — the classic off-by-a-million bug.
- Seeking without `backward=True` — lands before the nearest keyframe and decodes from there (or fails).
- Saving frames as PNG "for quality" — 10× the bytes of JPEG q90 with no retrieval benefit; quality only matters for OCR (use q95+ there).

## Resources

- PyAV examples: seeking and decoding (`av.open`, `container.seek`).
- PySceneDetect `ContentDetector` — threshold-based scene detection reference.
