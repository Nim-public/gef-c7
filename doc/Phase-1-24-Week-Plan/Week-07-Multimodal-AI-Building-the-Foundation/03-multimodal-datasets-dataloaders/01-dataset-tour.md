# Dataset Tour — COCO, Flickr30k, VQA, AudioCaps, Video Sets on the Hub

**What you'll learn:** the reference datasets for each modality pair, how to
load each one with current `datasets` calls, and the gotcha that each hides.

## 1. The tour table

| Dataset | Modality pair | Unit | Size | License | Hub id (examples) |
|---|---|---|---|---|---|
| COCO Captions | image↔text | image + 5 captions | 330k images | CC-BY-4.0 | `HuggingFaceM4/COCO` |
| Flickr30k | image↔text | image + 5 captions | 31k images | commercial-restricted | `nlphuji/flickr30k` |
| VQA v2 | image+text→text | image + question | 1.1M Qs | CC-BY-4.0 | `HuggingFaceM4/VQAv2` |
| AudioCaps | audio↔text | 10 s clip + caption | ~51k clips | CC-BY-4.0 | ` Confederation/AudioCaps` mirrors vary |
| MSR-VTT | video↔text | clip + caption | 10k clips | research-only | community mirrors |
| Clotho | audio↔text | 15–30 s + 5 captions | ~5k | CC-BY-4.0 | community mirrors |

License column is not decoration: Flickr30k and MSR-VTT are *not* freely
redistributable — download to `data/` locally, never commit them (the repo
`.gitignore` already excludes `data/`).

## 2. Loading patterns that actually work

```python
from datasets import load_dataset

# Image-caption pair — streaming first, then decide about caching.
ds = load_dataset("HuggingFaceM4/COCO", split="train", streaming=True)
ex = next(iter(ds))
print(ex.keys())            # image (PIL), sentids, sentences, ...
```

Streaming matters for the big sets: COCO is ~18 GB, and `load_dataset` will
happily download all of it before handing you the first row. Iterate with
`streaming=True`, take what you need, then materialize a *subset* parquet via
your manifest pipeline — the Week-07 pattern beats a 18 GB cache dir.

```python
# Audio: request decoding with the right sampling rate up front.
from datasets import Audio
ds = load_dataset(" Confederation/AudioCaps", split="train")  # or local mirror
ds = ds.cast_column("audio", Audio(sampling_rate=16_000))
ex = ds[0]
x, sr = ex["audio"]["array"], ex["audio"]["sampling_rate"]
assert sr == 16_000
```

`cast_column` with `Audio(sampling_rate=16_000)` is the audio equivalent of
the resample contract from the pipelines subfolder — decode happens at load
time, per-row, at the rate you asked.

## 3. The gotcha each dataset hides

| Dataset | Gotcha | Defense |
|---|---|---|
| COCO | `image` is lazy-decoded PIL; holding refs leaks RAM | decode → process → drop the PIL object |
| Flickr30k | captions are a list of 5; naive code trains on index 0 only | always iterate *all* captions |
| VQAv2 | answers are vote counts; top-answer extraction is a policy choice | store the policy in settings |
| AudioCaps | clips start mid-file; timestamps matter for alignment | keep `start_s` in the manifest |
| MSR-VTT | mirrors differ in split naming | assert split sizes after load |
| All HF | dataset scripts deprecated → trust `parquet` exports | prefer datasets with parquet exports |

## 4. Subset strategy for the capstone

You will not train on COCO; you will *borrow its evaluation shape*. The
capstone move: download 200–500 pairs per modality-pair dataset, build a
mini-benchmark parquet in the manifest schema (with `source_uri` and
license), and evaluate your RAG retrieval against those pairs with the
metrics from file 05. That is how the tour connects to the capstone without
18 GB of COCO in your life.

```python
def take_subset(ds_iter, n: int = 300) -> list[dict]:
    rows = []
    for i, ex in enumerate(ds_iter):
        if i >= n:
            break
        rows.append(ex)                       # caller persists to parquet
    return rows
```

## Exercises

1. Load 20 COCO rows in streaming mode and record: keys, image mode (RGB?),
   caption count distribution. Then repeat on Flickr30k and diff the schemas.
2. Load AudioCaps with and without `cast_column` at 16 kHz; measure the
   resample cost per row and where it happens (load vs access).
3. Build a 300-pair mini-benchmark parquet from one dataset of your choice,
   following the manifest schema — including license and source_uri — and
   write the five asserts that validate it.

## Pitfalls

- `trust_remote_code=True` on old dataset scripts — pin versions; prefer parquet-native datasets.
- Assuming HF `image` column is a path — it may be bytes or PIL depending on builder.
- Streaming + shuffle without a buffer size — you get "shuffled within a window" only; set `buffer_size` explicitly.

## Resources

- `datasets` docs: `load_dataset`, `Audio`, `Image` features, streaming mode.
- Dataset cards for license text: COCO, Flickr30k, AudioCaps.
