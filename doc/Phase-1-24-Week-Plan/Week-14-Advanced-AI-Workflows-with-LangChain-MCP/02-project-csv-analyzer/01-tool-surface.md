# Tool Surface — Profile / Pandas / Chart with Guards

**What you'll learn:** the three-tool surface for CSV analysis: a
profiler (schema + stats), a pandas executor (guarded), and a chart
renderer — each with the validation that keeps model-written pandas
honest.

## 1. The profiler — know the data before querying it

```python
@tool
def profile_csv(file_id: str) -> str:
    """Profile an uploaded CSV: columns, dtypes, null counts, sample rows.

    Args:
        file_id (str): id of an uploaded file.
    """
    df = load_df(file_id)
    profile = {
        "rows": len(df),
        "columns": {c: str(df[c].dtype) for c in df.columns},
        "nulls": df.isna().sum().to_dict(),
        "sample": df.head(3).to_dict(orient="records"),
    }
    return json.dumps(profile)
```

The profiler is the schema tool (W12 file 03-03) for files: the model
*must* call it before composing pandas code — the instruction ties it,
the trace verifies the order.

## 2. The pandas executor — guarded code, verified output

```python
@tool
def run_pandas(code: str, file_id: str) -> str:
    """Run pandas code against the uploaded CSV. `df` is the DataFrame.

    Args:
        code (str): Python using pandas; must assign the result to `result`.
    """
    if blocked := validate_pandas(code):
        return blocked
    result = run_in_sandbox(code, df=load_df(file_id))
    return json.dumps({"result": result, "rows": result_rows(result)})
```

```python
BLOCKED_PATTERNS = ["os.", "subprocess", "open(", "__import__", "eval(",
                    "exec(", "read_csv(", "to_csv("]

def validate_pandas(code: str) -> str | None:
    for pat in BLOCKED_PATTERNS:
        if pat in code:
            return f"blocked: '{pat}' is not allowed in pandas code"
    if "result" not in code:
        return "blocked: code must assign the answer to `result`"
    return None
```

| Guard | Catches |
|---|---|
| blocked patterns | filesystem, subprocess, eval escapes |
| `result` assignment | the answer must be extractable |
| sandbox execution (file 02) | everything the patterns miss |

## 3. The chart tool — visuals from verified frames

```python
@tool
def render_chart(code: str, file_id: str, chart_type: str, title: str) -> str:
    """Render a chart from pandas code. Code must assign a DataFrame to `result`.

    Args:
        code (str): pandas code producing the chart data.
        chart_type (str): 'bar' | 'line' | 'pie'.
        title (str): chart title.
    """
    if blocked := validate_pandas(code):
        return blocked
    df = run_in_sandbox(code, df=load_df(file_id))
    path = f"reports/charts/{slugify(title)}.png"
    getattr(df.plot(kind=chart_type), "figure").savefig(path)
    return f"saved: {path}"
```

Same derivation rule as W12 file 03-03: charts come from *executed
code over real data* — never from the model's memory of the numbers.

## Exercises

1. Build the profiler; require it before `run_pandas` via the
   constitution; verify the trace order on 5 queries.
2. Guard drill: run the six blocked patterns through `validate_pandas`;
   every one refused with its hint.
3. Chart drill: render one chart per type; verify files land
   repo-relative and answers name them.

## Pitfalls

- `pd.read_csv` inside generated code — the model re-reads *some* path;
  the `df` binding is the only data source; the pattern list blocks it.
- Profiler skipped by the model — the instruction plus trace-order check
  enforce the §1 rule.
- Charts without query provenance — same rule as W12: the chart's code
  appears in the answer.