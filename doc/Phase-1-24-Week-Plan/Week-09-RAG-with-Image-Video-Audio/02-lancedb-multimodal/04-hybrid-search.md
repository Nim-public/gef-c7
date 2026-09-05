# Native Hybrid Search — FTS + Vector, RRF

**What you'll learn:** LanceDB's native full-text search (FTS) combined
with vector search — two ranking signals fused by RRF, the retrieval
upgrade that fixes exact-term queries dense embeddings miss.

## 1. Why hybrid: the two failure modes

| Query type | Vector-only | FTS-only | Hybrid |
|---|---|---|---|
| "how does attention work" | strong | weak (exact terms) | strong |
| "Error 0x80070057" | weak (rare tokens) | **strong** | strong |
| "the quarterly EBITDA chart" | medium | medium | strong |

Dense embeddings blur exact tokens (error codes, names, ids); FTS nails
those and misses paraphrase. The fusion file's rank fusion, applied to your
own two indexes.

## 2. Build FTS + query both

```python
import lancedb
db = lancedb.connect("data/lancedb")
table = db["units"]

# build FTS index on the caption column (one-time; rebuild on corpus change)
table.create_index(index_type="FTS", schema_version="v2",
                   on_columns=["caption"], replace=True)

vec_hits = (table.search(q_vec, vector_column_name="text_vec")
                 .limit(20).to_list())
fts_hits = (table.search(q_text, query_type="fts")   # string query → FTS path
                 .limit(20).to_list())
```

## 3. The fusion, RRF as specified

```python
def rrf(result_lists: list[list[str]], k: int = 60) -> dict[str, float]:
    """Reciprocal Rank Fusion over ranked unit_id lists."""
    scores: dict[str, float] = {}
    for lst in result_lists:
        for rank, uid in enumerate(lst, start=1):
            scores[uid] = scores.get(uid, 0.0) + 1.0 / (k + rank)
    return dict(sorted(scores.items(), key=lambda kv: -kv[1]))

ids_vec  = [r["unit_id"] for r in vec_hits]
ids_fts  = [r["unit_id"] for r in fts_hits]
fused    = rrf([ids_vec, ids_fts])
```

RRF constants: `k=60` dampens rank-1 dominance; lists of *unequal length*
are fine (a hit in both lists rises; a hit in one stays modest). No score
calibration needed — the reason RRF beats weighted fusion across engines.

## 4. Filters compose with both paths

```python
res = (table.search(q_vec, vector_column_name="text_vec")
            .where("modality = 'image'", prefilter=True)
            .limit(20).to_list())
# FTS + filter:
res_fts = (table.search("orientation histogram", query_type="fts")
                .where("modality = 'image'", prefilter=True)
                .limit(20).to_list())
```

The capstone query planner, then, is: detect exact-token queries (regex for
codes/ids) → lean FTS; else 50/50 RRF; always prefilter by modality scope.

## 5. Tokenizer reality — where FTS matches, literally

FTS is lexical: it matches *tokens*. Three practical consequences:

| Query | FTS result | Why |
|---|---|---|
| "EBITDA" vs "EBITDA margin" | both hit rows containing "EBITDA" | token overlap |
| "don't" vs "do not" | miss unless tokenizer splits/normalizes | tokenization choice |
| "C++" | often tokenized oddly (C, ) | punctuation handling |

```python
# test your corpus's tokenizer behavior with the three pairs above —
# record what matches before trusting FTS-lean routing
```

The router's exact-term detection (patterns file 05) assumes FTS behaves
sanely on codes and names — verify with your *actual* units, since
 LanceDB's default tokenizer handles hyphens and symbols differently than
your intuition expects.

## Exercises

1. Build FTS on your captions; find 5 queries where FTS beats vector-only
   (error codes, unique terms) and 5 where it loses (paraphrases) — the
   table is your router's training data.
2. Fusion ablation: RRF(k=60) vs RRF(k=1) vs naive score-fusion on 20
   queries; R@10 for each — verify score-fusion loses when scales mismatch.
3. Latency: measure vec-only vs FTS vs fused per query — the budget line
   for your Week-10 tool contract.

## Pitfalls

- FTS on *empty* captions — build the index after fillna("") and expect
  those rows never to hit; document it.
- Comparing fused results against GT built from vector-only — hybrid
  changes the notion of relevance; GT must be human-labeled for fusion
  evals.
- Tokenizer mismatch (FTS default tokenizer vs your queries) — quote-heavy
  or code queries need the right tokenizer setting; test with real queries.

## Resources

- LanceDB full-text search docs (create_index FTS, query_type="fts").
- Cormack et al. 2009 (RRF); your fusion file (W8) — the same fusion,
  engine-side.
