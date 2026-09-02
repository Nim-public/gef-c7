# 02 — Project: CSV Analyzer with LangChain

> Week 14 index: [README.md](README.md)

**Session 1 project:** *CSV Analyzer with LangChain — 1. Chat with Data: ask questions about your CSV in plain English and get instant answers. 2. Smart Summaries: auto-generate data profiles, statistics, and quality reports. 3. AI Analysis: perform correlations, trends, and pattern detection through conversation. 4. Visual Insights: create charts and get AI-powered interpretations of your data.*

---

## What you'll learn

- Schema-aware data tools: the pandas-executing agent done safely (W6-03's rules + W12-04's numeric guards, LangChain edition)
- The four feature pillars as four composable pieces: chat, profile, analyze, visualize
- A Gradio/CLI front end over the same chain you unit-test

## 1. Design: four features, one tool surface

| Feature | Implementation | Guard |
|---|---|---|
| Chat with Data | agent + `run_pandas`/`run_sql` tool | read-only, row caps (W6-02) |
| Smart Summaries | deterministic `df.describe()` profiling tool (no LLM for stats) | none needed — code, not model |
| AI Analysis | LLM interpretation **over profile/tool rows** | numbers-supported check (W12-04) |
| Visual Insights | chart tool saving PNG + returning path + summary | fixed output dir (W10-02) |

The profiling insight (carry it everywhere): **statistics belong to deterministic tools; the LLM interprets them** — never let the model compute your numbers.

## 2. The tools

```python
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from langchain_core.tools import tool

DF_CACHE: dict[str, pd.DataFrame] = {}

def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(f"data/{name}.csv", parse_dates=True)
    DF_CACHE[name] = df
    return df

@tool
def profile_csv(name: str) -> str:
    """Data profile: dtypes, shape, missing values, describe() statistics for a loaded CSV."""
    df = DF_CACHE.get(name) or load_csv(name)
    buf = df.describe(include="all").to_string()[:2500]
    missing = df.isna().sum()[df.isna().sum() > 0].to_string() or "none"
    return f"shape={df.shape}\ndtypes:\n{df.dtypes.to_string()}\nmissing:\n{missing}\nstats:\n{buf}"

@tool
def run_pandas(code: str, name: str) -> str:
    """Run a pandas expression on the loaded CSV. `df` is the DataFrame.
    MUST end with an expression or .to_string(). Read-only: no writes/inplace."""
    import pandas as pd
    env = {"pd": pd, "df": DF_CACHE[name]}
    try:
        if not code.replace(" ", "").startswith(("df", "len(", "pd.")):
            return "ERROR: expression must start from df"
        result = eval(code, {"__builtins__": {}}, env)      # sandboxed eval, restricted builtins
        return str(result)[:2000]
    except Exception as e:
        return f"ERROR {type(e).__name__}: {e} — fix the expression or use profile_csv."
```

(`eval` with restricted builtins is a *demo-grade* sandbox — say so in the README and prefer `df.query()`/SQL for production; the teaching point is the guard pattern.)

```python
@tool
def chart_data(name: str, kind: str, x: str, y: str, title: str) -> str:
    """Create a chart (kind: bar|line|scatter) from loaded CSV columns. Returns the PNG path."""
    df = DF_CACHE[name]
    ax = getattr(df.plot, kind)(x=x, y=y, title=title, figsize=(8, 4))
    path = f"data/charts/{title.replace(' ', '_')}.png"
    plt.tight_layout(); plt.savefig(path); plt.close()
    return f"Chart saved to {path}. Summary: {df[[x, y]].describe().to_string()}"
```

## 3. The agent

```python
from langchain.agents import create_agent

analyzer = create_agent(
    model="openai:gpt-4o-mini",
    tools=[profile_csv, run_pandas, chart_data],
    system_prompt=(
        "You are a data analyst. Rules: profile first, then query. Every number in your "
        "answer must appear in a tool result you received. Reference charts by path. "
        "If the CSV lacks the column, say so instead of guessing."),
)
result = analyzer.invoke({"messages": [{"role": "user", "content":
    "Analyze sales.csv: monthly revenue trend, anomalies, and a bar chart by region."}]})
```

## 4. The four features, wired

1. **Chat with Data** — the agent above, in a Gradio `gr.ChatInterface` (W9-01) with session state
2. **Smart Summaries** — `profile_csv` invoked *directly* (no LLM) for the always-on data-quality panel; the LLM only narrates its output
3. **AI Analysis** — correlation/trend prompts that reference the profile ("given these stats, what relationships deserve investigation?") — hypothesis generation, verified back against `run_pandas`
4. **Visual Insights** — `chart_data` + a forced interpretation step ("describe what this chart shows and one anomaly")

## 5. Evaluation (your harnesses, again)

- Numbers-supported check on 10 analysis answers (W12-04 §3)
- Tool-selection accuracy on 15 questions (profile vs pandas vs chart — W10-04 suite)
- Chart sanity: 3 charts eyeballed against the data (the LLM picks axes — verify they're the right ones)

## Exercises

1. Build the analyzer over a capstone CSV; run 10 questions; log trajectories (W10-04 schema).
2. Harden `run_pandas`: reject `inplace=`, `.to_sql`, imports in code; test 5 malicious expressions (file writes, `os.` calls). What does restricted-builtins *not* stop?
3. Add a "data quality report" node (W13-01 graph) that chains profile → missing-value strategy suggestions → a markdown report.
4. AI-analysis consistency: run the same correlation question 3× at temperature 0 — how stable are the claimed findings? (W5-05's judge-spread lesson.)
5. Extend to JSON input (W1-04 + `json_normalize`): nested events → flat columns → the same four features. What broke in the schema assumptions?

## Pitfalls

- **LLM-computed statistics** — "revenue is about 1.2M" from mental math is the signature analytics-agent failure; tools compute, LLM interprets
- **Unrestricted `eval`** — restricted builtins is *mitigation*, not security; production = SQL/duckdb tool (W6-02's read-only pattern)
- **Chart axes hallucinated from column names** — validate x/y exist in `df.columns` before plotting
- **Profile output too big** — `describe(include="all")` on 100 columns floods context; cap and summarize (W10-05)
- **Session state leaking across users** — `DF_CACHE` is global; scope per session or reload per request

## Resources

- LangChain [SQL/pandas agent how-tos](https://python.langchain.com/docs/tutorials/) — the library-packaged versions
- W6-03/04 — the SQL/pandas discipline being wrapped
- [matplotlib programmatic use](https://matplotlib.org/stable/users/getting_started/) — Agg backend for servers
- pandas [`describe`/profiling](https://pandas.pydata.org/docs/user_guide/basics.html#descriptive-stats) — what your summary tool should include
