# Deep-Dive: Agentic RAG with LangChain

Parent overview: [`../04-agentic-rag-langchain.md`](../04-agentic-rag-langchain.md)

The agentic RAG capstone in LangChain terms: three-source routing
(vector/SQL/web), sub-question decomposition, self-improving loops that
turn failure logs into eval cases, and the W13 graph-equivalence test
that proves the port.

## File map

| File | What it covers |
|---|---|
| [`01-three-source-routing.md`](01-three-source-routing.md) | Vector / SQL / web routing |
| [`02-decomposition.md`](02-decomposition.md) | Sub-question generation |
| [`03-self-improving-loops.md`](03-self-improving-loops.md) | Logs to eval sets |
| [`04-graph-parity.md`](04-graph-parity.md) | W13-01 equivalence testing |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-three-source-routing.md` — the routing, LangChain edition.
2. `02-decomposition.md` — multi-hop via sub-questions.
3. `03-self-improving-loops.md` — the eval set that grows itself.
4. `04-graph-parity.md` — same cases, W13 graph vs W14 chains.

## Prerequisites

- [`../01-langchain-foundations/`](../01-langchain-foundations/) — LCEL,
  typed outputs, `create_agent`.
- [`../../Week-12-Building-AI-Agents-with-phiData-Agno/05-agentic-rag-with-phidata/`](../../Week-12-Building-AI-Agents-with-phiData-Agno/05-agentic-rag-with-phidata/)
  — the three-power routing this mirrors.