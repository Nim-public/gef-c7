# Deep-Dive: LangChain Foundations

Parent overview: [`../01-langchain-foundations.md`](../01-langchain-foundations.md)

LangChain is the composition framework: prompt templates, LCEL pipelines,
structured outputs, and the modern `create_agent` API. This subfolder
maps each primitive onto your W10–W13 vocabulary — everything here is a
re-expression of discipline you already own.

API verified against context7 id `/websites/langchain_oss_python_langchain`.

## File map

| File | What it covers |
|---|---|
| [`01-prompt-templates.md`](01-prompt-templates.md) | Versioned, validated, file-loaded prompts |
| [`02-lcel-composition.md`](02-lcel-composition.md) | Pipelines, streaming, fallbacks/retries |
| [`03-structured-output.md`](03-structured-output.md) | Pydantic-validated chains |
| [`04-create-agent.md`](04-create-agent.md) | The modern agent API, mapped |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-prompt-templates.md` — prompts as versioned artifacts.
2. `02-lcel-composition.md` — the pipe syntax and its runtime guarantees.
3. `03-structured-output.md` — Pydantic at the chain boundary.
4. `04-create-agent.md` — the agent API, mapped to W10/W11.

## Prerequisites

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/`](../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/)
  — the constitution and fitter these templates carry.
- [`../../Week-13-Building-AI-Agents-with-LangGraph/01-langgraph-foundations/`](../../Week-13-Building-AI-Agents-with-LangGraph/01-langgraph-foundations/)
  — `create_agent` builds on LangGraph under the hood.