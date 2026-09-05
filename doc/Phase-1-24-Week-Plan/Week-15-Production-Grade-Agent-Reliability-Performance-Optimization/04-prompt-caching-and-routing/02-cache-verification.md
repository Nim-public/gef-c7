# Cache Verification — `cached_tokens` in Billing

**What you'll learn:** verifying the cache discount in the billing
response: the `cached_tokens` field (OpenAI) and equivalents, the
discount math, and the verification test that proves the reorder
actually saves money.

## 1. Reading the billing response

```python
resp = client.chat.completions.create(model=..., messages=messages)
usage = resp.usage
print(usage.prompt_tokens)               # total prompt tokens
print(usage.prompt_tokens_details.cached_tokens)  # served from cache
```

| Field | Meaning | Billing |
|---|---|---|
| `prompt_tokens` | total prompt | full price on uncached |
| `cached_tokens` | prefix served from cache | discounted (typically 50–90% off) |
| `completion_tokens` | the answer | full price, always |

The discount is the provider's pricing table applied to `cached_tokens`
— your ledger computes the effective rate per call and the harness
tracks the trend. The W9-04 ledger gains two columns: `cached_tokens`
and `effective_prompt_cost`.

## 2. The verification test

```python
def test_prefix_cache_working():
    # same stable prefix, two calls:
    r1 = client.chat.completions.create(model=..., messages=MSGS)
    r2 = client.chat.completions.create(model=..., messages=MSGS)
    cached = r2.usage.prompt_tokens_details.cached_tokens
    assert cached >= 0.8 * r2.usage.prompt_tokens, (
        f"cache not hitting: {cached}/{r2.usage.prompt_tokens}")
```

| Observation | Meaning |
|---|---|
| second call: `cached_tokens ≈ prompt_tokens` | the prefix is caching |
| second call: `cached_tokens = 0` | the prefix changed or is too short |
| cache hits only sometimes | something variable leaks into the prefix |

The test is the reorder rule's acceptance gate: run it after every
prompt change. The minimum-prefix-length rule (providers typically
cache from 1024 tokens) goes in the same test — a 200-token constitution
may not cache at all.

## 3. The savings math (the ledger's row)

```python
def effective_cost(prompt_tokens: int, cached_tokens: int,
                   price_full: float, price_cached: float) -> float:
    uncached = prompt_tokens - cached_tokens
    return uncached * price_full + cached_tokens * price_cached

# your constitution+tools prefix: 2000 tok; discount 50%:
# full: 2000 × p   vs   effective: 0 × p + 2000 × 0.5p  → 50% saved
```

| Scenario | Tokens/call | With 50% cache discount |
|---|---|---|
| 2k stable + 500 variable, 100 calls/day | 250k prompt | 175k-equivalent (−30%) |
| agent loop (6 turns, same prefix) | 6 × prefix | prefix paid once per session |

The agent loop is the multiplier: six turns sharing one prefix pay the
prefix once (or at the cached rate six times) — the savings compound
with conversation length.

## 5. The cache pin note (the savings' manifest)

```markdown
# Prompt caching (W15)
- reorder: stable/variable split, audit at 100%
- provider: [yours], min prefix 1024 tok, discount [measured]
- verification: test_prefix_cache_working (CI, after prompt changes)
- savings: [measured $/task before vs after]
```

The pin note is the caching decision's record — the reorder, the
measured discount, the verification test, and the savings. It is the
deployment memo's cost chapter, one block.

## Exercises

1. Implement the verification test; run it against your reordered
   prompt; the cache must hit on the second call.
2. Ledger drill: add `cached_tokens` + effective cost to the trajectory
   rows; run the eval set; report the savings vs the unreordered
   baseline.
3. Minimum-length drill: shrink the stable prefix below the provider's
   minimum; observe the cache stop hitting — the floor, discovered.
4. Pin drill: write the note; the savings row cites the ledger.