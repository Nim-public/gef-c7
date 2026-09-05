# Hybrid Retrieval — Cross-Space Fusion with Filters

**What you'll learn:** the online retrieval component: text-vector, image-
vector, and FTS searches fused by RRF, filtered by modality scope, with
the router from the patterns file in front.

## 1. The retriever, complete

```python
# scripts/retrieve.py
import re, lancedb

db = lancedb.connect("data/lancedb")
table = db["units"]

def retrieve(query: str, k: int = 10, scope: str | None = None) -> list[dict]:
    route = route_query(query)                       # from patterns file 05
    base = table.search()
    if scope:
        base = base.where(f"modality = '{scope}'", prefilter=True)

    lists = []
    if route in ("P1-fts", "P1-merged"):
        lists.append([h["unit_id"] for h in
                      base.search(query, query_type="fts").limit(20).to_list()])
    if route in ("P1-merged", "P2"):
        col = "image_vec" if route == "P2" else "text_vec"
        q = clip_text_embed(query) if col == "image_vec" else encode_text([query])[0]
        lists.append([h["unit_id"] for h in
                      base.search(q, vector_column_name=col).limit(20).to_list()])

    fused = rrf(lists)
    return [hydrate(uid, score) for uid, score in list(fused.items())[:k]]
```

Three searches at most, one fusion, one hydrate (join back to unit facts
from the table). Every query class from the routing table is served by a
subset — the retriever is the router's executor.

## 2. Filters: scope, parent, version

| Filter | Clause | Use |
|---|---|---|
| modality scope | `modality = 'image'` | modality-targeted tabs |
| coarse mode | `parent_id IS NULL` | context-window filling |
| caption version | `caption_version = 'v3'` | rolling re-index |
| freshness | `ingested_at > X` | demo-time additions |

Prefilter for restrictive filters (scope on 10% of rows); the sweep file's
nprobe/refine numbers apply to the vector paths.

## 3. The hydrate step: facts from the table, not the embedding

```python
def hydrate(uid: str, score: float) -> dict:
    row = table.to_pandas().query("unit_id == @uid").iloc[0]
    return {"unit_id": uid, "score": round(float(score), 4),
            "text": row["text"], "path": row["path"],
            "parent_id": row.get("parent_id")}
```

The returned dict is the tool contract's payload (W9 file 01): scores for
the agent, text for the prompt, path for citation thumbnails, parent for
drill-down.

## Exercises

1. Implement `retrieve` with all three searches; verify the router picks
   different search subsets per query class (log them).
2. Filter drill: scope to images at 10% of corpus; compare prefilter vs
   postfilter hit counts at k=10.
3. Contract test: `retrieve` output matches `tool-contract.md`'s schema for
   5 queries, including one empty-result query.

## Pitfalls

- Searching the *wrong column* for the route (CLIP query against text_vec)
  — silent garbage; assert encoder↔column pairing in code.
- Fusion over lists of different *content* types (ids vs paths) — fuse
  unit_ids only.
- Hydrate via per-row queries in a loop — batch the join; 10 rows is fine,
  1000 is not.

## Resources

- Patterns file 05 (the router), LanceDB files 01/04 (schema, fusion).
- Your tool contract (W9 file 01 exercises) — the payload schema.
