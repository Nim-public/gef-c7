# Pattern 1 — Caption-Then-Index: Trade-offs

**What you'll learn:** the workhorse pattern: generate text captions for
every visual unit, index the captions, retrieve with ordinary text RAG.
Its strengths are economic; its failure modes are *semantic loss* — each
one named and paired with a detection.

## 1. The pipeline and its costs

```python
def caption_then_index(units: list[dict]) -> dict:
    captions = [blip_caption(u["path"]) for u in units]       # ~1 s/unit CPU
    texts = [u.get("ocr_text", "") + "\n" + c
             for u, c in zip(units, captions)]                # fuse with OCR!
    vecs = encode_text(texts)                                  # W4 encoder
    return {"vecs": vecs, "texts": texts}
```

| Cost item | Number (your corpus scale) | Notes |
|---|---|---|
| Captioning | ~1 s/unit CPU, offline | one-time; re-run on model upgrade |
| Index build | unchanged from text RAG | captions are just text |
| Query time | unchanged | the pattern's whole selling point |
| Storage | captions in manifest/DB | ~200 B/unit |

Query-time cost identical to text RAG — why this pattern is the *default*
for corpora under ~100k visual units.

## 2. The failure modes, each with a detection

| Failure | Example | Detection |
|---|---|---|
| Number blindness | chart values lost | caption vs OCR diff (sidecar merge) |
| Hallucinated detail | "blue graph" for gray | caption QA: VLM verify or spot-check |
| Layout loss | "left column" claims | region captions or OCR geometry |
| Caption drift | model upgrade changes all captions | caption version in manifest |
| Duplicate-ish captions | 5 near-identical rows | near-dup check (W8 matrix diag) |

The merge line (`ocr_text + caption`) is the pattern's best practice:
captions give *semantics*, OCR gives *values* — neither alone suffices for
charts, and the merge costs nothing at query time.

## 3. When P1 is the right pattern

- Corpus mostly *images of things* (products, scenes) — captions carry it.
- Latency-critical query path — zero added query cost.
- Corpus under ~100k units — captioning is a one-time offline cost.

When it is not: chart-heavy corpora without OCR (numbers lost), or
fine-grained visual queries ("the frame where the cursor is at the
top-right") — captioning compresses exactly what those queries need.

## 4. The caption QA harness — catching failure mode #2 automatically

Hallucinated detail is the failure mode hand-checks miss at scale. A cheap
automated check: re-embed the caption and the image, and flag pairs whose
cross-modal similarity is anomalously low *relative to the corpus*:

```python
import numpy as np

def caption_qa(img_emb: np.ndarray, cap_emb: np.ndarray,
               corpus_scores: np.ndarray) -> bool:
    cos = float(img_emb @ cap_emb / (np.linalg.norm(img_emb) *
                                     np.linalg.norm(cap_emb)))
    mu, sd = corpus_scores.mean(), corpus_scores.std() + 1e-9
    return cos > mu - 3 * sd          # flag only true outliers
```

Run it at caption time; flagged units go to the quarantine list with
`notes += " |caption-qa:low-sim"` — the Week-07 flag discipline, applied
to generated text. Expect ~1–3% flag rate on healthy corpora; 10%+ means
the caption model is wrong for your domain, not that your threshold is.

## Exercises

1. Caption 30 of your images; merge with OCR where present; hand-check 10
   captions against images and log the failure-mode counts.
2. Retrieval ablation: index (a) captions only, (b) OCR only, (c) merged —
   R@10 for each on 20 queries; the merge should win on chart queries.
3. Drift drill: caption 10 images with two BLIP variants; measure caption
   similarity between variants — the number that justifies manifest-side
   caption versioning.

## Pitfalls

- Captioning *at query time* — it is an offline ingest step; query-time
  captioning is a 100× latency bug.
- Trusting captions for numbers — always merge OCR before indexing charts.
- Re-captioning the whole corpus on a whim — bump a caption version and
  re-embed only what changed (the settings-version discipline).

## Resources

- Your BLIP captioning code (W8 file 03); the manifest's `sidecar_status`.
- Week-04 chunking files — the text index these captions feed.
