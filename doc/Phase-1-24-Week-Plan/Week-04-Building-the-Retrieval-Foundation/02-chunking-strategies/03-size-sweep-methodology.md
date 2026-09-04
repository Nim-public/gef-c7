# 02.3 — The Size/Overlap Sweep

> Subfolder index: [README.md](README.md) · Parent: [../02-chunking-strategies.md](../02-chunking-strategies.md)

---

## What you'll learn

- The hit-rate metric: the measurement that makes chunking decisions empirical
- The sweep protocol: size × overlap grid on your corpus
- The knee: finding the optimal operating point
- The reporting format that makes the sweep auditable

## 1. The hit-rate metric

```python
import json

def hit_rate(results: list[dict], eval_set: list[dict], k: int = 5) -> float:
    """Fraction of eval questions where a relevant chunk appears in top-k."""
    hits = 0
    for case in eval_set:
        got = {r["id"] for r in results(case["query"], k)}
        if got & set(case["relevant_ids"]):
            hits += 1
    return hits / len(eval_set)
```

The eval set: 20–30 questions, each with hand-marked relevant chunk ids. The questions come from: the corpus itself (obvious questions), user phrasings (the hard ones), and adversarial cases (the boundary probes). The W1-05 discipline applied to retrieval.

## 2. The sweep protocol

```python
SIZES = [256, 384, 512, 768, 1024]
OVERLAPS = [0, 64, 128]
STRATEGY = "recursive"           # fixed per sweep — one variable at a time

results = []
for size in SIZES:
    for overlap in OVERLAPS:
        if overlap >= size: continue
        chunks = chunk_all(corpus, size, overlap, STRATEGY)       # file 01
        emb = encode([c["text"] for c in chunks])
        index = build_index(emb)
        hr = hit_rate(lambda q, k=5: search_chunks(index, q, k), eval_set)
        results.append({"size": size, "overlap": overlap, "hit_rate": hr, "n_chunks": len(chunks)})
```

The grid: 5 sizes × 2–3 overlaps = 10–15 configurations. Each takes ~5 minutes (chunk + embed + index + eval) — the full sweep in under an hour. The output table:

| size | overlap | hit_rate@5 | n_chunks | notes |
|---|---|---|---|---|
| 256 | 0 | 0.55 | 2100 | too fragmented |
| 512 | 64 | 0.72 | 890 | |
| **768** | **100** | **0.78** | **640** | **best** |
| 1024 | 0 | 0.68 | 420 | dilution |

## 3. Reading the sweep (the knee)

The hit-rate curve typically rises with size (more context per chunk) then falls (dilution). The knee — where the curve flattens — is the operating point:

- **Below the knee**: increasing size helps (more context per chunk)
- **At the knee**: optimal balance
- **Above the knee**: dilution wins (W4-02's dilution trade)

The knee varies per corpus: structured docs (clear sections) peak earlier; meandering prose peaks later. The sweep finds *your* knee, not a universal one.

## 4. The reporting format (auditable, reproducible)

```markdown
## Chunking sweep — corpus v3, eval v1, 25 queries
| size | overlap | strategy | hit_rate@5 | MRR | n_chunks | embed_time |
|---|---|---|---|---|---|---|
| 512 | 64 | recursive | 0.72 | 0.58 | 890 | 45s |
| **768** | **100** | **recursive** | **0.78** | **0.64** | **640** | **38s** |
| 768 | 100 | +contextual headers | **0.83** | 0.69 | 640 | 39s |

Selected: 768/100/recursive + contextual headers
Evidence: eval_set v1, embedder all-MiniLM-L6-v2@8b3219a
```

Every variable pinned, every number reproducible, the winner justified — the sweep output *is* the chunking decision's documentation.

## Exercises

1. Build the eval set: 25 queries with relevant chunk ids — the fixture all future sweeps use.
2. Run the full sweep (§2) on your corpus; produce the table; identify the knee.
3. The overlap ablation: at the best size, sweep overlap ∈ {0, 10%, 20%} — measure the hit-rate delta; is overlap helping?
4. The distribution check: are the eval questions evenly distributed across document types? (Biased eval → biased sweep.)
5. The reporting drill: write the §4 markdown block for your sweep — the format that makes the decision auditable at a glance.

## Pitfalls

- **Sweeping without a fixed eval set** — the hit rate measures the eval, not the chunking; freeze the eval first
- **Confounding embedder and chunker** — change one variable per sweep (W5-02's rule)
- **The knee on a tiny eval set** — 5 questions can't distinguish 0.72 from 0.78; ≥20 questions minimum
- **Ignoring n_chunks** — 2× the chunks = 2× the storage and embed time; the trade matters
- **The sweep run once, corpus updated** — re-sweep on corpus changes; the optimal size shifts with content

## Resources

- W4-02 parent (the strategies), W4-03 (the index each config builds), W4-05 (the task consuming the winner) — composed here
- Chroma, *Evaluating chunking strategies* — the metrics-first methodology
- W16-01 (the versioning discipline applied to sweep results)
