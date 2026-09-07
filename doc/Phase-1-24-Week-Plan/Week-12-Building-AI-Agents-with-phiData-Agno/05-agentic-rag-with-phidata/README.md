# Deep-Dive: Agentic RAG with phiData/Agno

Parent overview: [`../05-agentic-rag-with-phidata.md`](../05-agentic-rag-with-phidata.md)

Fixed RAG (retrieve-then-stuff) vs agentic RAG (the model decides whether
and what to retrieve): the decision analysis, the three-power agent, the
route-accuracy measurement against your W9 router, and the cost/quality
trade.

## File map

| File | What it covers |
|---|---|
| [`01-fixed-vs-agentic.md`](01-fixed-vs-agentic.md) | The decision analysis, per query class |
| [`02-three-power-agent.md`](03-three-power-agent.md) | Knowledge + SQL + web toolkit routing |
| [`03-route-accuracy.md`](03-route-accuracy.md) | Measuring the model's routing vs W9-04 |
| [`04-cost-quality-trade.md`](04-cost-quality-trade.md) | Token and latency tables |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-fixed-vs-agentic.md` — decide per query class, not per project.
2. `02-three-power-agent.md` — the routing design.
3. `03-route-accuracy.md` — measure what the router became.
4. `04-cost-quality-trade.md` — the tables that justify it.

## Prerequisites

- [`../02-knowledge-and-databases/01-knowledge-lancedb.md`](../02-knowledge-and-databases/01-knowledge-lancedb.md)
  and [`../02-knowledge-and-databases/03-grounding-rules.md`](../02-knowledge-and-databases/03-grounding-rules.md)
  — the knowledge layer and its battery.
- [`../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md`](../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md)
  — the router this file's model replaces.