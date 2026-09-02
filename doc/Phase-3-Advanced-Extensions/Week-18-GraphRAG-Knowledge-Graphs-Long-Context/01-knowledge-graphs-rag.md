# 01 — Knowledge Graphs for RAG

> E2 index: [README.md](README.md)

**Core topic:** *Knowledge graphs basics, entity/relation extraction from your corpus, and why graphs answer questions vectors can't.*

---

## What you'll learn

- KG primitives: entities, relations, properties — and the schema-first vs open extraction choice
- Building a KG from your corpus with an LLM extractor
- The graph operations that answer multi-hop questions (paths, neighborhoods, aggregations)
- Vector failure modes that motivate the graph

## 1. The vector failure modes (from your own stack)

W4's top-k retrieves *similar text*. Three question classes it structurally fails:

| Failure | Example | Why |
|---|---|---|
| **Multi-hop** | "Which vendor in our contract also appears in the lawsuit?" | answer = connection *between* two chunks, not one chunk |
| **Global summary** | "What are the main themes across all 300 reports?" | no single chunk holds the answer; top-k returns 300 |
| **Aggregation over relations** | "How many entities connect billing to legal?" | relations are implicit in text, not stored |

A **knowledge graph** stores entities (`Vendor-A`, `Lawsuit-2025`, `Refund-Policy`) as nodes and typed relations (`SUES`, `MENTIONED_IN`, `GOVERNED_BY`) as edges — making connections *queryable* instead of *hoped-for*.

## 2. Building the graph from your corpus

### The extraction prompt (schema-guided)

```python
EXTRACT_PROMPT = """Extract entities and relations from this text.

Entity types: {entity_types}
Relation types: {relation_types}

Return JSON: {{"entities": [{{"name": "...", "type": "...", "mentions": ["exact text"]}}],
               "relations": [{{"source": "...", "target": "...", "type": "...", "evidence": "..."}}]}}

Rules: entity names exactly as written in the text; every relation cites its evidence span;
no invented entities.

Text:
{chunk}"""
```

```python
import json

def extract_chunk(chunk_text: str) -> dict:
    r = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content":
                   EXTRACT_PROMPT.format(chunk=chunk_text,
                                         entity_types="Person|Org|Product|Policy|Location",
                                         relation_types="SUPPLIES|SUED_BY|GOVERNED_BY|MENTIONED_IN|PART_OF")}])
    return json.loads(r.choices[0].message.content)
```

Two design choices:

- **Schema-guided** (fixed types above) — consistent, queryable, misses the unexpected; the production default
- **Open extraction** (no types) — richer, messier; needs normalization/dedup passes (LLM merges "Vendor A"/"ACME Corp")

Every relation carries `evidence` (the source text + chunk id) — the citation layer (W4-01) extends to graphs: answers cite the *edges* that support them.

## 3. The graph store: networkx to start, graph DBs to scale

```python
import networkx as nx

G = nx.MultiDiGraph()

def add_extraction(G, ex: dict, chunk_id: str):
    for e in ex["entities"]:
        if not G.has_node(e["name"]):
            G.add_node(e["name"], type=e["type"], chunks=[chunk_id])
        G.nodes[e["name"]]["chunks"] = G.nodes[e["name"]].get("chunks", []) + [chunk_id]
    for r in ex["relations"]:
        G.add_edge(r["source"], r["target"], type=r["type"],
                   evidence=r["evidence"], chunk=chunk_id)
```

Scale path: networkx (≤ ~100k edges, single process) → **Neo4j** (Cypher queries, production) → **NebulaGraph/Neptune**. The W6-02 decision pattern applies — embedded/simple first, server when multi-user writes demand it.

## 4. Graph operations = retrieval

```python
def entity_neighborhood(G, entity: str, depth: int = 1) -> dict:
    """Local search: everything connected to an entity (GraphRAG 'local' search seed)."""
    if entity not in G: return {"nodes": [], "edges": []}
    nodes = nx.ego_graph(G.to_undirected(), entity, radius=depth)
    return {"nodes": list(nodes.nodes), "edges": list(nodes.edges(data=True))}

def multi_hop(G, a: str, b: str, max_len: int = 3) -> list:
    """All paths connecting two entities — the multi-hop answer."""
    try:
        return list(nx.all_simple_paths(G.to_undirected(), a, b, cutoff=max_len))
    except nx.NodeNotFound:
        return []

def co_occurrence(G, type_a: str, type_b: str) -> list:
    """Entities of type A connected (transitively) to entities of type B."""
    a_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == type_a]
    return [n for a in a_nodes for n in nx.descendants(G.to_undirected(), a)
            if G.nodes[n].get("type") == type_b]
```

The failure-mode table, answered:

| Question class | Graph operation |
|---|---|
| multi-hop ("vendor ↔ lawsuit") | `multi_hop(a, b)` + edge evidence |
| entity-centric detail | `entity_neighborhood(entity)` |
| relation counting ("how many Orgs connect to Legal") | `co_occurrence` + count |
| global themes | community summaries (file 02) |

## 5. Hybrid: graph edges point back to text

Every node/edge stores its `chunks` — so graph retrieval *seeds* vector retrieval: find the connection in the graph, then retrieve the underlying chunks for grounded generation. The graph never replaces the corpus; it indexes *relationships over* it (W6-02's storage map gains a third store).

## Exercises

1. Extract entities/relations from 20 of your capstone chunks (schema-guided); report entity/type counts and 3 relations you didn't know were in the text.
2. Entity resolution pass: merge "Acme Corp"/"Acme Corporation"/"ACME" — write the alias map + merge function; report the pre/post node counts.
3. Multi-hop demo: answer the vendor/lawsuit-class question via `multi_hop` — then try it with W4 vector top-k. Show both answers.
4. Evidence audit: pick 5 edges; verify each `evidence` string appears in its cited chunk. What's your extraction hallucination rate?
5. Cost model: extraction LLM calls per 1,000 chunks (tokens in/out) — at what corpus size does KG construction need batching/cheaper models?

## Pitfalls

- **Extraction hallucination without evidence fields** — invented edges are worse than missing ones; require + verify `evidence`
- **Entity fragmentation** — "MSFT"/"Microsoft" as two nodes; alias maps and LLM-merge passes are mandatory at scale
- **Chunk-ids lost** — edges without `chunk` citations can't be grounded in answers (W4-01's contract)
- **Graph for everything** — "when was X shipped" is SQL/vec question; graph answers *connections* (W6-04's tree gains a branch)
- **Extraction cost per corpus update** — incremental extraction per new chunk, not whole-corpus rebuilds

## Resources

- Edge et al., *From Local to Global: A Graph RAG Approach* (Microsoft) — the GraphRAG paper (file 02's source)
- Neo4j [LLM Knowledge Graph Builder](https://neo4j.com/labs/genai-ecosystem/) — production extraction patterns
- networkx [docs](https://networkx.org/documentation/stable/) — your first graph store
- LangChain [graph transformers](https://python.langchain.com/docs/how_to/#graphs) — LLMGraphTransformer reference
