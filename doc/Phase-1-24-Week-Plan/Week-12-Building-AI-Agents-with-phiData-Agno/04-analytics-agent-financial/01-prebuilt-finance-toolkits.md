# Prebuilt Finance Toolkits — YFinance Usage and Limits

**What you'll learn:** the prebuilt toolkit pattern: what Agno's
YFinanceTools gives you, what it cannot guarantee, and the wrapper that
makes its numbers verifiable rather than trustable.

## 1. The toolkit, plainly

```python
from agno.tools.yfinance import YFinanceTools

finance_agent = Agent(
    name="Finance Agent",
    model=...,
    tools=[YFinanceTools(
        stock_price=True,
        analyst_recommendations=True,
        company_info=True,
    )],
    markdown=True,
)
```

| Tool | Returns | Trust level |
|---|---|---|
| stock price | quote data | live but uncached — verify freshness |
| recommendations | analyst consensus | point-in-time, opaque methodology |
| company info | structured facts | usually reliable, still verify |

Prebuilt toolkits are *someone else's tool contract*: you get the
function without the W10 discipline (no error contract, no provenance
metadata, unknown caching). The capstone rule: prebuilt tools are fine
for exploration; production numbers go through your verification layer.

## 2. Wrapping prebuilt tools for verification

```python
@tool
def verified_stock_price(symbol: str) -> str:
    """Current price with timestamp, for numeric claims.

    Args:
        symbol (str): ticker symbol, e.g. 'NVDA'.
    """
    raw = yf_price(symbol)                       # the prebuilt call
    ts = datetime.now(timezone.utc).isoformat()
    return json.dumps({"symbol": symbol, "price": raw_price(raw),
                       "as_of": ts, "source": "yfinance"})
```

The wrapper adds what the prebuilt tool lacks: timestamp, source, and a
stable JSON shape — the provenance trio that lets the reasoning display
(file 04) cite *when* and *whence* every number came.

## 3. Limits, stated once

| Limit | Consequence | Mitigation |
|---|---|---|
| rate limits / blocked requests | tool errors mid-demo | cache layer, retry with backoff |
| data delay (15 min on some feeds) | stale quotes presented as live | `as_of` in every response |
| no historical depth guarantee | backtests mislead | your warehouse for history |
| external dependency | network failure = tool failure | degrade to corpus data (W8 ladder) |

The capstone rule: prebuilt finance tools answer *"what is NVDA worth
now?"* — your warehouse answers *"what was our Q3 revenue?"*. Different
trust domains; the dual-pipeline routing (file 02-04) sends them to
different tools.

## 4. The honest tool description (prebuilt edition)

```python
tools=[YFinanceTools(stock_price=True,
                     tool_description_extension=
                     "Returns live-ish market data with up to 15 min "
                     "delay. Always state the as_of time when quoting "
                     "prices. Not for historical analysis.")]
```

The description carries the *limits* — the model cannot state a caveat
it was never told. This is the W10 docstring bar applied to a toolkit
you did not write: read its actual behavior, then write the description
that tells the truth about it.

## Exercises

1. Run the prebuilt toolkit; capture raw outputs for 5 queries; write
   the trust-level column (freshness, source opacity) for each.
2. Wrapper drill: add `verified_stock_price`; the answer's numbers must
   now carry `as_of` — verify in 3 responses.
3. Limit drill: rate-limit or block the tool (proxy); verify the retry
   + degradation path produces an honest "source unavailable" answer.

## Pitfalls

- Treating prebuilt tool output as ground truth — it is a source; the
  verification layer makes it citable.
- Demo-day rate-limit surprises — cache and backoff are not optional for
  external APIs.
- Historical analysis on live-quote feeds — wrong tool for the depth;
  your warehouse owns history.