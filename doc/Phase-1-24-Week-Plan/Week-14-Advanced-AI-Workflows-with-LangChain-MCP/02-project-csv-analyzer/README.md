# Deep-Dive: Project — CSV Analyzer

Parent overview: [`../02-project-csv-analyzer.md`](../02-project-csv-analyzer.md)

The CSV analyzer is the classic data-intake agent: profile/pandas/chart
tools with guards, sandboxed execution, four user-facing features, and
numeric grounding checks — the Week 06 lesson, agent-shaped.

## File map

| File | What it covers |
|---|---|
| [`01-tool-surface.md`](01-tool-surface.md) | profile / pandas / chart tools with guards |
| [`02-sandbox-discipline.md`](02-sandbox-discipline.md) | Restricted eval, malicious probes |
| [`03-four-features.md`](03-four-features.md) | Chat / summary / analyze / visualize wiring |
| [`04-numeric-grounding.md`](04-numeric-grounding.md) | `numbers_supported` checks |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-tool-surface.md` — the three tools and their guards.
2. `02-sandbox-discipline.md` — user data + model code, sandboxed.
3. `03-four-features.md` — the four features as one surface.
4. `04-numeric-grounding.md` — numbers that check themselves.

## Prerequisites

- [`../01-langchain-foundations/`](../01-langchain-foundations/) — LCEL
  and `create_agent`.
- [`../../Week-13-Building-AI-Agents-with-LangGraph/04-team-agents-codegen-loop/02-sandbox-discipline.md`](../../Week-13-Building-AI-Agents-with-LangGraph/04-team-agents-codegen-loop/02-sandbox-discipline.md)
  — the sandbox this project hardens further.
