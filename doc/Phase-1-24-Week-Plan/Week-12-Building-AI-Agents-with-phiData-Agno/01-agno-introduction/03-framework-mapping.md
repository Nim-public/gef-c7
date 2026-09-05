# Framework Mapping — W10/W11/W12 Completion Table

**What you'll learn:** the three-framework comparison that ends the
"which framework" debates: one table, one row per capability, each cell
citing the week that built or tested it.

## 1. The completion table

| Capability | W10 (hand-rolled) | W11 (OpenAI SDK) | W12 (Agno) |
|---|---|---|---|
| agent loop | 50 lines, yours | `Runner.run` 4 steps | `Agent.run` + Teams |
| tool contracts | ToolRegistry + hints | `@function_tool` + failure fn | `@tool`/Toolkit + docstrings |
| structured output | manual validators | `output_type` strict | `output_schema` Pydantic |
| history | message list + fitter | `SQLiteSession` | `SqliteDb`/`PostgresDb` sessions |
| guardrails | gates + audits | tripwires (in/out) | instructions + tool flags |
| knowledge/RAG | your LanceDB hybrid | BYO (your stack) | `Knowledge` + LanceDB native |
| multi-agent | none | handoffs / as_tool | `Team` (roles), Workflows |
| observability | your harness | traces + your merge | AgentOS + your merge |
| context budgeting | fitter + properties | manual | manual |
| eval harness | yours | yours (extended) | yours (extended) |

Read the last two rows twice: **no framework replaces your harness or
your budget discipline.** That is the finding of three weeks of mapping.

## 2. The selection table (the memo's next row)

| If the capstone needs… | Pick | Because |
|---|---|---|
| full control + teaching value | W10 patterns | you own every seam |
| strict structured outputs + guardrails | W11 SDK | tripwires + strict schema |
| fastest knowledge-backed agents | W12 Agno | `Knowledge` + LanceDB native |
| team topologies with roles | W12 Agno `Team` / W11 handoffs | first-class on both |
| vendor-neutral tool logic | any | your logic stayed plain functions |

The capstone answer (from your W10 boundary memo): the *policies*
(budgets, gates, detectors, eval) are framework-independent assets; the
*mechanism* is swappable. That is why the tool logic stayed in plain
functions.

## 3. The completion table as a learning map

Each framework forced you to re-express the same four concerns:

| Concern | The question each framework asks |
|---|---|
| loop | who decides control flow? |
| tools | what is the contract surface? |
| memory | what persists, what fits? |
| eval | how do you know it regressed? |

Your answers are framework-independent — which is exactly why the
verdict memos (W11) and the completion table here can coexist.

## 5. The migration cost column (the table's fine print)

| Move | Cost | Paid by |
|---|---|---|
| W10 → W11 SDK | ~6 h port, battery per step | W11 file 06 |
| W11 → Agno | ~2 h (tools+instructions mostly 1:1) | this week's exercises |
| any → CrewAI | ~2 h (roles) + process choice | this week's file 06 |
| any framework bump | re-run battery + pin note | standing rule |

The cost column is why the decision (file 06 of this week) is allowed to
be "stay": every framework hop re-runs the battery, and the battery's
pass rate is the only currency that matters. A framework that cannot
pass your existing tests does not get adopted for features alone.

## Exercises

1. Fill the W10/W11/W12 table with your implementation status per cell
   (ported / tested / N/A); the N/A cells are Week 13+ scoping input.
2. Cross-test drill: run one W11 test (trajectory shape) against the
   Agno port unchanged — the schema is the contract; the test either
   ports cleanly or names a gap.
3. Decision drill: pick ONE framework for the final build; write the
   three-sentence justification citing the table and one cost column
   number.

## Pitfalls

- Framework tourism — three frameworks is comparison; four is avoidance.
  The table ends the tour.
- Copying cells without testing — a mapping you have not run is a guess;
  the battery is the arbiter.
- Losing the manual rows in a framework switch — the fitter, gates, and
  detectors are yours in every framework; write them down per port.

## Resources

- Agno docs (context7: `/agno-agi/docs`); OpenAI Agents SDK (W11 files).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/04-when-not-agents.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/04-when-not-agents.md)
  — the original boundary discipline.