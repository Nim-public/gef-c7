# Result Formatting — Grounded Answers with SQL Audit Lines

**What you'll learn:** formatting query results into grounded answers:
the numbers stated with units, the SQL shown as the audit line, the row
counts declared, and the empty-result honesty.

## 1. The answer format

```python
def format_result(question: str, sql: str, rows: list[dict]) -> str:
    if not rows:
        return ("No rows matched that query. The data may not contain "
                "an answer — try different filters.")
    lines = []
    for r in rows[:5]:
        lines.append("- " + ", ".join(f"{k}: {v}" for k, v in r.items()))
    more = f"\n(showing 5 of {len(rows)} rows)" if len(rows) > 5 else ""
    audit = f"\n\nsql: `{sql}`\nrows: {len(rows)}"
    return "\n".join(lines) + more + audit
```

| Element | Purpose |
|---|---|
| per-row lines | the evidence, readable |
| truncation notice | honest about size |
| `sql:` audit line | the claim's provenance |
| `rows:` count | the sample size stated |

The format is the W12 reasoning-display contract (user view vs reviewer
view) at SQL granularity: the user sees rows; the audit line carries
the provenance. The numbers_supported pairing (W14 file 02-04) audits
that every number in the prose appears in the rows.

## 2. Empty and error results (the honesty paths)

| Case | Output |
|---|---|
| 0 rows | "No rows matched… try different filters." |
| 1 row | the row, stated as singular |
| huge aggregate | the number + the SQL + row count |
| overflow | the cap notice with the true count |

The empty case is the W13 honest-refusal path, SQL edition: "no rows"
is an *answer*, not a failure. The eval set (file 05-02) includes the
empty case exactly for this.

## 3. The synthesis (rows → prose, honestly)

```python
SYNTH_PROMPT = """Using ONLY the query results below, answer the
question. State units. If the results don't contain the answer, say so.
Do not compute new aggregates beyond simple comparisons of shown values.

Results: {rows_json}
Question: {question}"""
```

| Rule | Why |
|---|---|
| only from shown rows | no mental math on unshown data |
| units stated | 1200 vs 1.2k ambiguity |
| simple comparisons allowed | "June > May" is safe; "sums to X" re-derives |
| refuse on gaps | the honesty rule |

The synthesis prompt is the borderline between reporting and computing:
simple comparisons of *shown* values are safe; new aggregations go
through another query (the verification loop).

## 5. The formatting pin note (the answer contract's manifest)

```markdown
# SQL result formatting (W06)
- format: per-row lines, truncation notice, sql audit line, row count
- empty: honest "no rows matched" message (never a crash)
- synthesis: only from shown rows; simple comparisons; refuse gaps
- audit: numbers_supported pairing extends to SQL results
```

The pin note is the answer format's manifest — the display contract
(W12 file 04-04) SQL edition, with the honesty paths named.

## Exercises

1. Implement `format_result`; run it on the ladder's Q1–Q8 outputs;
   every answer carries the audit line.
2. Empty drill: query a filter that matches nothing; the honest message
   fires; the eval's empty case passes.
3. Synthesis drill: run the synthesis prompt on 5 results; audit every
   number in the prose against the rows_json — the pairing audit, SQL
   edition.
4. Pin drill: write the note; the pairing audit command green.

## 6. The number-pairing audit (SQL edition)

```python
def audit_sql_numbers(answer: str, rows: list[dict]) -> list[str]:
    issues = []
    for n in extract_numbers(answer):
        in_rows = any(str(n) in str(v) for r in rows for v in r.values())
        if not in_rows:
            issues.append(f"number {n} not in query results")
    return issues
```

| Check | Catches |
|---|---|
| numbers in prose, not in rows | hallucinated figures |
| rows with numbers never mentioned | incomplete answers (warning) |

The pairing audit is the numeric-grounding check (W14 file 02-04)
applied to SQL results — the answer's figures must be traceable to the
returned rows. The audit runs in the harness gate (W15 file 04).

## Exercises (continued)

5. Audit drill: plant a hallucinated number in a draft answer; the audit
   flags it before delivery.