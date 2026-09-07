# Exercises — Multimodal Datasets & DataLoaders

Expanded set with worked approaches. All snippets assume the repo `.venv`,
run from the root (`py` on PowerShell). Datasets load to `data/` (gitignored).

## 1. Mini-benchmark builder (from 01-dataset-tour)

**Task:** script `scripts/build_mini_benchmark.py` — pull 300 pairs from one
Hub dataset (streaming), map to the manifest schema, write
`data/manifests/mini-benchmark.parquet`, and validate with five asserts.

**Worked approach:**

```python
import pandas as pd
from datasets import load_dataset

def coco_stream_rows(n=300):
    ds = load_dataset("HuggingFaceM4/COCO", split="train", streaming=True)
    for i, ex in enumerate(ds):
        if i >= n:
            break
        yield {
            "unit_id": f"coco-{ex.get('imgid', i)}",
            "modality": "image",
            "rel_path": "",                  # bytes live in the HF row, not disk
            "sha256": "",                    # fill after persisting processed
            "source_uri": f"https://cocodataset.org/#train",
            "license": "CC-BY-4.0",
            "captured_at": "",
            "settings_json": "",
            "notes": f"captions={len(ex.get('sentids', []))}",
        }

rows = list(coco_stream_rows())
df = pd.DataFrame(rows)
df.to_parquet("data/manifests/mini-benchmark.parquet")
assert len(df) == 300
assert df.unit_id.is_unique
assert df.rel_path.dtype == object
```

**Pass criterion:** asserts pass *and* a second run produces a byte-identical
parquet (streaming order stable when you fix the seed/buffer).

## 2. Roundtrip tests for all modalities (from 02-custom-dataset-classes)

**Task:** one pytest file with a parametrized roundtrip test: for each
modality in the manifest, build the Dataset over 8 rows, fetch item 3, and
assert `unit_id` equality plus the modality-specific tensor shape.

**Worked approach:** parametrize over `["text", "image", "audio", "video"]`;
expected shapes: text `(≤128,)` ids; image `(3, 224, 224)`; audio
`(80, 3000)`; video `(12, 3, 224, 224)`. Skip a modality with
`pytest.skip` if the corpus has zero rows of it — but print the skip reason
so the gap is visible, not silent.

**Pass criterion:** test file green on your corpus; the *shape* table lives
in the test docstring, so a reader sees the contract without opening code.

## 3. Throughput tuning report (from 03-dataloader-tuning)

**Task:** for the image Dataset, produce `reports/dataloader-tuning.md` with
the workers×batch grid: workers ∈ {0, 2, 4, 8} × batch ∈ {8, 32}, s/batch
after warm-up, plus one paragraph interpreting the surface.

**Worked approach:** reuse `profile_loader`; run each cell 3× and report the
median (spawn jitter is real on Windows). Interpretation pattern to aim for:
"workers=0 is decode-bound; throughput saturates at 4 workers because
Pillow decode is GIL-free per worker but disk-bound beyond that; batch=32
amortizes collate overhead 3.1×."

## 4. The drift drill, automated (from 04-video-in-dataset)

**Task:** test that fails when the sampling rule changes: encode one clip,
compare mean-pooled embedding against a *committed reference vector*
(cosine > 0.999). Commit the reference vector and the rule version.

**Worked approach:**

```python
REF = np.load("tests/fixtures/clip-drift-reference.npy")   # (512,)

def test_sampling_rule_stable():
    emb = encode_clip_frames(uniform_sample_decode(SAMPLE, n=12), pool="mean")
    cos = float(emb @ REF / (np.linalg.norm(emb) * np.linalg.norm(REF)))
    assert cos > 0.999, f"sampling drift: cos={cos:.4f}"
```

The reference vector is tiny (2 KB) and catches: changed `n`, changed offset
rule, changed resize, changed normalize — i.e., every silent preprocessing
decision, in one test.

**Pass criterion:** intentionally bumping the offset rule to `(i + 0) / n`
turns the test red; restoring it green.

## 5. Capstone wiring (from all files)

**Task:** your capstone `scripts/encode_corpus.py` should (a) read the
manifest, (b) use `MultimodalUnits` + two-pass encoding, (c) write the
`(N, 512)` matrix + row-aligned manifest, (d) assert the row invariant, and
(e) emit the tuning report path in its log output.

**Worked approach:** assemble from files 02–03; the only new logic is the
invariant assertion after the write:

```python
meta = pd.read_parquet("data/manifests/corpus-manifest.parquet")
mat = np.load("data/embeddings/clip-vit-b32/matrix.npy")
assert len(meta) == mat.shape[0] == mat.shape[0]
```

**Pass criterion:** deleting any processed file and re-running the script
regenerates it (cache correctness), and the invariant test is part of
`tests/` so it runs in CI, not just locally.

## Pitfalls recap

- Streaming loads that look hung — first batch includes connection setup; time *after* the first row.
- Assert-less benchmarks: a parquet with duplicate `unit_id`s poisons every later join; the five asserts in exercise 1 are the minimum, not the maximum.
- Tuning reports without warm-up exclusion — Windows spawn cost (~1–2 s) dominates small grids and inverts conclusions.
