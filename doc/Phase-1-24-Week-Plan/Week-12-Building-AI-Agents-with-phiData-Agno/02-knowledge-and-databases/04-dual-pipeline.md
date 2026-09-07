# Dual-Pipeline Design — Knowledge vs SQL Tool Selection

**What you'll learn:** the two-pipeline architecture: `Knowledge` for
prose and `SQL` for numbers, with the routing decision the model makes —
and the guardrails that keep text-to-SQL from becoming text-to-fiction.

## 1. The architecture

```python
from agno.agent import Agent
from agno.tools.duckdb import DuckDbTools

analytics = Agent(
    model=...,
    knowledge=knowledge,                  # prose, chunks, citations
    search_knowledge=True,
    tools=[DuckDbTools(db_path="data/warehouse.duckdb")],
    instructions=[
        "Facts, quotes, explanations → search_knowledge.",
        "Numeric aggregates over tables → run_sql_query. Never estimate "
        "numbers from memory or from text snippets.",
        "Validate: run_sql results must be non-empty; empty result → say "
        "so, do not invent.",
        "Cite: knowledge answers cite unit_ids; SQL answers name the "
        "query and row count.",
    ],
    markdown=True,
)
```

| Pipeline | Serves | Failure without the other |
|---|---|---|
| Knowledge | semantics, quotes, chart *context* | numbers get estimated from prose |
| SQL | exact aggregates, filters | prose can't compute |

The W6 lesson (tabular RAG) applied at the agent layer: numbers come
from queries; meaning comes from text; the agent routes between them.

## 2. Guarded SQL composition

```python
SQL_GUARDRAILS = [
    "SELECT only — no INSERT/UPDATE/DELETE/DROP.",
    "Single statement per call.",
    "LIMIT required on every query (default 50).",
    "Only the whitelisted tables: {tables}.",
]

def validate_sql(sql: str, tables: set[str]) -> str | None:
    low = sql.lower()
    if any(w in low for w in ("insert", "update", "delete", "drop", "alter")):
        return "blocked: write operations are disabled"
    if not low.strip().startswith("select"):
        return "blocked: only SELECT statements"
    if not any(t in low for t in tables):
        return f"blocked: table not in allow-list {sorted(tables)}"
    if "limit" not in low:
        return "blocked: add a LIMIT clause"
    return None
```

The validator runs *inside* the tool (the W10 registry posture — client
trust is zero): the agent can compose any SELECT; the tool refuses the
rest with an instructive error (file 05 of W10 — hints teach).

## 3. Routing quality: the dual-battery

| Query | Correct route | Battery check |
|---|---|---|
| "What does the Q3 chart show?" | knowledge | search fired, unit cited |
| "What was total revenue in Q3?" | SQL | sql tool fired, query shown |
| "Why did revenue rise?" | knowledge (then maybe SQL) | search first, numbers cited |
| "List all customers named Smith" | SQL | sql fired, row count reported |
| "Who wrote the memo?" | knowledge | search fired |

Route accuracy is measured exactly like the W9 router (expected-tools
sets) — the eval set gains a `route` column, and the same A/B on
instruction wording applies. The W9-05 router has become model behavior;
the measurement survives unchanged.

## 4. The two-store contract

| Store | Owns | Id |
|---|---|---|
| `Knowledge` (LanceDB) | text chunks, citations | `unit_id` |
| warehouse (DuckDB) | exact tabular facts | query + row count |

One sentence in the capstone README ties them: *"prose is cited by
unit; numbers are cited by query."* The audit trail for a numeric claim
is the SQL itself — which is why the query text appears in the answer
(file 04's reasoning display).

## Exercises

1. Build the dual-pipeline agent; run the route battery (5 cases);
   report route accuracy vs the W9 router's table.
2. SQL-guardrail drill: attempt each blocked pattern (write, no-LIMIT,
   off-list table); verify instructive refusals, zero side effects.
3. Numeric-parity drill: answer the same numeric question via SQL and
   via knowledge-only; show the knowledge answer drifts — the case for
   the dual pipeline, demonstrated on your data.

## Pitfalls

- Vectorizing the warehouse "so one tool suffices" — numeric hallucination
  by design; the dual split is the defense.
- SQL guardrails validated in the model's instructions only — instructions
  are prompts, not gates; the tool validates (W10 registry rule).
- Citation style mixing — knowledge answers cite units; SQL answers cite
  queries; mixing them corrupts the audit trail.

## Resources

- Agno tool docs (DuckDb/SQL toolkits) (context7: `/agno-agi/docs`).
- [`../../Week-06-RAG-for-Tabular-Data/`](../../Week-06-RAG-for-Tabular-Data/)
  — the tabular foundation.
- [`../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md`](../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md)
  — the routing measurement this extends.