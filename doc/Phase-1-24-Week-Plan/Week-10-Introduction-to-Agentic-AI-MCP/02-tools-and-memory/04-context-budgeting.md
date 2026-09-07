# Context Budgeting — Truncation, Compression, Per-Layer Costs

**What you'll learn:** the context fitter: a deterministic function that
assembles each step's context under a hard budget, with a fixed priority
order and measured per-layer costs — the difference between an agent and
a token bonfire.

## 1. The budget table, measured (your corpus, 8k window)

| Layer | Budget | Measured cost (typical step) | Compression rule |
|---|---|---|---|
| System + constitution | 400 | 380 | never compress |
| Tool schemas | 600 | 520 (5 tools) | drop tools, not fields |
| Scratchpad | 300 | 120–300 | summarize oldest note first |
| Closed history steps | 2500 | 180/step raw | closed → one line each |
| Open (current) step | 400 | 250 | never compress mid-step |
| Retrieved context | 3500 | 2900 (top-6) | W9-04 top-K trim |
| Answer reserve | 700 | — | untouchable |

```python
PRIORITIES = ["system", "schemas", "open_step", "retrieved",
              "scratchpad", "closed_history"]      # cut from the end

def fit_context(layers: dict[str, str], budgets: dict[str, int]) -> dict:
    out, over = {}, 0
    for name in PRIORITIES:
        tok = count(layers.get(name, ""))
        budget = budgets[name] + (over if name in ("scratchpad", "closed_history") else 0)
        if tok <= budget:
            out[name] = layers[name]; over += budget - tok
        else:
            out[name] = compress(name, layers[name], budget)
            over = 0
    return out
```

The fitter is pure and testable: same layers in, same context out —
determinism discipline, applied to prompts.

## 2. Compression that teaches (not truncates blindly)

| Layer | Bad cut | Good cut |
|---|---|---|
| Observation | mid-JSON `...{trunc` | fields in order, `[+3 more hits]` tail |
| Closed step | delete entirely | `step2: get_unit_text(u042) → margin 12.4%` |
| Scratchpad | drop newest | merge related notes into one line |
| Retrieved snippets | chop the middle | top-K by score, score visible |

The principle: compression preserves *the decision-relevant surface* —
ids, numbers, scores — and deletes verbosity. The unit tests assert
exactly that (ids survive, numbers survive).

## 3. The cost ledger per step (file 04's first input)

```python
def step_tokens(layers: dict) -> dict:
    return {k: count(v) for k, v in layers.items()}

# one 6-step trajectory, summed:
#   system 380×6=2280 | schemas 520×6=3120 | obs 180×6=1080
#   retrieved 2900×6=17400 | answer 210 → total ≈ 24k tokens
```

Read the ledger: retrieved context is 72% of spend — the agent's real
cost is your RAG layer, not the loop. Optimizing the loop before the
retrieval budget is optimizing 3% of the bill.

## 4. Paging over truncation for the long tail

When history *must* exceed budget (deep multi-hop), page instead of cut:

```python
def page_history(closed: list[str], page: int = -1, per_page: int = 4) -> str:
    chunk = closed[page * per_page: (page + 1) * per_page]
    tail = f"[page {page+1}/{(len(closed)+per_page-1)//per_page}; " \
           f"call history_page(p) for more]"
    return "\n".join(chunk) + "\n" + tail
```

The agent can *call* `history_page(0)` — memory access becomes a tool
with a schema, which is the whole trick: the fitter bounds the default;
the agent pays tokens only when it decides the older steps matter.

## Exercises

1. Implement `fit_context` + `compress` for your layers; property-test
   that ids and numbers always survive compression.
2. Ledger drill: token-account 5 real trajectories; produce the per-layer
   spend table; name the layer to optimize first (it will be retrieved
   context).
3. Paging drill: force a 12-step trajectory; verify the agent uses
   `history_page` at most once and the answer still cites correctly.

## Pitfalls

- Counting tokens with `len(text)/4` in tests — use the real tokenizer;
  the 25% error flips budgets.
- Compressing the open step — partial observations mid-decision produce
  confident nonsense.
- Budgets without the answer reserve — long contexts silently starve the
  answer; the reserve is untouchable by construction.

## Resources

- Your Week-09 budget (retrieved-context layer); file 04 — the harness
  that consumes these ledgers.
- `tiktoken`/model tokenizer docs for `count()`.
