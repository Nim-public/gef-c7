# 01.4 — The Datasets Library

> Subfolder index: [README.md](README.md) · Parent: [../01-huggingface-platform.md](../01-huggingface-platform.md)

---

## What you'll learn

- Arrow under the hood: why `datasets` is memory-mapped and fast
- Lazy decoding for images/audio; streaming for infinite/large data
- The processing API: `filter`, `map`, `shuffle`, splits
- Building your own dataset from local files

## 1. Arrow under the hood

```python
from datasets import load_dataset

ds = load_dataset("imdb")                    # downloads once → Arrow files on disk
print(ds)
# DatasetDict({train: Dataset(features: {'text': Value('string'), 'label': ClassLabel(...)},
#              num_rows: 25000), test: ...})
print(ds["train"][0])                        # decoded on access — lazy
```

What Arrow buys: **columnar, memory-mapped storage** — `ds[0]` decodes one row without loading 25k rows; `.filter/.map` operate in parallel over the Arrow table. Memory usage stays ~constant regardless of dataset size (until you call `.to_pandas()` or materialize everything).

## 2. Streaming — datasets larger than disk

```python
stream = load_dataset("nelorth/oxford-flowers", split="train", streaming=True)
for example in itertools.islice(stream, 5):        # one pass, no download completes
    print(example.keys())
```

Streaming caveats: **single pass only** (no random access, no `len()`), shuffle uses a buffer (`shuffle(buffer_size=10_000)` — approximation), and repeated iteration re-downloads unless cached. Streaming is for exploration and one-pass training; indexed workloads want Arrow on disk.

## 3. Processing: filter, map, shuffle

```python
ds = load_dataset("imdb", split="train")

short = ds.filter(lambda ex: len(ex["text"]) < 500, num_proc=4)
labeled = ds.map(lambda ex: {"length": len(ex["text"])}, num_proc=4)
balanced = ds.shuffle(seed=42).select(range(5000))
```

- `.filter` keeps rows (predicate), `.map` transforms/adds columns — both parallelize with `num_proc`
- `.map(..., remove_columns=[...])` drops intermediates — keeps memory flat
- **Batched map** (`batched=True`) processes lists of examples — much faster for tokenizers:

```python
tok = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
tokenized = ds.map(lambda batch: tok(batch["text"], truncation=True, max_length=256),
                   batched=True, batch_size=1000, remove_columns=["text"])
```

## 4. Building datasets from local files

```python
from datasets import Dataset, DatasetDict

rows = [json.loads(l) for l in open("data/corpus.jsonl", encoding="utf-8")]
ds = Dataset.from_list(rows)                       # from your W1-04 JSONL directly

# with images/audio — features declare the media type for lazy decoding:
from datasets import Features, Image, Value
schema = Features({"id": Value("string"), "image": Image(), "caption": Value("string")})
media_ds = Dataset.from_list(media_rows, features=schema)
```

Saving: `ds.save_to_disk("data/imdb_processed")` (Arrow + metadata) and `load_from_disk` — the W4/W16 versioned-artifact pattern applied to datasets.

## 5. Splits and versioning

```python
split = ds.train_test_split(test_size=0.1, seed=42, stratify_by_column="label")
DatasetDict({"train": split["train"], "test": split["test"]}).save_to_disk("data/imdb_v2")
```

- `stratify_by_column` preserves class ratios per split (W1-05's discipline)
- Versioned saves (`imdb_v1`, `v2`) match the W16-01 eval-versioning rules — datasets are artifacts too
- Document every transformation: `ds.info.dataset_name`, description, and the changelog in your README

## Exercises

1. Memory profile: load a 1M-row text dataset with and without streaming — measure peak RSS (`psutil`) for both.
2. Tokenization map: batched map with a tokenizer over 100k rows — benchmark `num_proc` ∈ {1, 4, 8}.
3. Shuffle-quality check: streamed shuffle with buffer 1k/10k/50k on a sorted dataset — measure how well each mixes (first-100 label distribution).
4. Build a `DatasetDict` from your capstone's JSONL (W1-04 fixture) with stratified splits and versioned save; verify reload equality.
5. Arrow introspection: open the on-disk Arrow file, inspect the schema and row-group layout — explain why random access is O(1).

## Pitfalls

- **`.map` with heavy per-example work unbatched** — batched=True with the tokenizer is 5–20× faster
- **Streaming + `.filter` with state** — filters must be stateless per example in streaming mode
- **Materializing images eagerly** — `Image()` feature decodes on access; keep lazy until the model needs pixels
- **Forgetting `num_proc`** — single-process map is the default and the bottleneck
- **Version-less saves** — `save_to_disk` overwrites silently; directory-per-version (W16-01)

## Resources

- [datasets docs](https://huggingface.co/docs/datasets/index) — load, stream, process, save
- [Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html) — the storage spec behind it
- W2-01 parent (Hub), W1-04 (local formats) — the sources this library bridges
