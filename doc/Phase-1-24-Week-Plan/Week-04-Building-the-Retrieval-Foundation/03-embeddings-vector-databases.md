# 03 — Embeddings & Vector Databases (FAISS, LanceDB)

> Week 4 index: [README.md](README.md)

**Session topics:** *Embeddings — converting data into numerical representations (S1) · Vector Databases — storage and retrieval using FAISS (S1), LanceDB (S2) · Implement vectorization and vector databases for embedding storage and search (S2)*

---

## What you'll learn

- What a vector index actually computes — brute force first, then why indexes exist
- FAISS: flat, IVF, and when each is right
- LanceDB: an embedded vector database with metadata + filtering
- The similarity metrics (L2 vs cosine vs inner product) and when they're equivalent

## 1. First, no database: brute force

Semantic search = find the nearest vectors. With 1,000 chunks you don't need an index at all:

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
corpus = ["chunk one text...", "chunk two text...", "..."]      # from file 02
emb = model.encode(corpus, normalize_embeddings=True)            # (N, 384)

def search(query, k=5):
    q = model.encode([query], normalize_embeddings=True)[0]
    sims = emb @ q                          # cosine (normalized) — one matrix op
    top = np.argsort(-sims)[:k]
    return [(corpus[i], float(sims[i])) for i in top]
```

`N=1k`: trivially fast. `N=1M`: 384-dim float32 = 1.5 GB, and every query scans everything. **Vector indexes trade a little recall for big speed/memory wins.**

## 2. FAISS (Facebook AI Similarity Search)

### Flat — exact, zero tuning

```python
import faiss
import numpy as np

d = 384
index = faiss.IndexFlatIP(d)               # inner product = cosine on normalized vectors
index.add(emb.astype("float32"))           # (N, 384)

q = model.encode(["refund timeline"], normalize_embeddings=True).astype("float32")
scores, ids = index.search(q, k=5)         # exact nearest neighbors
```

Use flat up to ~100k vectors. Exact = your evals' ground truth (file 02's hit-rate test should use flat as reference).

### IVF — approximate, tuned

Clustering first (nlist cells), searching only the nearest few cells (nprobe):

```python
nlist = 100
quantizer = faiss.IndexFlatIP(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
index.train(emb.astype("float32"))         # k-means over your vectors — needs ≥ ~30*nlist
index.add(emb.astype("float32"))
index.nprobe = 10                          # search 10 of 100 cells: ~10× faster, ~99% recall
```

**Recall is a dial** (`nprobe`), not a property. Measure it: run the same query set on flat vs IVF and compute overlap of top-k. When nprobe=nlist you've rebuilt flat (exact) — the dial's ceiling.

Rule of thumb: IVF earns its keep around 100k–10M vectors; below that, flat; above that, HNSW-class graphs (or quantized IVF — `IndexIVFPQ`, the "PQ" from Week 9's IVF-PQ mention).

### Which metric?

- **Cosine similarity** = dot product on normalized vectors — so normalize embeddings and use `IndexFlatIP`; identical results, simpler index
- L2 (Euclidean) ranks identically to cosine *when all vectors are normalized* — the reason you always see `normalize_embeddings=True` in this program
- Mixed dim counts or unnormalized vectors = bug factory; normalize everywhere

## 3. LanceDB — a real vector database

FAISS is an in-memory index — no metadata filtering, no persistence story, no updates. LanceDB is an **embedded** database (files on disk, no server — like SQLite for vectors), which is why the program uses it from here on.

```python
import lancedb
import pandas as pd

db = lancedb.connect("data/lancedb")       # just a folder
table = db.create_table(
    "capstone_chunks",
    data=pd.DataFrame({                    # vector + payload in one table
        "id": chunk_ids, "text": chunk_texts, "source": sources,
        "doc_type": doc_types, "vector": emb_list,   # list of 384-float vectors
    }),
    mode="overwrite",
)
```

Search, filter, done:

```python
q = model.encode(["what is the refund timeline"], normalize_embeddings=True)[0]

hits = (table.search(q)
        .where("doc_type = 'policy'", prefilter=True)   # SQL-like metadata filter
        .limit(5)
        .to_list())

for h in hits:
    print(round(h["_distance"], 3), h["source"], h["text"][:80])
```

- Filtering with `prefilter=True` = permission checks before search (the security pattern from file 01)
- Scales: Lance format on disk, ANN by default (`nprobes`, `refine_factor` knobs), but starts sensible without tuning
- Updates: `table.add(...)`, `table.delete("id = '...'")` — a real DB, not a frozen index
- Build-in-one-line alternative: `pydantic` schema + `EmbeddingFunctionRegistry` auto-embeds on add (see docs) — but explicit vectors (above) teach you more

### FAISS vs LanceDB vs (preview) cloud DBs

| | FAISS | LanceDB | Pinecone/Weaviate/Qdrant/PGVector |
|---|---|---|---|
| Server | none (library) | none (embedded) | dedicated/managed |
| Metadata filter | manual | SQL-like ✓ | rich ✓ |
| Persistence | save/load files | files on disk ✓ | managed ✓ |
| Sweet spot | pure KNN research, evals | local dev → prod-ish | multi-tenant, scale-out |

## 4. The query-time checklist (same every system)

1. **Same embedding model + normalization** as ingestion (W1-04 → now a schema rule)
2. **k** chosen for the prompt budget (3–8 after reranking, Week 5)
3. **Metadata filter** applied pre-search for permissions/type
4. **Threshold** on `_distance`/score — "no good hit" must look different from "top hit is bad" (feeds file 01's insufficiency escape)
5. **Return metadata with the chunk** — citations are downstream of this decision

## Exercises

1. Time brute force vs `IndexFlatIP` at N=1k, 10k, 50k (your corpus + synthetic). When does the index matter?
2. Build IVF (`nlist=100`): sweep `nprobe ∈ {1, 5, 10, 50}`; plot recall@5 (vs flat) and QPS. Where's your sweet spot?
3. LanceDB end-to-end: chunks from file 02 with metadata → table → 10 queries with `doc_type` filter. Verify filtered results *only* come from that type.
4. Security test: 3 chunks your persona shouldn't see (permissions field), filtered query vs unfiltered. Show the leak and the fix.
5. Distance sanity: for one query, print top-10 distances. Find the "elbow" where scores turn bad — that's your threshold. Wire it into the RAG prompt as the insufficiency trigger.

## Pitfalls

- **Unnormalized vectors + IP index** — scores are meaningless magnitudes; normalize once at encode time
- **IVF trained on too few vectors** — `index.train` crashes or clusters badly; need ≥ ~30×nlist training points
- **`float32` forgetfulness** — FAISS wants float32; float64 raises cryptic errors
- **Post-filtering vs pre-filtering** — filtering after top-k can return zero results when matches exist elsewhere; use `prefilter=True`
- **Trusting ANN recall** — always measure against flat on your eval set (that's what it's for)

## Resources

- [FAISS wiki](https://github.com/facebookresearch/faiss/wiki) — *Getting started*, *Running on GPUs*, index choice guide
- [LanceDB docs](https://lancedb.github.io/lancedb/) — search/filter/hybrid (hybrid = Week 5)
- Johnson et al., *Billion-scale similarity search with GPUs* (IVF/PQ internals — skim)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — pick the embedding model (Week 5 compares them properly)
