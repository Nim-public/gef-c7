# Guarded Table Analytics — SQL Composition over Your Tables

**What you'll learn:** the analytics agent over *your* warehouse: schema
introspection, guarded composition, result handling, and the answer
format that keeps every number's provenance on the record.

## 1. The agent, assembled

```python
analytics = Agent(
    name="Analytics Agent",
    model=...,
    tools=[AnalyticsTools(db_path="data/warehouse.duckdb"),
           KnowledgeTools(knowledge=knowledge)],
    instructions=[
        "Numbers over our tables: run_sql_query. Always call get_schema "
        "before querying an unfamiliar table.",
        "Every numeric answer states: the SQL used and the row count.",
        "Never compute in your head what one query could compute.",
        "Context and quotes: use knowledge search and cite unit_ids.",
    ],
    output_schema=AnalysisResult,
    markdown=True,
)
```

The constitution merges the two pipelines' rules (file 02-04): numbers
via SQL with provenance, meaning via knowledge with citations.

## 2. The composition loop (schema → query → check)

```text
1. get_schema                      → know the columns before writing SQL
2. run_sql_query                   → the answer's numbers
3. verify_number (independent SQL) → the check
4. answer with: SQL text + row count + unit citations (if any)
```

| Step | Artifact | Audit role |
|---|---|---|
| schema call | DDL excerpt | proves the columns were known |
| answer query | SQL text + rows | the claim's provenance |
| verification query | second SQL | the independent check |
| final answer | `AnalysisResult` | binds claims to artifacts |

The loop is the numeric-hallucination defense (file 03) expressed as a
*procedure* the instructions mandate — the model's discipline is
prompted, the tool's discipline is enforced.

## 3. Result handling — what the agent does with rows

| Situation | Required behavior |
|---|---|
| >50 rows | summarize; report count; offer top rows |
| 0 rows | say so; propose a relaxed query |
| NULL-heavy columns | report coverage, not just means |
| ambiguous units (K/M/B) | normalize and state the unit |

```python
class AnalysisResult(BaseModel):
    answer: str
    sql_used: list[str]
    rows_considered: int
    citations: list[str]              # unit_ids if knowledge was used
    charts: list[str]                 # chart paths, if rendered
    caveats: list[str] = []
```

The typed result makes the provenance *structural*: `sql_used` and
`rows_considered` are fields, not prose promises — the harness audits
them like citations.

## 4. The eval additions (analytics-specific)

| Case | Gold |
|---|---|
| "Total revenue Q3?" | exact number from a known query |
| "Revenue by month, charted" | chart artifact + SQL in answer |
| "Why did revenue rise?" | knowledge citations + SQL support |
| "Revenue for a table that doesn't exist" | honest schema error |

The W10 eval-set pattern with a numeric column: the gold value is
computable, so the harness checks the *number*, not the phrasing.

## Exercises

1. Assemble the agent; run the composition loop on 5 analytics queries;
   verify every answer carries `sql_used`.
2. Row-handling drill: force each §3 situation (LIMIT cutoff, 0 rows,
   NULL-heavy column); verify the mandated behaviors.
3. Numeric-eval drill: add 5 numeric tasks with computable golds to the
   eval set; score exact-match on the number.

## Pitfalls

- Answers with numbers but no SQL in `sql_used` — that is a hallucination
  with good manners; the validator rejects it.
- Schema calls skipped "for speed" — guessed columns are the top
  text-to-SQL failure; the instruction exists because of that stat.
- Charts without query provenance — the chart tool takes SQL; a chart
  from model-recalled data is a hallucination with axes.