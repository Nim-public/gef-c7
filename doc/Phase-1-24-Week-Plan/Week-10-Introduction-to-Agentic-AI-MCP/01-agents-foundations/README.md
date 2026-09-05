# Deep-Dive: Agents Foundations

Parent overview: [`../01-agents-foundations.md`](../01-agents-foundations.md)

This subfolder defines the agent precisely (one control-flow transfer
away from a pipeline), builds the ReAct loop in 50 traced lines, walks
three trajectories you can predict before running, and draws the boundary
where agents are the wrong tool.

## File map

| File | What it covers |
|---|---|
| [`01-agent-definition.md`](01-agent-definition.md) | Loop, tools, memory, control-flow transfer |
| [`02-hand-rolled-react.md`](02-hand-rolled-react.md) | The 50-line ReAct implementation, traced |
| [`03-demo-trajectories.md`](03-demo-trajectories.md) | Single-tool, multi-tool, impossible tasks |
| [`04-when-not-agents.md`](04-when-not-agents.md) | The pipeline boundary, with a decision test |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-agent-definition.md` — the definition that separates agents from pipelines.
2. `02-hand-rolled-react.md` — build the loop; never treat it as magic.
3. `03-demo-trajectories.md` — predict, then verify, three trajectories.
4. `04-when-not-agents.md` — decide *before* building.

## Prerequisites

- Week 04/09 (retrieval as a tool), Week 09 (tool contract).
- [`../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/03-router-safety.md`](../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/03-router-safety.md)
  — the injection battery this week extends to tools.
