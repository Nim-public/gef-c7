# Advanced Data Tools — Charts, Schema, Verification

**What you'll learn:** the three tools that turn an analytics agent from
"LLM with a SQL prompt" into a verifiable analyst: chart generation,
schema introspection, and numeric verification hooks.

## 1. The schema tool — introspection before composition

```python
@tool
def get_schema(tables: str | None = None) -> str:
    """Return the schema of the warehouse (or specific tables).

    Args:
        tables (str): comma-separated table names, or None for all.
    """
    return schema_ddl(tables)     # CREATE statements + row counts
```

Text-to-SQL fails most often from *guessed* schemas. The schema tool
makes the ground truth one call away — and the instruction ties it:
"call get_schema before your first query against an unfamiliar table."
The schema text is versioned with the warehouse (the settings-stamp
discipline).

## 2. The verification tool — numbers check numbers

```python
@tool
def verify_number(claim: str, sql: str) -> str:
    """Verify a numeric claim by running an independent SQL check.
    Args:
        claim (str): the numeric claim, e.g. 'total revenue Q3 = 1.2M'.
        sql (str): independent query recomputing the figure.
    """
    if blocked := validate_sql(sql, ALLOWED_TABLES):
        return blocked
    row = run_sql(sql)
    if not row:
        return "verification query returned no rows — claim unsupported"
    return f"verification: {row}"          # the agent compares, on the record
```

The verification hook is the numeric-hallucination defense (file 04
extends it): the agent's first SQL computes the answer; the second,
independent query *checks* it. Two agreements → the claim ships; a
mismatch → the claim dies with both queries in the transcript.

## 3. The chart tool — visualization as an artifact, not a guess

```python
@tool
def render_chart(data_sql: str, chart_type: str, title: str) -> str:
    """Render a chart from a SELECT query's results.

    Args:
        data_sql (str): SELECT returning >=2 columns.
        chart_type (str): 'bar' | 'line' | 'pie'.
        title (str): chart title.
    """
    if chart_type not in ("bar", "line", "pie"):
        return f"unsupported chart_type '{chart_type}'"
    df = run_sql_df(data_sql)              # validated path only
    path = f"reports/charts/{slugify(title)}.png"
    df.plot(kind=chart_type).figure.savefig(path)
    return f"saved: {path}"                # repo-relative, per W7 rules
```

The chart tool composes the guarded SQL path with rendering — the chart
is *derived from a query*, not from the model's imagination of the data.
The saved path is repo-relative and joins the citation trail (the
answer names the chart file).

## 4. The analytics toolkit, assembled

```python
class AnalyticsTools(Toolkit):
    def __init__(self, db_path: str, **kwargs):
        self.db = DuckDb(db_path)
        tools = [self.run_sql_query, self.get_schema,
                 self.verify_number, self.render_chart]
        super().__init__(name="analytics", tools=tools,
                         cache_results=True, **kwargs)
```

| Tool | Input | Output | Guard |
|---|---|---|---|
| `run_sql_query` | SELECT | rows + count | SQL validator |
| `get_schema` | table filter | DDL + counts | read-only |
| `verify_number` | claim + SQL | verdict | validator + independence check |
| `render_chart` | SQL + type | file path | validator + type enum |

Four tools, each with a guard, each returning citable evidence — the
file 04 agent's full surface, one toolkit.

## Exercises

1. Build `AnalyticsTools`; run the guarded-SQL battery (write attempts,
   no-LIMIT, off-list) — all refused with hints.
2. Verification drill: answer one aggregate question; then have the
   agent call `verify_number` with an independent query; both SQL texts
   must appear in the answer.
3. Chart drill: render one chart from a query; verify the file lands in
   `reports/charts/` repo-relative and the answer names it.

## Pitfalls

- Charts from model-recalled numbers — the tool takes *SQL*, not data;
  the derivation chain is the audit trail.
- Verification with the *same* query as the answer — that is not
  independent; instruct (and test) that the second query recomputes
  differently.
- Chart files outside `reports/` — repo-relative discipline (W7) applies
  to generated artifacts too.

## Resources

- Agno toolkits + your SQL validator (context7: `/agno-agi/docs`).
- [`../../Week-06-RAG-for-Tabular-Data/`](../../Week-06-RAG-for-Tabular-Data/)
  — the analytics foundation.
- [`../04-analytics-agent-financial/`](../04-analytics-agent-financial/)
  — the agent that consumes this toolkit.