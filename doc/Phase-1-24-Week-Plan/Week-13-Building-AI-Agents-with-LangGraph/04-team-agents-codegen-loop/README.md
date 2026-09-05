# Deep-Dive: Team Agents & the Codegen Loop

Parent overview: [`../04-team-agents-codegen-loop.md`](../04-team-agents-codegen-loop.md)

The self-repair graph — plan → write → test → debug, cycling with a
bound — plus sandbox discipline for generated code, the supervisor
topology for multi-worker teams, and the team-vs-single A/B.

## File map

| File | What it covers |
|---|---|
| [`01-self-repair-graph.md`](01-self-repair-graph.md) | Plan/write/test/debug cycle |
| [`02-sandbox-discipline.md`](02-sandbox-discipline.md) | Subprocess/container hardening |
| [`03-supervisor-topology.md`](03-supervisor-topology.md) | Routing workers |
| [`04-team-vs-single.md`](04-team-vs-single.md) | Measured A/B |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-self-repair-graph.md` — the cycle, with bounds.
2. `02-sandbox-discipline.md` — generated code never runs bare.
3. `03-supervisor-topology.md` — multiple workers, one router.
4. `04-team-vs-single.md` — is the team worth it? measure.

## Prerequisites

- [`../01-langgraph-foundations/03-cycles-and-bounds.md`](../01-langgraph-foundations/03-cycles-and-bounds.md)
  — the bounded cycle.
- [`../../Week-12-Building-AI-Agents-with-phiData-Agno/06-capstone-task-crewai-workflow/`](../../Week-12-Building-AI-Agents-with-phiData-Agno/06-capstone-task-crewai-workflow/)
  — the role-split ideas this topology re-expresses.
