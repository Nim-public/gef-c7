# Deep-Dive: Agents SDK Quickstart

Parent overview: [`../01-agents-sdk-quickstart.md`](../01-agents-sdk-quickstart.md)

This subfolder maps the SDK you hand-rolled in Week 10 onto the OpenAI
Agents SDK primitives: Agent/Runner/RunResult anatomy, the documented
4-step loop, Pydantic structured outputs, SQLite sessions, and the trace
model. API surface verified against context7 id
`/websites/openai_github_io_openai-agents-python`.

## File map

| File | What it covers |
|---|---|
| [`01-sdk-anatomy.md`](01-sdk-anatomy.md) | Agent / Runner / RunResult fields, mapped to W10 |
| [`02-loop-mechanics.md`](02-loop-mechanics.md) | The 4 documented loop steps, max_turns, handlers |
| [`03-structured-output.md`](03-structured-output.md) | output_type, Pydantic, strict JSON schema |
| [`04-sessions.md`](04-sessions.md) | SQLiteSession persistence across turns |
| [`05-tracing.md`](05-tracing.md) | Spans, dashboards, local export |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-sdk-anatomy.md` — the mapping table from your hand-rolled agent.
2. `02-loop-mechanics.md` — the loop you wrote, documented and official.
3. `03-structured-output.md` — typed finals instead of string parsing.
4. `04-sessions.md` — history persistence, host-side (W10 file 02 rules).
5. `05-tracing.md` — observability you got for free.

## Prerequisites

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/`](../../Week-10-Introduction-to-Agentic-AI-MCP/)
  — every SDK primitive maps to something you built by hand.
- Week 09 tool contract — the tools this SDK will call.
