# Deep-Dive: LangGraph Foundations

Parent overview: [`../01-langgraph-foundations.md`](../01-langgraph-foundations.md)

LangGraph is the explicit-graph framework: state as a typed schema,
nodes as functions, edges as wiring, cycles as first-class citizens.
This subfolder covers state design with reducers, node/edge wiring,
bounded cycles, and how to read an execution.

API verified against context7 id `/websites/langchain_oss_python_langgraph`.

## File map

| File | What it covers |
|---|---|
| [`01-state-design.md`](01-state-design.md) | TypedDict, Pydantic, reducers |
| [`02-nodes-and-edges.md`](02-nodes-and-edges.md) | Normal and conditional wiring |
| [`03-cycles-and-bounds.md`](03-cycles-and-bounds.md) | Retry counters, exit conditions |
| [`04-invoke-stream-inspect.md`](04-invoke-stream-inspect.md) | Execution path reading |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-state-design.md` — the state *is* the contract.
2. `02-nodes-and-edges.md` — the wiring.
3. `03-cycles-and-bounds.md` — loops that terminate.
4. `04-invoke-stream-inspect.md` — reading what ran.

## Prerequisites

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/`](../../Week-10-Introduction-to-Agentic-AI-MCP/)
  — the loop your graph replaces.
- [`../02-knowledge-and-databases/04-dual-pipeline.md`](../02-knowledge-and-databases/04-dual-pipeline.md)
  on the W12 branch — same tools, graph-wired.
