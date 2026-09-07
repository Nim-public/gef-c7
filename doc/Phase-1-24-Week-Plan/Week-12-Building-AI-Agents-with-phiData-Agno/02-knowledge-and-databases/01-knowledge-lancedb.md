# Knowledge + LanceDB — Hybrid Search and Rerankers, Wrapped

**What you'll learn:** Agno's `Knowledge` object over your existing
LanceDB tables: the constructor surface, `SearchType` options, reranker
pluggability, and how agentic RAG (`search_knowledge=True`) differs from
fixed retrieval.

## 1. The constructor, against your W09 stack

```python
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.reranker.cohere import CohereReranker
from agno.vectordb.lancedb import LanceDb, SearchType

knowledge = Knowledge(
    vector_db=LanceDb(
        uri="data/lancedb",
        table_name="units",                 # your W09 table
        search_type=SearchType.hybrid,      # vector + FTS, your W9-04 choice
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        reranker=CohereReranker(model="rerank-v3.5"),   # optional refinement
    ),
)
agent = Agent(model=..., knowledge=knowledge, search_knowledge=True)
```

| `Knowledge` option | Your W09 equivalent |
|---|---|
| `LanceDb(uri, table_name)` | your `units` table |
| `SearchType.vector` | pure dense (W9 sweeps' baseline) |
| `SearchType.hybrid` | vector + FTS fused (W9 file 04) |
| `reranker` | your ITM/refine layer, pluggable |
| `embedder` | your encoder choice (the W8 memo) |

The wrap is real: same engine, same table — the parity check from the
migration drill (W12 file 01) applies. Agno adds the *agent-facing*
plumbing: `search_knowledge=True` makes retrieval a tool the model can
choose to call (agentic RAG), rather than a fixed pre-step.

## 2. Fixed vs agentic retrieval, at the Knowledge level

| Mode | Mechanism | Cost profile |
|---|---|---|
| fixed (pre-step) | retrieve top-k, inject into context | 1 retrieval, always |
| agentic (`search_knowledge=True`) | the model decides *whether/what* to search | 0–n retrievals, model-chosen |
| KnowledgeTools | think/search/analyze sub-tools | agentic + reasoning trail |

```python
# agentic with a reasoning trail:
from agno.tools.knowledge import KnowledgeTools
kt = KnowledgeTools(knowledge=knowledge, enable_think=True,
                    enable_search=True, enable_analyze=True)
agent = Agent(model=..., tools=[kt], markdown=True)
```

The W12-05 file is the decision analysis; this file is the plumbing.
The one-line version: agentic retrieval trades a fixed cost for a
*variable* cost with a routing decision inside — measure before
preferring it (file 05's comparison).

## 3. Schema and embedding parity (the silent killers)

| Risk | Symptom | Control |
|---|---|---|
| embedder mismatch vs your indexed vectors | retrieval "works", hits are wrong | embedder id pinned = W8 memo's encoder |
| chunking differs from your W7 settings | hybrid scores incomparable | ingest through your manifest pipeline, or re-index via Agno and re-sweep |
| table name collision | silent reuse of old vectors | version-suffixed table names (W9-04 stamping) |

```python
# verify the wrap: same queries, both stacks
for q in GOLDEN_QUERIES:
    a = my_hybrid_search(q, k=5)                 # your W9 function
    b = knowledge.search(query=q, k=5)           # Agno's call
    assert [h.unit_id for h in a] == [r.unit_id for r in b]
```

The parity loop is the acceptance test for the whole wrap — retrieval
behavior must be identical or the difference gets a name and a decision.

## 4. Rerankers as configuration, not code

```python
reranker=CohereReranker(model="rerank-v3.5")
# or a custom reranker implementing the same interface over your ITM head
```

Your W11 rerank experiment (retrieve-then-rerank) becomes a constructor
argument — the *policy* (rerank top-K only) stays yours, documented in
the same decision memo. The pluggable interface is where your W8 BLIP-ITM
work can re-enter as a custom reranker.

## Exercises

1. Wrap your corpus in `Knowledge` with hybrid search; run the §3 parity
   loop on 5 golden queries; document any hit-order differences.
2. SearchType sweep: vector vs hybrid on your 25-query set (through the
   same agent); R@5 both ways — Agno edition of the W9 sweep.
3. Reranker A/B: no reranker vs Cohere (or your ITM) on the chart-query
   class; report R@1 delta and added latency.

## Pitfalls

- Different embedder ids between your W09 index and the `Knowledge`
  constructor — vectors and queries in different spaces; parity loop
  catches it in one run.
- Trusting `search_knowledge=True` to always retrieve — the model may
  skip the tool; the insufficiency battery (file 03) exists for exactly
  this.
- Re-indexing through Agno with different chunking — your W7 settings
  version discipline applies; keep one ingest path or version-stamp both.

## Resources

- Agno knowledge docs: LanceDb, SearchType, rerankers, KnowledgeTools
  (context7: `/agno-agi/docs`).
- [`../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/04-hybrid-search.md`](../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/04-hybrid-search.md)
  — the fusion semantics `SearchType.hybrid` mirrors.