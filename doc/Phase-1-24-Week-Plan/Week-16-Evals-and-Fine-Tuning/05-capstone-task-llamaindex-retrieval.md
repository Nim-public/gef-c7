# 05 — Weekly Task: LlamaIndex-Powered Retrieval in Your Capstone

> Week 16 index: [README.md](README.md) · **Due: before Week 17 (capstone phase kickoff)**

**Task (from the schedule):** *Implement a LlamaIndex-powered retrieval system within your capstone project.*

The formal task adds the final retrieval framework — LlamaIndex — to your capstone, reusing your corpus, eval harness, and production layers. The deliverable is not "LlamaIndex for its own sake": it's a *measured* comparison against your W4–5 engine and a decision about what the capstone ships.

---

## 1. Deliverable

```
llamaindex/
  ingest.py              # LlamaIndex ingestion: readers → nodes → index (over your corpus)
  retrieval.py           # query engine(s) + your W4/W5 engine behind one interface
  eval/
    results.md           # comparison table on the shared harness
  README.md              # integration decisions
```

Demo: the same 10 questions answered through (a) your W4/W5 engine and (b) LlamaIndex — with retrieval scores and citations from each.

## 2. LlamaIndex essentials

```powershell
pip install llama-index llama-index-embeddings-huggingface
```

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = None                                  # retrieval-only this week (your LLM stack stays)

docs = SimpleDirectoryReader("data/raw").load_data()
index = VectorStoreIndex.from_documents(docs)        # parse → chunk (nodes) → embed → store
qe = index.as_query_engine(similarity_top_k=5)
resp = qe.query("What is the refund timeline?")
print(resp.response)
for n in resp.source_nodes:                          # cited nodes = your citation layer
    print(n.score, n.metadata.get("file_name"), n.text[:80])
```

Concept mapping (nothing new — repackaged):

| LlamaIndex | Your W4–6 concept |
|---|---|
| `SimpleDirectoryReader` | W1-04 parsers |
| Node parser | W4-02 chunker |
| `Settings.embed_model` | W5-02 embedder (pin it!) |
| `VectorStoreIndex` | W4-03 index (LanceDB integrations exist) |
| `as_query_engine` | W4-01 grounded answer (includes an LLM synthesis step!) |
| `similarity_top_k` | top-k (W4-03) |

Note the default: `query_engine` includes its own LLM answer generation — use `index.as_retriever()` for retrieval-only parity with your harness, and the query engine where you want its synthesis.

## 3. Requirements (graded)

### Integration
- [ ] LlamaIndex ingestion over ≥ your W4 corpus, with **your** embedder + chunk-size settings (Settings-level, not defaults)
- [ ] Retrieval-only interface: same dict contract as `search_knowledge` (W9-05) so both engines sit behind one interface
- [ ] Postprocessors wired where you had them (reranker, metadata filters — LlamaIndex node postprocessors)

### Evaluation (the shared harness decides)
- [ ] Same 25-query W4-05 harness run against **both** engines (LlamaIndex retriever vs your hybrid)
- [ ] Table: hit rate @5, MRR, p95 latency, index size, ingest time — per engine
- [ ] Ragas spot-check (10 answers) if using the query-engine path (W5-05)

### Decision (README)
- [ ] Ship, adopt partially, or reject LlamaIndex for the capstone — with the table as evidence
- [ ] Production layers inherited: budgets, tracing, caching, routing from W15 (the new system must not bypass them)

## 4. Rubric

| Area | Weight |
|---|---|
| LlamaIndex ingestion + retrieval (Settings pinned, not defaults) | 25% |
| Shared-interface integration (one contract, two engines) | 20% |
| Harness comparison table (honest, same queries) | 30% |
| Ship/adopt/reject decision + rationale | 15% |
| Production-layer inheritance note | 10% |

## 5. README decision section (answer explicitly)

1. **Comparison table** (§3) with per-engine notes on chunking differences observed (LlamaIndex's node parser vs your W4-02 strategy — *same corpus, different chunk counts*; explain why)
2. **Framework position**: where LlamaIndex beats your stack (connectors? index types? speed of iteration?) and where yours wins (your metadata model, your hybrid, your production layers)
3. **Ship decision**: what the capstone's final retrieval architecture is, with the evidence
4. **Inherited production layers**: budget/tracing/routing wired into the new path (or explicitly not, and why)
5. **Capstone readiness** (file 06 checklist referenced): retrieval architecture final, eval harness final, demo path final

## 6. Stretch (pick one)

- LlamaIndex on LanceDB (`LanceDBVectorStore` integration) — your W9 store, index-agnostic retrieval; rerun the harness
- Router query engine: LlamaIndex's router choosing between your SQL tool and vector retrieval (W12-05, framework edition)
- Sub-question query engine: compound questions decomposed and answered per-source (W5-03 fusion, LlamaIndex edition)

Office Hours (31 Dec): bring the comparison table and the ship decision — this is the last checkpoint before the capstone phase freezes architecture.
