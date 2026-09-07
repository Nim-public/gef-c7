# Deep-Dive: Practice — Agents SDK Capstone Port

Parent deliverable spec: [`../06-practice-agents-sdk-capstone.md`](../06-practice-agents-sdk-capstone.md)

The parent defines the porting exercise: your Week-10 hand-rolled agent,
rebuilt on the SDK, compared case-for-case, debugged via traces, and
judged by a lines-vs-capabilities verdict. This subfolder is the method.

## File map

| File | What it covers |
|---|---|
| [`01-port-methodology.md`](01-port-methodology.md) | W10 agent → SDK primitives, in order |
| [`02-comparison-table.md`](02-comparison-table.md) | Same cases, both implementations |
| [`03-trace-debugging.md`](03-trace-debugging.md) | Planted failure, root-caused in the trace |
| [`04-verdict.md`](04-verdict.md) | Lines saved vs capabilities gained |
| [`exercises.md`](exercises.md) | Stretch tasks and the self-review rubric |

## Build order

1. `01-port-methodology.md` — port by component, battery after each.
2. `02-comparison-table.md` — the same eval set, both implementations.
3. `03-trace-debugging.md` — debug the SDK version with the trace tools.
4. `04-verdict.md` — the memo that decides what Week 12+ builds on.

## Prerequisites

- All five prior subfolders — every SDK primitive is ported and tested.
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/06-practice-first-mcp-agent/`](../../Week-10-Introduction-to-Agentic-AI-MCP/06-practice-first-mcp-agent/)
  — the reference implementation.
