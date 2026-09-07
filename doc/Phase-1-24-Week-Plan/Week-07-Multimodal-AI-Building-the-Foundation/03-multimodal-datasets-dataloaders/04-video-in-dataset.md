# Video in Dataset — Frame Sampling Inside `__getitem__`

**What you'll learn:** the hard case from the parent file, done properly:
sampling frames inside a Dataset without decode storms, worker explosions,
or nondeterministic samples.

## 1. The three architectures (pick before writing code)

| Architecture | Where decode happens | Pros | Cons |
|---|---|---|---|
| **Pre-sampled** (ingest writes frames to `data/processed/video-keyframes/`) | once, offline | `__getitem__` reads JPEGs: fast, deterministic | storage 12×~100 KB/clip |
| **Decode-in-getitem** (seek each time) | per access | zero storage | 3–8 s/video access; brutal on workers |
| **Hybrid** (decode once in worker cache, keep LRU) | first access | warm reuse within a run | memory-tuning, eviction bugs |

For the capstone: **pre-sampled**. You sample once during ingest (video
pipeline file), store provenance in the manifest, and the Dataset becomes a
boring image Dataset — which is exactly what you want during evaluation.

## 2. Pre-sampled Dataset, full implementation

```python
from pathlib import Path
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset

class VideoFrameDataset(Dataset):
    """Rows = sampled clips; each item returns N frames as one tensor."""

    def __init__(self, manifest: pd.DataFrame, frames_root: str, n_expected: int = 12):
        self.df = manifest[manifest.modality == "video"].reset_index(drop=True)
        self.frames_root = Path(frames_root)
        self.n_expected = n_expected

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, i: int) -> dict:
        row = self.df.iloc[i]
        clip_dir = self.frames_root / row.unit_id
        # Frames were written at ingest: f0000.jpg ... f0011.jpg
        frame_paths = sorted(clip_dir.glob("f*.jpg"))
        if len(frame_paths) != self.n_expected:
            raise RuntimeError(
                f"{row.unit_id}: expected {self.n_expected} frames, "
                f"found {len(frame_paths)} — reprocess")
        import torch, numpy as np
        arrs = [np.asarray(Image.open(p).convert("RGB"), dtype=np.float32) / 255.0
                for p in frame_paths]
        return {"unit_id": row.unit_id,
                "pixel_values": torch.tensor(np.stack(arrs)).permute(0, 3, 1, 2)}
                # shape: (12, 3, 224, 224)
```

The length check is the whole point of pre-sampling: ingest bugs surface as
loud `RuntimeError`s at Dataset-build time, not as silently shifted frames
at eval time.

## 3. Deterministic decode-in-getitem (when you must)

```python
import av

def uniform_sample_decode(path: str, n: int = 12, size: int = 224) -> list:
    """Seek-based sampling: deterministic, no full decode."""
    with av.open(path) as container:
        dur = container.duration / av.time_base
        stream = container.streams.video[0]
        out = []
        for i in range(n):
            ts = dur * (i + 0.5) / n
            container.seek(int(ts / stream.time_base), stream=stream, backward=True)
            for frame in container.decode(stream):
                img = frame.to_image().resize((size, size), Image.BICUBIC)
                out.append(img)
                break
    return out
```

Rules if you go this route:

- **One decode per item max.** Two workers × 12 seeks × 30 fps decode is how
  "training ran at 2 it/s" happens.
- **The seek rule is part of the contract**: `(i + 0.5) / n` offsets. Change
  it and every embedding you ever built is stale. It belongs in
  `preproc-settings.json`, not in a function body.
- Cap workers at 2 for video Datasets; seek-heavy decode does not scale with
  workers (disk seek contention), it just multiplies IO pressure.

## 4. Temporal metadata must ride along

A frame tensor without timestamps is a bag of pixels. Every item should also
return the sampled timestamps so evaluation (Week 12) can ask "was the
retrieved frame *near* the ground-truth moment?":

```python
# ingest writes the sampling record once:
record = {"unit_id": uid, "frames": [{"t": 1.25, "file": "f0000.jpg"}, ...]}
# Dataset returns it unchanged:
item["frame_times"] = torch.tensor([f["t"] for f in record["frames"]])
```

Load the record parquet in `__init__` (cheap: it is metadata), index it in
`__getitem__` (fast), and never recompute times at access.

## 5. The failure drills

| Drill | Expected failure | Lesson |
|---|---|---|
| Delete f0007.jpg from one clip | loud `RuntimeError` at access | length check works |
| Change sampling rule to `(i + 0) / n` | silent embedding drift vs old matrix | sampling rule is contract |
| Set workers=8 on decode-in-getitem | wall time *worse*, disk saturates | seek contention |
| Drop `frame_times` from items | eval cannot compute temporal metrics | metadata rides along |

## Exercises

1. Build `VideoFrameDataset` over 5 pre-sampled clips and the roundtrip test:
   shapes `(12, 3, 224, 224)`, `unit_id` match, `frame_times` present.
2. Implement decode-in-getitem for the same 5 clips; measure s/item for
   workers ∈ {0, 2, 4}; explain the non-monotonic result.
3. Simulate the drift drill: encode one clip with both sampling rules and
   report the cosine distance between the two mean-pooled embeddings.

## Pitfalls

- `sorted(glob("f*.jpg"))` lexicographic sort breaks at frame 10000 (f1000 < f999) — zero-pad filenames at ingest (`f%04d`).
- Assuming `container.duration` exists for all containers (live segments, some MKVs) — fall back to decoded-audio length or last PTS.
- PIL decode inside the seek loop for *all* frames instead of the first — you wanted one frame after seek, not the keyframe neighborhood.

## Resources

- PyAV seek semantics (`backward`, `any_frame`) and `frame.pts`/`time_base`.
- Your own `../02-modality-processing-pipelines/03-video-pipeline.md` — this file assumes its ingest step ran.
