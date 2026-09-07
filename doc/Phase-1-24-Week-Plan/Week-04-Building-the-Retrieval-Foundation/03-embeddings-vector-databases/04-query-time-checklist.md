# 03.4 — The Query-Time Checklist

> Subfolder index: [README.md](README.md) · Parent: [../03-embeddings-vector-databases.md](../03-embeddings-vector-databases.md)

---

## What you'll learn

- The five-item checklist that prevents the silent retrieval bugs
- The threshold calibration: from the distance distribution to the operating point
- The consistency contract as a runtime assertion

## 1. The five-item checklist

| # | Check | Failure it prevents |
|---|---|---|
| 1 | **Same embedder + normalization** as ingestion | silent zero-quality retrieval (W4-03) |
| 2 | **k** set for the prompt budget | context overflow (W4-01) |
| 3 | **Metadata prefilter** applied | permission leaks (E7-01) |
| 4 | **Threshold** on scores | confident garbage served as answers |
| 5 | **Metadata returned** with hits | citations impossible (W4-01) |

Each item is a runtime assertion — not a code comment.

## 2. The threshold calibration

```python
def find_threshold(query_results: list[dict], percentile: float = 0.95) -> float:
    """From wrong-passage runs: the score above which hits are trustworthy."""
    bad_scores = [r["score"] for r in query_results if not r["relevant"]]
    return float(np.percentile(bad_scores, percentile))
```

The calibration procedure: run 20 queries against wrong-passage data (the negative set), collect their top scores, and set the threshold above the 95th percentile. The result: hits below the threshold are flagged as "weak" — feeding the insufficiency escape (W4-01's no-answer path).

## 3. The runtime assertion

```python
def validated_search(query: str, k: int = 5) -> list[dict]:
    assert CONTRACT["embedder"] == CURRENT_EMBEDDER, "embedder drift!"
    assert CONTRACT["normalize"] == True, "normalization drift!"
    hits = table.search(embed(query), k=k).to_list()
    for h in hits:
        assert h["id"] and h["text"], "malformed hit"
        assert h["permissions"] in ALLOWED, "permission violation"
    return hits
```

The assertions are cheap (~μs) and catch the drift bugs that would otherwise surface as mysterious quality drops weeks later. In production, the assertions log warnings instead of raising — the alerts fire, the system degrades gracefully (W15-01).

## 4. The consistency contract as an artifact

```python
CONTRACT = {
    "embedder": "sentence-transformers/all-MiniLM-L6-v2",
    "revision": "8b3219a",
    "normalize": True,
    "chunking": {"strategy": "recursive", "size": 768, "overlap": 100},
    "corpus_version": "v3",
    "index_type": "IVFFlat",
    "nprobe": 10,
}
# stored in the LanceDB table metadata AND the deployment manifest (E8-01)
```

Every search validates its contract against the stored one — the drift detection is a dict comparison, not an investigation.

## Exercises

1. Contract enforcement: implement `validated_search` with all five checks; write the test that breaks each one.
2. Threshold calibration: 20 wrong-passage queries → the negative score distribution → the threshold; verify 19/20 weak hits flagged.
3. The drift canary: change the embedder revision in the contract; run `validated_search` — the assertion fires. Fix and verify.
4. Permission audit: 3 user personas × 10 queries — verify each persona only sees permitted chunks (the prefilter path).
5. The metadata completeness check: for 100 hits, verify every required field is present and non-null — the malformed-hit detector.

## Pitfalls

- **Assertions removed for performance** — the checks cost microseconds; removing them trades safety for nothing
- **The contract checked but not stored** — without the stored contract, there's nothing to compare against
- **Threshold set from one query** — calibrate from the distribution, not one data point (W4-03's calibration)
- **The contract in code but not in the manifest** — deployment drift (E8-01); the contract travels with the deployment
- **Silent assertion removal in error handling** — `try/except AssertionError` defeats the check entirely

## Resources

- W4-01 (the contracts this checklist implements), W5-03 (the filter consumer), E7-01 (the security context) — composed here
- W15-01 (the assertion/alerting pattern), E8-01 (the manifest) — the operational layers
