# Agno Assembly — Toolkits + Knowledge in One Agent

**What you'll learn:** the assembly: W12's toolkits (CorpusTools,
AnalyticsTools), Knowledge, and the verification hooks in one agent —
every prior week's discipline in a single constructor call.

## 1. The assembly

```python
from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.models.openai import OpenAIResponses

agent = Agent(
    name="Data Agent",
    model=OpenAIResponses(id="pinned-model-id"),
    tools=[
        CorpusTools(mode="eval"),
        AnalyticsTools(db_path="data/warehouse.duckdb"),
    ],
    knowledge=knowledge,                  # W12-02 wrap, hybrid
    search_knowledge=True,
    instructions=[
        *GROUNDING_RULES,                 # W12-02 file 03, cvN
        *ROUTING_RULES,                   # knowledge vs SQL (W12-02 file 04)
        "Always verify totals with verify_number.",
    ],
    output_schema=AnalysisResult,
    markdown=True,
    show_tool_calls=True,
)
```

Every constructor argument is an artifact you already tested: toolkits
(W12-03 battery), knowledge (W12-02 parity), rules (W12-02 battery),
typed output (W12-04). Assembly is composition — the port methodology
from W11 file 06-01, third application.

## 2. What "one agent" means (and what stays outside)

| Component | In the agent | Outside |
|---|---|---|
| toolkits | yes | their tests |
| knowledge | yes | the ingest pipeline |
| grounding rules | yes (`instructions`) | the battery that tests them |
| verification | as tools + policy | the mismatch drills |

The agent object is thin; the *system* is the surrounding artifacts.
The assembly's test is that the agent behaves identically to its
components' tested behavior — the W12 comparison tables are the
baseline.

## 3. The 15-case design (preview)

| # | Class | Cases |
|---|---|---|
| 1–5 | corpus QA (knowledge) | quotes, explanations, citations |
| 6–10 | analytics (SQL) | aggregates, filters, trends |
| 11–13 | mixed (both) | numeric + context |
| 14 | impossible | honest refusal |
| 15 | ambiguous | clarification or flag |

The case table is file 02's subject; the assembly's job is to *not*
special-case any of them — one agent, one tool surface, fifteen shapes
of question.

## 4. The assembly checklist (the capstone's agent review)

```text
[ ] toolkits: battery-green at current Agno version
[ ] knowledge: parity loop green (5 golden queries)
[ ] grounding rules: battery green, version stamped (cvN)
[ ] typed output: citation validator catches phantoms
[ ] verification: policy wired, mismatch drill passed
[ ] config stamps: every trajectory row carries component versions
```

The checklist is the assembly's acceptance review — six rows, each
citing an artifact from Weeks 10–12. It is the W10 pipeline gates
(contract, quarantine, determinism, settings) applied to an agent
constructor: the constructor is thin *because* everything behind it is
tested.

## 5. The assembly's component pin table

| Component | Version/artifact | Verified by |
|---|---|---|
| toolkits | W12-03 battery date | parity test |
| knowledge | W12-02 parity date | golden queries |
| grounding rules | cvN | insufficiency battery |
| typed output | schema v1 | validator tests |
| model | pinned id | every run's header |

The pin table is the assembly's version manifest — five components, five
verification artifacts. The 15-case run inherits all five pins; any
upgrade re-runs the corresponding battery before the table is trusted
again.

## Exercises

1. Assemble the agent; run the smoke test (W10-06 style) on both canned
   and real models.
2. Config-stamp drill: verify every trajectory row carries the assembly
   versions (toolkits, knowledge, rules, model).
3. Thin-agent drill: list what is *not* in the constructor (ingest,
   battery, drills) — the surrounding system, named.
4. Pin-table drill: fill §5 from `reports/sdk-versions.md`; any missing
   verification blocks the 15-case run.
4. Checklist drill: run the §4 review; every row cites its artifact;
   any red row blocks the 15-case run (file 02).

## Pitfalls

- Assembly that re-implements tested logic inline — the toolkits are the
  tested units; the agent composes.
- Instructions that contradict the batteries' rules — one source per
  rule (the constitution cvN), imported not retyped.
- Forgetting `show_tool_calls` before the demo — the audit trail is one
  flag; it is also the reviewer's window.