# Preprocessing Determinism — Seeded Augs, Validation-by-Eye

**What you'll learn:** make preprocessing reproducible across runs, machines,
and teammates: seeded randomness, canonical parameters, and visual validation
that catches drift before embeddings do.

## 1. Why determinism is a *retrieval* problem

Embeddings are derived data. If preprocessing is nondeterministic, the same
image produces different vectors on re-ingest, your FAISS index and your
manifest disagree, and retrieval quality degrades in ways that look like
"model got worse" but are actually "pixels changed." Determinism is the
precondition for the caching strategy in
[`../01-multimodal-ai-landscape/02-representation-levels.md`](../01-multimodal-ai-landscape/02-representation-levels.md).

## 2. Seeded randomness: three sources, three fixes

```python
import random, numpy as np, torch

def seed_everything(seed: int = 42) -> None:
    random.seed(seed)                       # python's RNG (aug order, shuffles)
    np.random.seed(seed)                    # numpy (noise, crops)
    torch.manual_seed(seed)                 # torch (dropout, init) — CPU
    torch.cuda.manual_seed_all(seed)        # all GPUs — torch
```

| Nondeterminism source | Example | Fix |
|---|---|---|
| Python `random` | random crop order | `random.seed(s)` before pipeline |
| NumPy | Gaussian noise aug | `np.random.seed(s)` or `np.random.default_rng(s)` |
| Torch (GPU) | nondeterministic kernels | `torch.use_deterministic_algorithms(True)` + `CUBLAS_WORKSPACE_CONFIG=:4096:8` |
| Library defaults | `Image.resize` filter changes across versions | pin filter explicitly (see image pipeline) |
| Parallel execution | thread pool ordering in batch encode | sort work before dispatch |

For the capstone, the last row is the sneaky one: multiprocessing workers
return in completion order, so a nondeterministic *merge order* creates a
nondeterministic matrix. Always re-sort results by `unit_id` before writing.

## 3. Canonical parameters: the single source of settings

```python
# data/manifests/preproc-settings.json — committed to git
SETTINGS = {
    "version": 3,
    "image": {"size": 224, "resample": "bicubic", "mean": [0.48145466, 0.4578275, 0.40821073],
              "std": [0.26862954, 0.26130258, 0.27577711], "flatten_bg": "white"},
    "audio": {"target_sr": 16000, "mono": "mean", "trim_db": 40, "window_s": 30},
    "video": {"frames": 12, "strategy": "uniform+keyframes", "jpeg_quality": 90},
}
```

Version bumps are semantic: bump when the *output* changes even if code
reads nicer. The processed-file cache key from the landscape file includes
this whole object — that is what makes stale caches detectable.

## 4. Validation-by-eye: the 5-minute ritual that saves 5 hours

Automated checks prove shapes and ranges; *looking* proves content. Build a
contact sheet once per settings change:

```python
from PIL import Image, ImageDraw
from pathlib import Path

def contact_sheet(paths: list[str], out: str = "reports/preproc-sheet.jpg",
                  cols: int = 5, thumb: int = 224) -> None:
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb, rows * (thumb + 18)), "white")
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        img = Image.open(p).resize((thumb, thumb))
        x, y = (i % cols) * thumb, (i // cols) * (thumb + 18)
        sheet.paste(img, (x, y))
        d.text((x + 4, y + thumb + 2), Path(p).stem[:18], fill="black")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=85)
```

Look for, in order: sideways images (EXIF bug), black squares (alpha
flattening bug), washed-out frames (double normalization), duplicated crops
(sampling bug). For audio, plot three log-Mel spectrograms — floor clipping
appears as flat black bands; resampling aliasing as mirrored high-frequency
energy. Two minutes of looking beats two days of confused ablation.

## 5. The determinism test you can actually run

```python
def assert_deterministic(build_once, sample_paths, seed: int = 42):
    """Run the pipeline twice; outputs must be byte-identical."""
    seed_everything(seed)
    out_a = [build_once(p) for p in sample_paths]
    seed_everything(seed)
    out_b = [build_once(p) for p in sample_paths]
    for a, b in zip(out_a, out_b):
        if hasattr(a, "tobytes"):
            assert np.array_equal(a, b), f"nondeterministic: {a.shape}"
        else:
            assert a == b
```

Run it on 5 units of each modality after any settings change. It catches the
unseeded-aug bug, the unsorted-merge bug, and the changed-default bug in
under a minute.

## Exercises

1. Break and fix: remove `seed_everything` from a pipeline that uses a
   random 10% salt-and-pepper aug; run `assert_deterministic`; then restore
   the seed and confirm it passes.
2. Shuffle test: encode 50 units twice with workers=4 vs workers=1 and
   compare embedding matrices. If they differ, find the unsorted merge.
3. Build the contact sheet for your processed images after the settings
   version bump from 2 → 3, and write three observations of what changed.

## Pitfalls

- Seeding in the wrong process — with multiprocessing, seed *inside* each worker's initializer, not only the parent.
- Determinism checks on CPU only — GPU kernels can still be nondeterministic; the env var matters.
- "Validation by eye" skipped because CI is green — CI checks shapes; only you catch the sideways slide.

## Resources

- PyTorch reproducibility notes (`torch.use_deterministic_algorithms`).
- `np.random.default_rng` (PCG64) — the modern seeded NumPy API.
