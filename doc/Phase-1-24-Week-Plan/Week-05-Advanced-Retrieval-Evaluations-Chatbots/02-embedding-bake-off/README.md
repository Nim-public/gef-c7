# 02 — Embedding Bake-off: Deep Dive

> Parent topic: [../02-embedding-models.md](../02-embedding-models.md) · Week 5 index: [../../README.md](../../README.md)

**File map:**

- [01-dense-models.md](01-dense-models.md) — the local model comparison
- [02-api-and-sparse.md](02-api-and-sparse.md) — OpenAI/Cohere embedders, ELSER sparse
- [03-the-bake-off.md](03-the-bake-off.md) — the protocol and the prefix traps
- [exercises.md](exercises.md) — labs

## Key content from the parent topic

The W5-02 bake-off compares embedding models on **your corpus** with **your eval set** — the only comparison that matters. Key rules: same chunks across models (one variable), prefix requirements per model (E5/BGE), normalization consistency, and per-model re-indexing.

| Model | Dim | Prefix needed | Notes |
|---|---|---|---|
| all-MiniLM-L6-v2 | 384 | no | fast default |
| BAAI/bge-small-en-v1.5 | 384 | query instruction | strong in class |
| intfloat/e5-base-v2 | 768 | "query:"/"passage:" | prefix mandatory |
| OpenAI text-embedding-3-small | 1536 | no | API, per-token cost |
| ELSER | sparse | no | Elastic; learned term expansion |

The bake-off table (from the parent's protocol) reports: hit rate @5, MRR, tokens/s, memory, and the degradation map per slice. The winner is pinned with `revision=` and recorded in the E8-01 manifest.

For the full implementation, protocols, and pitfall catalog, see the parent file and the W5-02 exercises.
