# Deep-Dive: Tools and Memory

Parent overview: [`../02-tools-and-memory.md`](../02-tools-and-memory.md)

This subfolder builds the agent's two persistent organs: the tool layer
(function-calling protocol, validated registry, error contracts) and the
memory layer (four-tier taxonomy, context budgeting with measured costs).

## File map

| File | What it covers |
|---|---|
| [`01-function-calling.md`](01-function-calling.md) | Schema → decision → execute → observe |
| [`02-tool-registry.md`](02-tool-registry.md) | jsonschema validation, error contracts |
| [`03-memory-taxonomy.md`](03-memory-taxonomy.md) | History / scratchpad / episodic / semantic |
| [`04-context-budgeting.md`](04-context-budgeting.md) | Truncation, compression, per-layer costs |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-function-calling.md` — the protocol under every framework.
2. `02-tool-registry.md` — validation and errors as contracts.
3. `03-memory-taxonomy.md` — what the agent remembers, and where.
4. `04-context-budgeting.md` — the token ledger that bounds everything.

## Prerequisites

- [`../01-agents-foundations/`](../01-agents-foundations/) — the loop that
  consumes tools and memory.
- [`../../Week-09-RAG-with-Image-Video-Audio/04-end-to-end-multimodal-rag/02-hybrid-retrieval.md`](../../Week-09-RAG-with-Image-Video-Audio/04-end-to-end-multimodal-rag/02-hybrid-retrieval.md)
  — the tools being registered.
