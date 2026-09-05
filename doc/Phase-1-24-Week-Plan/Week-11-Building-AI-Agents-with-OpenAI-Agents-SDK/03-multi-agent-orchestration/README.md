# Deep-Dive: Multi-Agent Orchestration

Parent overview: [`../03-multi-agent-orchestration.md`](../03-multi-agent-orchestration.md)

Three orchestration topologies (handoff, chaining, delegation), how state
crosses agent boundaries, and the anti-patterns that turn a system of
specialists into a token centrifuge.

## File map

| File | What it covers |
|---|---|
| [`01-handoff-pattern.md`](01-handoff-pattern.md) | Router → specialist topology |
| [`02-chaining.md`](02-chaining.md) | Sequential refinement with typed outputs |
| [`03-delegation.md`](03-delegation.md) | Manager with agents-as-tools |
| [`04-state-passing.md`](04-state-passing.md) | Context, outputs, summaries across boundaries |
| [`05-anti-patterns.md`](05-anti-patterns.md) | Ping-pong, spirals, bloat — with detectors |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-handoff-pattern.md` — the topology your router already implies.
2. `02-chaining.md` — pipelines as typed agent chains.
3. `03-delegation.md` — sub-agents as tools; the fork from handoffs.
4. `04-state-passing.md` — what crosses the boundary, what never does.
5. `05-anti-patterns.md` — the failure catalog, with trace detectors.

## Prerequisites

- [`../02-tools-handoffs-guardrails/02-handoffs.md`](../02-tools-handoffs-guardrails/02-handoffs.md)
  — the mechanics all three topologies build on.
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/04-when-not-agents.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/04-when-not-agents.md)
  — the boundary discipline, now per-agent.
