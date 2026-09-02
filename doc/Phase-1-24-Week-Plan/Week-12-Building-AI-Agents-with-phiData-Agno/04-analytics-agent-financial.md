# 04 — Analytics Agent: Financial & Stock Data

> Week 12 index: [README.md](README.md)

**Session 2 topic:** *Developing an AI-powered analytics agent for financial or stock data.*

---

## What you'll learn

- The session-2 build: an agent that answers financial questions with real data, charts, and citations
- Finance tools (yfinance) + your guarded SQL + charting, composed
- The reasoning/trace display that makes analytics agents auditable
- Numeric-hallucination defenses specific to analytics (the W6-03 rules at agent level)

## 1. The fastest path: prebuilt finance toolkit

Agno ships finance toolkits — a good first run:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

agent = Agent(
    name="Finance analyst",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True,
                         company_info=True)],
    instructions=[
        "Use the tools for every number. Never recall prices from memory.",
        "Show the tool-derived values before interpreting them.",
        "Add 'Data may be delayed' when presenting market data.",
    ],
    markdown=True,
)
agent.print_response("Compare NVDA and AMD stock price and analyst mood.", stream=True)
```

Watch the trace (playground, file 01): the agent calls multiple tools, synthesizes, formats. This is a *prebuilt toolkit* — the same idea as file 03's `CapstoneToolkit`, maintained by the framework.

## 2. The real build: analytics over YOUR tabular data

The session's intent maps to your capstone: an agent answering analytics questions over `data/` (financial CSVs, stock exports — or your domain's equivalent), combining W6 SQL + charting + W9 knowledge:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from capstone_toolkit import CapstoneToolkit          # file 03

analytics = Agent(
    name="Analytics agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[CapstoneToolkit(row_limit=100)],
    instructions=[
        "You are a financial/analytics analyst for the capstone dataset.",
        "Numbers: ALWAYS via sql_query. Never compute in your head.",
        "Trends/comparisons: ask for the aggregated rows, then interpret.",
        "Charts: use chart_data; reference the returned file path.",
        "Include the SQL and the row values you based claims on.",
        "If data is missing or ambiguous, say so and state assumptions.",
    ],
    add_datetime_to_context=True,                     # W6-03 date rule, built in
    markdown=True,
)
analytics.print_response("Which product had the highest revenue last quarter, and how does its monthly trend look?", stream=True)
```

The trajectory to expect (and to verify): `sql_query` (aggregate) → `sql_query` (monthly breakdown) → `chart_data` → final answer with SQL + path. Log it (W10-04) — this is a flagship demo for the capstone.

## 3. Numeric-hallucination defenses (analytics-specific)

Analytics agents fail in a signature way: **correct narrative, invented numbers**. The defense stack:

| Layer | Mechanism |
|---|---|
| Tool-only numbers | instruction rule 2 + the validator (W6-03) |
| Show-your-data contract | the prompt forces rows/SQL into the answer — auditable |
| Cross-check | a `verify_number` tool: "does value X for metric Y exist in the DB?" the *judge* or a post-run check can call |
| Rounding/format discipline | units in tool outputs ("revenue INR"), so the model doesn't invent currency |
| Date grounding | `add_datetime_to_context=True` + explicit ranges (W6-03) |

Post-run programmatic check (cheap, catches the worst case):

```python
import re

def numbers_supported(answer: str, tool_rows) -> list[str]:
    nums_in_answer = set(re.findall(r"-?\d[\d,]*\.?\d*", answer))
    nums_in_rows = set(re.findall(r"-?\d[\d,]*\.?\d*", str(tool_rows)))
    return sorted(n for n in nums_in_answer if n not in nums_in_rows)
```

Unexplained numbers = flag the answer (W5-04's output guard, analytics edition).

## 4. Reasoning display (auditability)

Analytics answers need their work shown. Two patterns:

1. **Inline artifacts** — the prompt contract already demands SQL + rows in the answer (auditability)
2. **Reasoning trace display** — Agno's reasoning tools / `show_tool_calls=True` render the step-by-step in the UI; the playground shows spans (W11-05 analog)

For the capstone: keep the *trace in your JSONL* (W10-04) and the *artifacts in the answer* — the user sees conclusions; the auditor sees both layers.

## 5. yfinance / live-data caveats (for the stock half)

- Live market data = **volatile tool outputs** — cache responses for evals (determinism, W10-04); evals with live prices are unfalsifiable otherwise
- Ticker validation: hallucinated tickers return plausible-looking empty frames; validate symbols against a fixed list
- Date windows: "last quarter" needs the clock (W6-03) — `add_datetime_to_context=True`
- Never let the agent *trade* or call write-apis without the W10-04 HITL gate (read-only finance is already a big demo)

## Exercises

1. Build the prebuilt finance agent (§1); ask 3 comparison questions. Log tool calls — how many roundtrips per answer?
2. Build your analytics agent over your CSV (§2); run 8 questions from your W6 eval set. Success rate vs the W6 Text2SQL-alone baseline — where does the agent add value (chart? multi-step)? Where is it slower for the same answer?
3. Implement `numbers_supported`; plant one hallucinated number in an answer (edit the final text) and verify the check flags it.
4. Add the chart tool to a trend question; verify the file path + summary stats return, and the answer references them.
5. Live-data determinism drill: cache yfinance responses to disk keyed by (ticker, date-window); rerun the eval twice — same results? This is your W16 eval reproducibility lesson, one quarter early.

## Pitfalls

- **Narrative-hallucination** — right *kind* of sentence, wrong numbers; the §3 stack exists because prompts alone don't fix it
- **Uncapped rows in tool output** — a "SELECT *" observation is a context bomb (W10-05); `row_limit` enforced in the toolkit
- **Silent date drift** — "last quarter" computed by the model without a clock; inject today's date, always
- **Charts as magic** — a chart path without interpretation is a dead end; the answer must reference and interpret it
- **Demo-data confusion** — synthetic stock data in your repo presented as real market data; label sources in metadata (W7-01)

## Resources

- Agno [Finance/YFinance toolkit docs](https://docs.agno.com) — prebuilt tool flags
- [yfinance docs](https://ranaroussi.github.io/yfinance/) — the data layer under the toolkit
- W6-03 (Text2SQL pipeline) + W10-04 (measurement) + W5-04 (output guards) — composed here
- OpenAI Cookbook, structured-analytics-agent examples (prompt contracts for numbers)
