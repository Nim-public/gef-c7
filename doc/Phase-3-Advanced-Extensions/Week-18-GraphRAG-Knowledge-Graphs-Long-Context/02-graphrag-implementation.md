# 02 — GraphRAG: Communities, Local & Global Search

> E2 index: [README.md](README.md)

**Core topic:** *The Microsoft GraphRAG approach — indexing pipeline (entity → community → summaries) and the two retrieval modes (local, global).*

---

## What you'll learn

- The GraphRAG indexing pipeline: extraction → entity graph → community detection → hierarchical summaries
- **Local search** (entity-anchored retrieval) and **global search** (map-reduce over community summaries)
- Building a working GraphRAG-lite over your corpus with networkx + your LLM stack
- Cost profile: why GraphRAG ingestion is expensive and how to budget it

## 1. The GraphRAG pipeline (Microsoft, 2024)

```
INGESTION:
  chunks ─► LLM entity/relation extraction (file 01) ─► entity graph
        ─► community detection (Leiden) ─► hierarchical communities
        ─► per-community LLM summaries (at multiple levels)

QUERY:
  LOCAL  ── entity in question ──► neighborhood + linked chunks ─► answer
  GLOBAL ── theme question ──────► map: ask every community summary ─► reduce: synthesize
```

The key innovation vs naive KG-RAG: **communities**. Leiden clustering groups densely-connected entities; an LLM writes a summary per community (and per meta-community, recursively). Global questions are answered *from the summaries* — a 300-report corpus compresses to ~20 community summaries that fit in context.

## 2. Building it (lite version over your corpus)

### Step 1 — graph (file 01) → communities

```python
import networkx as nx
import community as community_louvain      # pip install python-louvain

undirected = G.to_undirected()
communities = community_louvain.best_partition(undirected, resolution=1.0)

# attach community id to every node
for node, cid in communities.items():
    G.nodes[node]["community"] = cid
```

### Step 2 — community summaries (map step)

```python
def summarize_community(G, cid: int) -> str:
    members = [n for n, c in communities.items() if c == cid]
    edges = [(u, v, d["type"]) for u, v, d in G.edges(data=True)
             if u in members and v in members]
    r = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content":
                   f"Entities: {members[:40]}\nRelations: {edges[:60]}\n"
                   "Write a 150-word summary of the themes and connections in this group. "
                   "Be factual; only use the listed entities/relations."}])
    return r.choices[0].message.content
```

Summaries get embedded and indexed (W4-03) — global search is vector search *over community summaries*.

### Step 3 — global search (map-reduce)

```python
import numpy as np

def global_search(question: str, k: int = 5) -> str:
    summaries = {cid: summarize_community(G, cid) for cid in set(communities.values())}
    sembs = np.array([embed(s) for s in summaries.values()])         # W4 embedder
    q = embed([question])[0]
    top = np.argsort(-(sembs @ q))[:k]                                # map: pick relevant communities
    parts = [f"[community {i}] {summaries[i]}" for i in top]
    r = client.chat.completions.create(                               # reduce: synthesize
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content":
                   f"Summarize the answer to: {question}\n\n"
                   f"Community summaries:\n" + "\n\n".join(parts)}])
    return r.choices[0].message.content
```

This answers *"what are the main themes across all reports?"* — the question W4 top-k structurally cannot (file 01's failure table).

### Step 4 — local search (entity-anchored)

```python
def local_search(question: str, entity: str, k: int = 5) -> str:
    nb = entity_neighborhood(G, entity, depth=1)                      # file 01 §4
    edge_ctx = "\n".join(f"{u} -[{d['type']}]-> {v}: {d['evidence']}"
                         for u, v, d in nb["edges"][:20])
    chunk_ids = {c for n in nb["nodes"] for c in G.nodes[n].get("chunks", [])}
    texts = fetch_chunks(chunk_ids)[:k]                               # your W4 store
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content":
                   f"Graph context:\n{edge_ctx}\n\nText:\n" + "\n".join(texts) +
                   f"\n\nQuestion: {question}\nAnswer with graph-relation + text citations."}])
    return r.choices[0].message.content
```

## 3. Local vs global — the question-shape router

| Question | Mode | Cost profile |
|---|---|---|
| "How is Vendor-A connected to the lawsuit?" | local | 1 neighborhood + k chunks |
| "Main themes across the reports?" | global | k summary reads (cheap per summary) |
| "Summarize everything about Product-X" | local (its subgraph) | neighborhood + chunks |
| "Any compliance risks across all vendors?" | global | map-reduce |

W12-05's router (or the W13 graph) gains a third arm: `sql | vector | graph_local | graph_global`.

## 4. The cost story (why GraphRAG ingestion is expensive)

One LLM extraction call per chunk (file 01) + one summary call per community + meta-community recursion. For 1,000 chunks: ~1,000 extraction calls + ~20–50 summaries. Budget: extraction with a cheap model (gpt-4o-mini/SLM) at temperature 0, batched; re-extraction only on new/changed chunks (incremental, W4-05's resumability rule). Microsoft's published guidance: GraphRAG costs ~10–100× naive RAG at *ingest*, then queries are cheap — the cost moves from query-time to index-time, which is usually the right trade for stable corpora.

## Exercises

1. Build communities over your file 01 graph; report community count/sizes. Do the groupings match your mental model of the corpus?
2. Global search demo: 3 "main themes" questions — answer via map-reduce; compare against naive top-10 chunks + LLM. Which is more complete?
3. Local search demo: 3 entity questions — verify edge citations resolve to chunks (file 01's evidence audit, now end-to-end).
4. Cost ledger: count LLM calls for indexing 1,000 chunks (extraction + summaries) vs 1,000 queries (vector top-k vs graph local vs global). Write the trade paragraph for your capstone.
5. Incrementality: add 5 new chunks; re-extract only those; re-run community detection — which summaries must regenerate? (Hint: only communities whose membership changed.)

## Pitfalls

- **Community summaries hallucinating** — summaries are LLM text over extracted lists; constraint them to listed entities/relations only (§2's rule)
- **Re-running global search per question** — summaries are *index-time* artifacts; cache them (W15-04 caching, now at graph level)
- **One flat community level** — Leiden at one resolution misses hierarchy; multi-resolution summaries are the paper's point (meta-communities)
- **Graph staleness vs vector index** — new chunks extracted for graph but not embedded (or vice versa); one ingestion pipeline writes both (W9-02's discipline)
- **Global search over stale summaries** — regenerate summaries when their community's edges changed

## Resources

- Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* (Microsoft Research) — the paper; §II–III cover exactly files 01–02
- [microsoft/graphrag](https://github.com/microsoft/graphrag) — the reference implementation (CLI + API)
- Neo4j + LLM Graph Builder — the production graph-store path
- W6-02 (storage decisions), W4-05 (incremental ingestion), W13 (graphs as orchestration — contrast with graphs as data)
