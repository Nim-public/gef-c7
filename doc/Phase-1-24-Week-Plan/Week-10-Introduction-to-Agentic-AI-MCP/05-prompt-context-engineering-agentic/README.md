# Deep-Dive: Prompt & Context Engineering for Agents

Parent overview: [`../05-prompt-context-engineering-agentic.md`](../05-prompt-context-engineering-agentic.md)

The agent's system prompt is a *constitution* (rules it may not break),
observations are *prompts* (errors teach), the context fitter has
*priorities* (what gets cut first), and failure phrasing is an *A/B
variable* (measured, not vibes). This subfolder builds all four.

## File map

| File | What it covers |
|---|---|
| [`01-agentic-constitution.md`](01-agentic-constitution.md) | The 7-rule system prompt, tested |
| [`02-observation-formatting.md`](02-observation-formatting.md) | Results and errors as instructive prompts |
| [`03-context-fitter.md`](03-context-fitter.md) | Priorities, truncation, paging — implemented |
| [`04-failure-phrasing.md`](04-failure-phrasing.md) | A/B measured rewording of error hints |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-agentic-constitution.md` — the rules before any run.
2. `02-observation-formatting.md` — the per-step prompt surface.
3. `03-context-fitter.md` — the deterministic assembler (extends file 02).
4. `04-failure-phrasing.md` — measure your way to better errors.

## Prerequisites

- [`../02-tools-and-memory/03-memory-taxonomy.md`](../02-tools-and-memory/03-memory-taxonomy.md)
  and [`04-context-budgeting.md`](../02-tools-and-memory/04-context-budgeting.md)
  — the layers this fitter assembles.
- [`../03-mcp-servers-fastmcp/03-client-batteries.md`](../03-mcp-servers-fastmcp/03-client-batteries.md)
  — the error hints being phrased here.
