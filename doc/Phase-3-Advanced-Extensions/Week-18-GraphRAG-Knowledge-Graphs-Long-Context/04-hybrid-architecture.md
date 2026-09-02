# 04 — Hybrid Architecture: Vector + Graph + SQL Behind One Router

> E2 index: [README.md](README.md)

**Core topics:** *The three-brain retrieval architecture — routing, fusion, and citation across vector, graph, and SQL stores.*

---

## What you'll learn

- The complete retrieval architecture your capstone can grow into: three stores, one router, one citation contract
- Router design for four retrieval arms (rules → classifier → agentic, from W12-05/W14-04)
- Fusion across heterogeneous results (RRF generalized, W4-04)
- The unified citation format that survives multi-store answers

## 1. The architecture

```
                       question
                          │
                    [router]  (rules → classifier → agent, W12-05)
        ┌─────────────┬────┴────────┬─────────────┐
        ▼             ▼             ▼             ▼
   vector (W4/W5)  graph (E2)   SQL (W6)     long-context (E2-03)
   chunks+meta     entities/     tables        whole-doc paste
        │             edges         │             │
        └─────────────┴──────┬──────┴─────────────┘
                             ▼
                    [fusion + dedup]  (RRF, cross-store)
                             ▼
                grounded generation + unified citations (W4-01)
```

Each store answers the question class it's shaped for (W6-04's tree, W18-01's failure table):

| Store | Question class | Example |
|---|---|---|
| Vector | prose/similarity | "how do I reset my password" |
| Graph | connections/multi-hop/global themes | "how are vendors connected to lawsuits"; "main themes" |
| SQL | aggregation/comparison | "top regions by revenue this quarter" |
| Long-context paste | single-doc deep dives | "summarize this 80-page contract" |

## 2. The router (three maturity levels, from W12-05)

```python
def route(question: str) -> list[str]:
    # L1: rules (deterministic, cheap)
    if re.search(r"\b(how many|total|sum|count|average|top \d+)\b", question, re.I):
        return ["sql"]
    if re.search(r"\b(connected|related to|relationship|between .+ and)\b", question, re.I):
        return ["graph"]
    # L2: zero-shot classifier (W2-02) over the four arms
    # L3: agent decides dynamically (W14-04's agentic RAG)
```

Production guidance: **L1 rules for the 60%** (deterministic, testable), **L2 classifier for the tail**, **L3 agentic only for genuinely open questions** — the W3-05 ladder, instantiated. Every routing decision is logged (W10-04) — route accuracy is a metric (W12-05 §4).

## 3. Fusion across heterogeneous stores

RRF (W4-04) fuses *ranked lists* regardless of what produced them — vector hits, graph neighborhoods, SQL rows. Each store's results are normalized to a common result shape first:

```python
def to_result(store: str, item: dict, rank: int) -> dict:
    if store == "vector":
        return {"id": item["id"], "kind": "chunk", "text": item["text"],
                "source": item["source"], "score": item.get("rerank_score")}
    if store == "graph":
        return {"id": f"edge:{item['u']}->{item['v']}", "kind": "relation",
                "text": f"{item['u']} -[{item['type']}]-> {item['v']}: {item['evidence']}",
                "source": item["chunk"], "score": None}
    if store == "sql":
        return {"id": f"row:{hash(str(item))}", "kind": "data",
                "text": str(item), "source": "database", "score": None}
```

Then RRF over the per-store rankings (W4-04's function), with **dedup by id** and a `kind` field the generation prompt uses to attribute ("From documents: … From the graph: … From the database: …").

## 4. The unified citation contract

Multi-store answers must cite *all* sources with one format:

```text
The refund window is 5 business days [handbook §4.2], and we processed 47 refunds
last quarter [sql: SELECT COUNT(*) …]. Vendor-A is linked to the 2025 lawsuit
through its parent company [graph: Vendor-A -[PARENT_OF]-> Acme Holding].
```

Generation prompt rules (W4-01 extended):

```python
CITATION_RULES = """
- Cite chunk results as [doc:id]
- Cite graph relationships as [graph: edge description]
- Cite database results as [sql: the executed query]
- Every factual claim must carry exactly one citation of its originating store."""
```

The `qa_check` node (W13-03) validates all three citation forms — one checker, three patterns.

## 5. When NOT to fuse

Fusion adds latency and citation complexity. Route to a **single arm** when:

- The router is confident (one arm scores far above others — W1-07 logprobs as confidence)
- The question is purely one class (pure SQL aggregation needs no vector hits)
- Latency budget < 1.5 s (fusion's synthesis call adds a stage)

The router returns the *arms*, not just the winner — `["sql"]` single-arm routing is the common case; multi-arm fusion is the escalation.

## Exercises

1. Build the router L1 rules for your capstone; measure route accuracy on 30 questions (W6-04 harness extended to 4 arms).
2. Implement `to_result` + RRF fusion across vector+graph+SQL on 5 multi-source questions; compare fused answers vs single-arm answers.
3. Citation-format audit: 10 fused answers — every claim cited, correct store format? Build the `qa_check` validator for all three patterns.
4. Latency budget: measure per-arm latencies and the fused pipeline p95. Where's the budget gone — and which arm would you cut first for a 2 s SLA?
5. Conflict resolution: vector and SQL "disagree" (doc says 5-day refunds; table shows 12-day average processing). How should the answer handle it? Write the conflict rule + test it.

## Pitfalls

- **Fusion as default** — multi-arm fusion on every question doubles latency for questions one arm answers perfectly (§5)
- **Store drift** — graph edges extracted from chunks the vector index no longer contains; one ingestion pipeline owns all stores (W9-02/W18-01)
- **Cross-store citation confusion** — users can't audit `[sql:…]` without the query; surface queries and edge evidence in the UI (W16-06 explanation levels)
- **Router rules rot** — the L1 regexes encode last quarter's question shapes; refresh from logged questions (W12-05's feedback loop)
- **Over-claiming fusion gains** — measure fused vs best-single-arm on your harness before shipping the complexity

## Resources

- Microsoft GraphRAG docs (E2-02) + W6-04/W12-05 (routing) + W4-04 (RRF) — the composed pieces
- LangGraph [adaptive RAG](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/) — the graph-orchestrated version of this router (W13's `add_conditional_edges` on `route_question`)
- W15-04 (routing cost model) — the optimization layer on top
- Anthropic, *Building effective agents* — the routing pattern this architecture generalizes
