# 05.2 — Search Service Design

> Subfolder index: [README.md](README.md) · Parent: [../05-capstone-task-search-engine.md](../05-capstone-task-search-engine.md)

---

## What you'll learn

- The search function: the single entry point that all consumers use
- The API shape: CLI, REST, or Gradio — the design that survives
- The threshold and fallback design: what happens when nothing matches

## 1. The search function (the single entry point)

```python
def search(query: str, k: int = 5, filters: dict | None = None) -> dict:
    """The single search entry point. All consumers use this.

    Returns: {"hits": [{id, text, source, score, via}], "caveat": str | None}
    """
    bm25_hits = bm25_search(query, k=k * 2, filters=filters)
    vec_hits = vector_search(query, k=k * 2, filters=filters)
    fused = rrf_fuse([h["id"] for h in bm25_hits], [h["id"] for h in vec_hits])[:k]
    results = fetch_full(fused)                        # rejoin with text + metadata

    if not results or max(r["score"] for r in results) < THRESHOLD:
        return {"hits": [], "caveat": "No strong matches found. Try rephrasing."}
    return {"hits": results, "caveat": None}
```

The contract: deterministic inputs, structured outputs, explicit caveats. Every consumer (the W3 bot, the W13 agent, the W14-05 assistant) codes against this function — the W9-05 contract pattern, one level up.

## 2. The API shapes

| Consumer | Shape |
|---|---|
| CLI | `py search.py "query" --type policy` |
| REST | `GET /search?q=...&type=policy&k=5` |
| Gradio | `gr.Interface(fn=search, ...)` |
| Agent tool | `search_knowledge(query, k, filters) -> dict` |

All four consume the same `search()` function — the API shape is a thin adapter, not a reimplementation.

## 3. The threshold design

The threshold comes from the W4-03 calibration (the distance distribution's elbow). The design:

```python
THRESHOLD = 0.72   # calibrated from the negative-score distribution

def should_answer(hits: list[dict]) -> bool:
    if not hits: return False
    return max(h["score"] for h in hits) >= THRESHOLD
```

The threshold is a *product decision* calibrated by data — too low serves weak matches, too high hides real answers. The calibration is re-run when the corpus or embedder changes (W4-03's drift rule).

## Exercises

1. Build the search function with all three arms (BM25, vector, RRF); test with 10 queries across question types.
2. The CLI: implement `search.py` with argparse (query, k, type filters); test the output format.
3. The threshold calibration: 20 wrong-passage queries → the negative score distribution → the threshold; verify the caveat fires.
4. The API: wrap `search()` in FastAPI (Base Camp 3); test with curl; measure p95 latency.
5. The multi-consumer test: the same `search()` function called from the CLI, the API, and a Gradio app — verify identical results.

## Pitfalls

- **Multiple search entry points** — each with different thresholds/filters; one function, many adapters
- **The caveat ignored** — consumers must check the caveat and handle it; test each consumer's handling
- **Filters applied inconsistently across consumers** — the CLI and API must produce identical results for the same query+filters
- **No provenance in the response** — consumers can't cite without source metadata
- **Latency measured cold** — first-call includes model loading; warm up before benchmarking

## Resources

- W4-01 through W4-04 — the components this service composes
- W9-05 (the retrieval contract), W14-05 (the MCP tool shape) — the consumers
- W15-05 (the latency/cost measurement discipline) — the SLA framework
