# 03 — Embeddings & Vector Databases: Deep Dive

> Parent topic: [../03-embeddings-vector-databases.md](../03-embeddings-vector-databases.md) · Week 4 index: [../README.md](../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-brute-force-baseline.md](01-brute-force-baseline.md) | NumPy search, the ground truth | 2 h |
| 2 | [02-faiss-indexes.md](02-faiss-indexes.md) | Flat, IVF, nprobe sweeps, recall measurement | 3 h |
| 3 | [03-lancedb-production.md](03-lancedb-production.md) | Tables, filters, metadata, persistence | 3 h |
| 4 | [04-query-time-checklist.md](04-query-time-checklist.md) | The consistency contract, thresholds | 2 h |
| — | [exercises.md](exercises.md) | Labs with worked approaches | 3 h |

## File map

- **01** — the brute-force baseline that defines correctness; the memory/latency limits
- **02** — FAISS: flat vs IVF, the nprobe dial, the recall measurement protocol
- **03** — LanceDB: tables, prefilter security, persistence, the metadata lifecycle
- **04** — the query-time checklist that prevents the silent bugs
- **exercises.md** — labs including the drift drill and the security test
