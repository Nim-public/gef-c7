# Pattern 2 — Unified Embedding Spaces

**What you'll learn:** skip captions: query text and images live in one
CLIP-style space, retrieval is one cosine. Maximum elegance, two real
costs — calibration and domain drift — both measurable.

## 1. The pattern in 10 lines

```python
import torch, torch.nn.functional as F

@torch.no_grad()
def retrieve_unified(query: str, table, k: int = 10):
    q = clip_text_embed(query)                     # (512,)
    res = (table.search(q, vector_column_name="image_vec")
                .limit(k).to_list())
    return [(r["unit_id"], r["_distance"]) for r in res]
```

One index, one encoder, zero captioning cost. This is the Week-07/08
pipeline promoted to a pattern — and it inherits everything already built:
the parity-tested processor, the manifest, the eval harness.

## 2. Cost one: cross-modal calibration

Absolute cosine values *differ per modality pair* (the modality-gap file's
core lesson). In a unified space you must not:

- threshold across modalities with one number;
- mix scores from text-index and image-index without rank fusion.

```python
# correct: per-query z-score or rank fusion before mixing
def calibrated_mix(vec_scores: dict[str, list[float]]) -> dict[str, float]:
    out = {}
    for name, s in vec_scores.items():
        mu, sd = np.mean(s), np.std(s) + 1e-9
        out[name] = {i: (v - mu) / sd for i, v in zip(ids[name], s)}
    return out
```

## 3. Cost two: domain drift

CLIP's space encodes *web photos*. Your corpus is slides, screenshots,
scans. The drift is measurable:

| Probe | Expected on web-domain | On drift-heavy corpus |
|---|---|---|
| text→image R@1 (natural queries) | 0.5–0.6 | collapses (0.1–0.3) |
| text→image R@1 (your domain terms) | — | often near random |
| OCR-merged P1 baseline | — | usually beats P2 on charts |

The P2-vs-P1 comparison is a 20-query eval you already have the harness
for — run it, and let the numbers pick per query class (file 05's router).

## 4. Where P2 genuinely wins

- **Scene/object queries** ("photo of a whiteboard") — captions flatten
  what CLIP encodes directly.
- **Zero-shot routing** (W8 file 02) — same space doubles as classifier.
- **Multi-lingual/lightweight query paths** — no LLM in the loop.

## Exercises

1. Run P2 on your 20-query set vs the P1 merged-index from file 02; report
   R@10 both ways and the domain split (natural images vs charts/screens).
2. Calibration drill: take the two hit-lists; compute z-scored and
   rank-fused merges; compare top-3 stability across the two methods.
3. Drift probe: pick 5 "web-domain" queries and 5 "corpus-domain" queries;
   report R@1 each — the gap *is* the drift number for your memo.

## Pitfalls

- Mixing P2 scores into a P1 pipeline without calibration — the modality
  gap makes one of the two scores systematically larger; rank fusion fixes.
- Judging P2 by its best queries — pattern selection needs the *spread*
  across your query classes, not the max.
- Re-encoding images after a CLIP upgrade without a version bump — stale
  space, silent degradation; settings-version discipline applies.

## Resources

- Your Week-08 CLIP matrix lab — the diagnostics become this pattern's
  health checks.
- LanceDB file (this week) — the `image_vec` column is P2's index.
