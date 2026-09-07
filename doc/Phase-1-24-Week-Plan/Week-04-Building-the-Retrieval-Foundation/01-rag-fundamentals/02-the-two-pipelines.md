# 01.2 — The Two Pipelines

> Subfolder index: [README.md](README.md) · Parent: [../01-rag-fundamentals.md](../01-rag-fundamentals.md)

---

## What you'll learn

- The ingestion pipeline: every stage, its inputs/outputs, its failure modes
- The query pipeline: routing, retrieval, generation — and the seam between them
- The component contracts that make the system testable

## 1. Ingestion — offline, runs when data changes

```python
def ingest(sources: list[str]) -> dict:
    stats = {"docs": 0, "chunks": 0, "embedded": 0, "failed": 0}
    for src in sources:
        try:
            text = extract(src)                     # W1-04: PDF/HTML/CSV → text
            chunks = chunk(text)                    # W4-02: strategy + metadata
            embs = embed([c["text"] for c in chunks])   # W2-03: same model, always
            store(chunks, embs)                     # W4-03: LanceDB + BM25
            stats["chunks"] += len(chunks)
        except Exception as e:
            stats["failed"] += 1
            log_failure(src, e)                     # recorded, never swallowed
    return stats
```

Stage-by-stage contracts:

| Stage | Input | Output | Failure mode |
|---|---|---|---|
| extract | file path | text + metadata | empty text, encoding garbage |
| chunk | text | chunks with ids + metadata | wrong size, broken boundaries |
| embed | chunk texts | vectors | model mismatch, normalization drift |
| store | chunks + vectors | indexed | partial writes, index corruption |

The resumability invariant (W4-05's file): fingerprint each source; skip already-ingested; re-ingest changed content only.

## 2. Query — online, per question

```python
def answer(question: str, k: int = 5) -> dict:
    q_vec = embed_query(question)                    # same embedder, normalized
    hits = search(q_vec, k=k)                        # W4-03/W5-03: hybrid + rerank
    if not hits or hits[0]["score"] < THRESHOLD:
        return {"answer": "I don't have that information.", "hits": []}
    context = assemble_context(hits)                 # W4-01: delimited blocks
    reply = generate(context, question)              # W4-01: grounded prompt
    return {"answer": reply, "hits": hits, "citations": extract_citations(reply)}
```

The query-side contracts:

| Contract | Test |
|---|---|
| insufficiency escape fires on weak retrieval | the no-match battery (W4-01 ex. 5) |
| citations resolve to real chunks | the citation validator (W5-04) |
| context fits the budget | the token check before the call (W10-05) |
| same embedder at query time | the contract check (W4-03) |

## 3. The seam between the pipelines

The query pipeline consumes what ingestion produced — the seam is where drift enters (W4-03's mismatch rule). The seam contract:

- the embedder model id + revision (pinned, W2-01)
- the normalization flag (True everywhere)
- the chunk format (ids, text, metadata — the W4-02 schema)
- the corpus version (W16-01's versioning)

Change any of these → re-index (or at least re-verify). The E8-01 manifest records all four.

## Exercises

1. Build both pipelines over 20 documents; measure per-stage timing — the ingestion is amortized, the query is SLA-critical.
2. The seam-drift drill: change the embedder at query time only — measure the retrieval collapse; then fix and verify.
3. The failure injection: make extraction return empty text for 20% of documents — trace the impact through chunking, embedding, and retrieval.
4. The contract test suite: write tests for every stage's input/output contract — the W15-01 pyramid, ingestion edition.
5. The resumability drill: crash at chunk 60%; resume; verify no duplicates and no gaps (W4-05's invariant).

## Pitfalls

- **Ingestion and query pipelines drift** — different chunkers, embedders, or normalizers on each side; one shared config (W4-03's contract)
- **Stage outputs unchecked** — empty extraction → empty chunks → empty index; validate every stage's output (W15-01)
- **The seam undocumented** — the embedder/model/normalization triple must be pinned and shared (E8-01's manifest)
- **Failures swallowed in ingestion** — the failed 20% becomes the unsearchable 20%; report every failure (W4-05)
- **Query-side thresholds hardcoded** — the corpus changes, the thresholds should too; calibrate from the distance distribution (W4-03 ex. 5)

## Resources

- W4-02 (chunking), W4-03 (vector DB), W4-05 (the task that assembles this) — the components
- W1-04 (the extraction layer), W2-03 (embeddings) — the upstream skills
- W4-01 parent (the contract this pipeline implements)
