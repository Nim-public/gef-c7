# DataLoader Tuning — Workers, Pinning, Prefetch, Batch Shapes

**What you'll learn:** tune a multimodal DataLoader with measurements, not
folklore: where the bottleneck actually is, which knobs move it, and the
batch-shape math for encoders.

## 1. Find the bottleneck first (60-second profile)

```python
import time
from torch.utils.data import DataLoader

def profile_loader(ds, collate, workers: int, n: int = 64) -> float:
    dl = DataLoader(ds, batch_size=8, collate_fn=collate, num_workers=workers)
    it = iter(dl); next(it)                       # warm-up (spawns workers)
    t0 = time.perf_counter()
    for i, _ in enumerate(it):
        if i >= n // 8:
            break
    return (time.perf_counter() - t0) / (n // 8)  # s/batch
```

| Reading | Bottleneck | First knob |
|---|---|---|
| Slow with workers=0, same with 8 | CPU transform inside `__getitem__` | vectorize transform, cache processed level |
| Fast at 0, slower at 8 | worker spawn/IPC overhead on tiny items | batch up items, fewer workers |
| Fast alone, stalls with GPU encode | transfer + encode serialization | `pin_memory` + `non_blocking`, prefetch |
| Memory grows until OOM | worker holding decoded refs | drop PIL/ndarray refs after return |

## 2. The knobs, in order of payoff

1. **`num_workers`** — start at physical cores − 2; more workers on
   IO-bound image decode, fewer on RAM-bound audio decode. Windows spawns
   (not forks): worker startup is seconds, so profile *after* warm-up.
2. **`pin_memory=True`** — page-locked host memory for async H2D copy; pair
   with `tensor.to("cuda", non_blocking=True)` in the loop.
3. **`persistent_workers=True`** — keeps workers alive between epochs;
   with Windows spawn this is not optional if you iterate repeatedly.
4. **`prefetch_factor`** — batches queued per worker; 2 is fine, 8 hides
   transform latency spikes at the cost of RAM.
5. **`batch_size`** — see §3; it is a *shape* decision before a speed one.

## 3. Batch shapes for encoders (the math that matters)

| Encoder | Per-unit shape | Batch of B | RAM (fp32) |
|---|---|---|---|
| CLIP ViT-B/32 | 3×224×224 | B×3×224×224 | B × 0.6 MB |
| MiniLM-L6 (text, 128 tok) | 128 ids | B×128 | negligible |
| Whisper base features | 80×3000 | B×80×3000 | B × 0.96 MB |
| Video: 12 frames | 12×3×224×224 | B×12×3×224×224 | B × 7.2 MB |

Video batches are 12× image batches per unit — B=32 video means 384 image
equivalents. Two legitimate responses: micro-batch the frames (encode 4
frames per forward, pool after), or drop to fp16. Do not "just increase
workers" — the bottleneck is the accelerator, and workers will only queue.

```python
# Micro-batching frames inside __getitem__/collate for video:
def video_to_microbatches(frames, micro_bs: int = 4):
    for i in range(0, len(frames), micro_bs):
        yield frames[i:i + micro_bs]      # encoder loops over these; pool after
```

## 4. Mixed modality batches: three honest options

1. **Homogeneous batches** — batch per modality (sampler groups by
   `modality`). Simplest; each encoder gets uniform shapes.
2. **Dict-of-tensors batches** — one batch contains all modalities;
   collate builds per-modality tensors; loop encodes each. Slower (small
   sub-batches) but preserves global shuffling.
3. **Two-pass encoding** — pass 1: encode all images; pass 2: all text.
   Cheapest; use when the dataset is static (indexing, not training).

For capstone indexing, option 3 is correct: your corpus is static and
throughput wins. Option 1 is for eval loops; option 2 for joint training
experiments only.

## 5. The tuning table, pre-computed

Starting points measured on a 6-core laptop, CPU-only encode (adjust, then
commit your numbers):

| Workload | workers | batch | pin | prefetch | notes |
|---|---|---|---|---|---|
| CLIP image encode, JPEGs | 4 | 32 | no (CPU) | 2 | decode-bound |
| MiniLM text encode | 2 | 256 | no | 2 | tokenizer-bound |
| Whisper 30 s windows | 2 | 8 | no | 2 | STFT is the cost |
| Video 12-frame samples | 4 | 4 | no | 2 | seek + decode |
| GPU encode (any) | 4 | GPU-max/2 | yes | 2 | overlap copy & compute |

## Exercises

1. Run `profile_loader` for workers ∈ {0, 2, 4, 8} on your image Dataset;
   plot s/batch and explain the shape of the curve (spawn cost floor).
2. Measure the fp16 speedup on CLIP encode: same batches, `model.half()`;
   record embedding max-abs drift vs fp32 (expect <1e-2) and decide if it is
   acceptable for retrieval (it usually is).
3. Implement two-pass encoding over your manifest; compare wall time vs the
   homogeneous-batch approach at workers=4.

## Pitfalls

- Tuning workers while the GPU encode loop is synchronous — overlap first (`non_blocking`), tune second.
- `num_workers > 0` on Windows without `if __name__ == "__main__":` guard — recursive spawn error on notebook-less scripts.
- Measuring with `len(dl)` includes partial last batch — exclude it from throughput math.

## Resources

- PyTorch DataLoader docs (all knobs) and the "single vs multi-process" notes.
- FAISS indexing notes — why encode once, index once, then serve.
