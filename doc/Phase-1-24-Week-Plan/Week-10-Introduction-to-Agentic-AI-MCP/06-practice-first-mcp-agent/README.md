# Deep-Dive: Practice — Your First MCP Agent

Parent deliverable spec: [`../06-practice-first-mcp-agent.md`](../06-practice-first-mcp-agent.md)

The parent defines the deliverable, eval set, red-team integration, and
metrics table. This subfolder is the build guide: assembling the full
agent (loop + registry + MCP tools), the 10-task eval set with expected
routes, the injection battery crossing tool outputs, and the harness
table everything reports into.

## File map

| File | What it covers |
|---|---|
| [`01-agent-assembly.md`](01-agent-assembly.md) | Loop + registry + MCP client wiring |
| [`02-eval-set-design.md`](02-eval-set-design.md) | 10 tasks with expected routes |
| [`03-red-team-via-tools.md`](03-red-team-via-tools.md) | Injection through tool outputs |
| [`04-metrics-table.md`](04-metrics-table.md) | The harness output, per dimension |
| [`exercises.md`](exercises.md) | Stretch tasks and the self-review rubric |

## Build order

1. `01-agent-assembly.md` — the parts exist; this is the wiring.
2. `02-eval-set-design.md` — 10 tasks, gold-labeled, before any run.
3. `03-red-team-via-tools.md` — the W9 battery, escalated.
4. `04-metrics-table.md` — one command, one table, the week's evidence.

## Prerequisites

- All five prior subfolders — every component exists and is tested.
- [`../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/03-router-safety.md`](../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/03-router-safety.md)
  — the battery this week extends.
