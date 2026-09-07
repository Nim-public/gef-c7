# Deep-Dive: Project — Code Review Agent

Parent overview: [`../03-project-code-review-agent.md`](../03-project-code-review-agent.md)

The two-layer review agent: a deterministic scan layer (AST + ruff)
that cannot hallucinate, an LLM review layer emitting structured
`Finding` models, a severity-sorted deterministic report, and diff-aware
context.

## File map

| File | What it covers |
|---|---|
| [`01-deterministic-layer.md`](01-deterministic-layer.md) | AST/ruff findings — facts first |
| [`02-llm-review-layer.md`](02-llm-review-layer.md) | Structured `Finding` models |
| [`03-report-generation.md`](03-report-generation.md) | Deterministic severity sort |
| [`04-diff-aware-review.md`](04-diff-aware-review.md) | Full-file context, line hints |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-deterministic-layer.md` — the facts the LLM cannot dispute.
2. `02-llm-review-layer.md` — judgment, typed.
3. `03-report-generation.md` — deterministic assembly.
4. `04-diff-aware-review.md` — review what changed, with context.

## Prerequisites

- [`../01-langchain-foundations/`](../01-langchain-foundations/) — typed
  chains.
- [`../../Week-13-Building-AI-Agents-with-LangGraph/04-team-agents-codegen-loop/02-sandbox-discipline.md`](../../Week-13-Building-AI-Agents-with-LangGraph/04-team-agents-codegen-loop/02-sandbox-discipline.md)
  — the sandbox if review suggests running anything.