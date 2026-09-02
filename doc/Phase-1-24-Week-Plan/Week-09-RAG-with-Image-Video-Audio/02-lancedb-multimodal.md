# 02 — LanceDB for Multimodal AI

> Week 9 index: [README.md](README.md)

**Session 1 topics:** *Introduction to LanceDB. Core LanceDB features for Multimodal AI. Embedding and Indexing Techniques — IVF-PQ, Hybrid search.*

---

## What you'll learn

- Why an embedded multimodal store fits this program (vs FAISS's index-only model)
- Multiple vector columns in one table — text and image vectors side by side
- IVF-PQ: product quantization mechanics, recall knobs, and when compression is worth it
- LanceDB's native hybrid search (vector + full-text, RRF-fused) — replacing your hand-rolled Week 4 RRF

## 1. LanceDB's role in the multimodal stack

Week 4 introduced LanceDB as a vector database with metadata. Multimodal workloads stretch it further, and it holds:

| Need | Feature |
|---|---|
| text + image + audio embeddings | **multiple vector columns** per table |
| cheap scale (100k–10M+) | ANN indexes incl. **IVF-PQ** (compressed) |
| "refund policy" + "photo like this" | **hybrid search** (vector + full-text + RRF) |
| filter by category/permissions | SQL `where` prefilter (W4-03/W5-03) |
| media stays on disk | store **paths/references**, not bytes — the manifest pattern (W7-01) |

One table, one row per asset, everything joined by the same `id` as your relational store (W6-02's coexistence map).

## 2. Multiple vector columns

```python
import lancedb, pandas as pd

db = lancedb.connect("data/lancedb")

table = db.create_table("catalog_multimodal", data=pd.DataFrame({
    "id":        ["p1", "p2", "p3"],
    "text":      ["mechanical keyboard RGB 87 keys", "gaming mouse 16k dpi", "27-inch 4k monitor"],
    "category":  ["keyboard", "mouse", "monitor"],
    "price":     [4500, 2500, 28000],
    "image_path":["data/img/p1.jpg", "data/img/p2.jpg", "data/img/p3.jpg"],   # reference, not bytes
    "text_vec":  txt_embs,      # (N, 384)  from MiniLM/BGE (W5-02 winner)
    "image_vec": img_embs,      # (N, 512)  from CLIP (W8-04 winner)
}), mode="overwrite")
```

Query each space separately and fuse yourself (W4-04 RRF), or let the table's native hybrid do it (§4). Cross-space retrieval — "text like this *image*" — is a CLIP trick: embed the image with CLIP's text encoder? No — embed the image, search `image_vec`; embed a *text query*, search `text_vec`, then RRF the two rankings (pattern 2 + 3 in file 03).

## 3. IVF-PQ — compressed approximate search

**Product quantization** shrinks vectors ~30–100×: split each 512-d vector into `m=64` subvectors of 8 dims; quantize each subvector to the nearest of 256 learned centroids (8 bits); store 64 bytes instead of 2048. Search reconstructs approximate distances from codebooks.

IVF-PQ = IVF clustering (W4-03) + PQ inside each cell:

```
1M vectors × 512d × 4B = 2 GB   →   IVF-PQ(64): ~64 MB + codebooks
```

```python
import faiss, numpy as np          # FAISS for the teaching version; LanceDB does this internally

d, m = 512, 64
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist=256, m=m, bits=8, metric=faiss.METRIC_INNER_PRODUCT)
index.train(emb.astype("float32"))            # needs ≥ ~30×nlist training vectors
index.add(emb.astype("float32"))
index.nprobe = 16                              # recall/speed dial, like W4-03
D, I = index.search(q.astype("float32"), k=5)
```

**Recall is bought back with**: `nprobe` ↑ (scan more cells), **refine/rerank** stage (fetch true vectors for the top candidates and re-rank exactly — LanceDB's `refine_factor`), larger `m`/`bits`. The W5-03 cross-encoder reranker sits *on top* of this stack naturally.

Compression decision rule: ≤ ~100k vectors → flat (exact, zero tuning). 100k–10M → IVF-PQ or HNSW; measure recall@k vs flat on your eval set (the W4-03 protocol, unchanged).

In LanceDB, creating an index triggers ANN automatically:

```python
table.create_index(metric="cosine", vector_column_name="text_vec",
                   num_partitions=64, num_sub_vectors=48)   # IVF-PQ under the hood
# query-time knobs:
res = (table.search(q, vector_column_name="text_vec")
            .nprobes(16).refine_factor(20).limit(10).to_list())
```

## 4. Native hybrid search

Week 4 hand-rolled BM25 + vectors + RRF. LanceDB does it natively — build a full-text-search (FTS) index, then query both at once:

```python
table.create_fts_index("text")                    # BM25-style full-text index

res = (table.search(query_type="hybrid")
            .vector(q_vec, vector_column_name="text_vec")
            .text("rgb mechanical keyboard")
            .limit(10)
            .rerank(reranker="rrf")               # built-in RRF fusion
            .to_list())
```

This is your Week 4 `search()` with the fusion maintained for you — same semantics (file 04's RRF), fewer moving parts. Keep your own RRF implementation around anyway: it fuses *cross-index* results (e.g., SQL rows + vector chunks, W6-04) which the native path doesn't cover.

## 5. Filtering + metadata on multimodal rows

```python
res = (table.search(q_img, vector_column_name="image_vec")     # search BY image
        .where("(category = 'keyboard') AND (price < 5000)", prefilter=True)
        .limit(5).to_list())
```

Same rules as W5-03: prefilter for permissions, post-filter only for soft preferences; every hit carries `id` → join to the relational store and to the raw media path for citation.

## Exercises

1. Memory audit: 200k × 512-d — flat vs IVF-PQ(m=64) size; measure with your actual table (`table.stats()` / disk usage). Recall@10 for both on your eval set?
2. nprobe/refine sweep: recall vs latency at `nprobe ∈ {1,8,32}` × `refine_factor ∈ {1, 20}`. Plot; pick an operating point and justify it in one line.
3. Native hybrid vs your RRF: same 25-query harness (W4-05) through both. Same ranking? Differences from BM25 parameters — document them.
4. Image-as-query: search `image_vec` with a photo, then with its CLIP text description — are the top-5 sets similar? What does that say about CLIP's space (W8-04)?
5. Multimodal filter probe: "keyboards under 5k with an image" — verify the prefilter path returns only rows with non-null `image_path` and `price < 5000`.

## Pitfalls

- **Storing media bytes in the table** — bloat + slow scans; store paths + fingerprints (W7-01)
- **Training IVF-PQ on too few vectors** — needs ≥ ~30×nlist; below that, stay flat
- **Recall unmeasured after enabling ANN** — the W4-03 lesson: approximate indexes trade recall *silently*; measure vs flat
- **Different embedding models across columns** — each column is its own space; never mix vectors from different models in one column
- **FTS index not rebuilt on add** — hybrid queries silently miss new rows; rebuild/update after ingestion

## Resources

- [LanceDB docs](https://lancedb.github.io/lancedb/) — indexes (IVF-PQ), hybrid search, multi-vector patterns
- FAISS wiki, *IndexIVFPQ* — the PQ reference implementation and tuning notes
- The Week 4 files (03/04) — the primitives this file composes
- Stockhamer & Böhm, *Product Quantization* survey (skim §1–2) — the compression idea's origin
