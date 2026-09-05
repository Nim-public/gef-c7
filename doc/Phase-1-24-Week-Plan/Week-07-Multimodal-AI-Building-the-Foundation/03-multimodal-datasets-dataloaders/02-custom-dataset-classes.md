# Custom Dataset Classes — Lazy Decode, Dict Returns, Collate Functions

**What you'll learn:** Dataset patterns that survive real corpora: lazy
decoding, dict returns, and `collate_fn` for the variable-length reality of
multimodal batches — plus the four classic traps.

## 1. The skeleton every modality shares

```python
from torch.utils.data import Dataset

class MultimodalUnits(Dataset):
    """One unit per row of the manifest; returns processor-ready dicts."""

    def __init__(self, manifest, settings, transform):
        self.df = manifest.reset_index(drop=True)
        self.settings = settings
        self.transform = transform          # modality-aware callable

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, i: int) -> dict:
        row = self.df.iloc[i]
        payload = self.transform(row)       # decode + preprocess (lazy!)
        return {"unit_id": row.unit_id, "modality": row.modality, **payload}
```

Three non-negotiables visible in this skeleton:

1. **Lazy decode** — nothing is opened until `__getitem__`; opening in
   `__init__` multiplies memory by DataLoader workers.
2. **Dict returns** — with `unit_id` inside. Tensors without identity make
   eval-time debugging impossible (which image was this?).
3. **Manifest-driven** — the Dataset owns *no file discovery logic*; the
   manifest from the landscape subfolder is the single source of rows.

## 2. Modality-aware transform: one interface, three branches

```python
def make_transform(settings):
    image_t = build_image_transform(settings["image"])   # from pipelines file
    audio_t = build_audio_transform(settings["audio"])   # decode→16k→windows
    video_t = build_video_transform(settings["video"])   # sample frames
    table = {"image": image_t, "audio": audio_t, "video": video_t,
             "text": lambda row: {"input_ids": tokenize(row.rel_path)}}
    def transform(row):
        return table[row.modality](row)
    return transform
```

Branching inside the transform (not the Dataset) keeps the Dataset generic
and unit-testable: fake rows in, dicts out, no disk needed for the test.

## 3. Variable lengths: the collate function is your policy

Multimodal batches collide with ragged shapes immediately: 197 patches here,
45 tokens there, 30 s windows of different counts. `collate_fn` is where you
*decide*, explicitly:

```python
import torch

def pad_collate(batch: list[dict]) -> dict:
    # 1) group by key; 2) pad sequences to batch max; 3) build masks.
    out = {"unit_id": [b["unit_id"] for b in batch],
           "modality": [b["modality"] for b in batch]}
    if "pixel_values" in batch[0]:                       # images: stack (same shape)
        out["pixel_values"] = torch.stack([b["pixel_values"] for b in batch])
    if "input_features" in batch[0]:                     # audio: pad time dim
        tmax = max(b["input_features"].shape[-1] for b in batch)
        out["input_features"] = torch.stack([
            torch.nn.functional.pad(b["input_features"], (0, tmax - b["input_features"].shape[-1]))
            for b in batch])
        out["feature_mask"] = torch.tensor([
            [1] * b["input_features"].shape[-1] +
            [0] * (tmax - b["input_features"].shape[-1]) for b in batch])
    if "input_ids" in batch[0]:                          # text: pad token dim
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        enc = tok([b["input_ids"] and b["text"] for b in batch], padding=True,
                  truncation=True, return_tensors="pt")
        out["input_ids"] = enc["input_ids"]
    return out
```

Two policies worth naming in your README: **pad-to-batch-max** (what most
code does) vs **bucket-by-length** (sort by length, batch similar lengths —
less padding compute, needs a length-aware sampler). For encoding-only
workloads, bucketing gives 20–40% throughput for free.

## 4. The four classic traps

| Trap | Symptom | Fix |
|---|---|---|
| File handle per item | "too many open files" at workers>0 | open per `__getitem__`, close immediately (or decode from bytes) |
| Lambda closing over `self.df` row | wrong row in workers | pass indices, index inside; never ship iterators to workers |
| Numpy int keys | `KeyError` on `.iloc[np.int64]` — no, actually works; but *dict* keys break | cast indices to `int` at boundary |
| Heavy work in `__init__` | 8 workers × full decode = 8× RAM | move to `__getitem__` |

The first and last are the same lesson: `__init__` runs once *per worker*;
`__getitem__` runs per item. Put cheap setup (paths, settings) in init and
expensive IO in getitem.

## 5. A test you should always have

```python
def test_dataset_roundtrip():
    ds = MultimodalUnits(manifest.head(8), SETTINGS, make_transform(SETTINGS))
    item = ds[3]
    assert item["unit_id"] == manifest.iloc[3].unit_id
    assert set(item) >= {"unit_id", "modality"}
    batch = pad_collate([ds[i] for i in range(8)])
    assert batch["pixel_values"].shape == (8, 3, 224, 224)
```

If that test passes for each modality, your DataLoader problems are
configuration (workers, prefetch), not structure.

## Exercises

1. Add a `"text"` branch to `make_transform` and extend the roundtrip test
   to a mixed 8-row batch containing all modalities.
2. Implement bucket-by-length batching for text rows; measure throughput vs
   pad-to-batch-max on 1,000 rows (workers=4).
3. Deliberately create trap #1 (hold file handles in `__init__`) and record
   the failure mode and OS limit on your machine (`ulimit -n` / Windows equivalent).

## Pitfalls

- `pin_memory=True` with dict batches — pinning works, but only for tensor values; strings stay in the queue.
- Returning torch tensors from `__getitem__` *and* collating again — double work; pick one layer.
- Worker processes inheriting CUDA context (CUDA init before fork) — crash with cryptic NCCL errors; init CUDA after DataLoader starts, or use `spawn`.

## Resources

- PyTorch `Dataset`/`DataLoader` docs; `worker_init_fn` for per-worker seeding.
- Transformers `DataCollatorWithPadding` as a reference collate implementation.
