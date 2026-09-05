# The Context Fitter — Priorities, Truncation, Paging

**What you'll learn:** the deterministic assembler that builds each step's
context under the budget table — priority order, per-layer compressors,
and the paging escape hatch — with property tests as the spec.

## 1. The fitter, complete

```python
PRIORITIES = ["system", "schemas", "open_step", "retrieved",
              "scratchpad", "closed_history"]      # cut from the end

BUDGETS = {"system": 400, "schemas": 600, "open_step": 400,
           "retrieved": 3500, "scratchpad": 300, "closed_history": 2500}
RESERVE = 700                                   # answer, untouchable

def fit_context(layers: dict[str, str], budgets=BUDGETS) -> dict[str, str]:
    out, slack = {}, 0
    for name in PRIORITIES:
        raw = layers.get(name, "")
        b = budgets[name] + (slack if name in ("scratchpad", "closed_history") else 0)
        if count(raw) <= b:
            out[name] = raw
            slack += b - count(raw)
        else:
            out[name] = COMPRESSORS[name](raw, b)
            slack = 0
    assert count("".join(out.values())) + RESERVE <= TOTAL
    return out
```

Two properties make it an engineering artifact rather than a prompt
template: **determinism** (same layers in, same context out) and **the
reserve** (the answer never gets starved by an earlier layer).

## 2. The compressor set — one per layer

| Layer | Compressor | Preserves |
|---|---|---|
| system | never compresses | the constitution |
| schemas | drop whole tools, never fields | callable surface integrity |
| open_step | never compresses | the in-flight decision |
| retrieved | top-K by score, scores visible | the stop-rule signal |
| scratchpad | merge/summarize oldest notes | conclusions, ids |
| closed_history | one line per step | step→result map |

```python
def compress_closed(steps: list[str], b: int) -> str:
    lines = [f"s{i}: {t}→{r}" for i, (t, r) in enumerate(steps)]
    while count("\n".join(lines)) > b and len(lines) > 2:
        mid = len(lines) // 2
        lines[mid] = f"s{mid}: [summarized: {steps[mid][0][:30]}…]"
    return "\n".join(lines)
```

Middle-out summarization: the *current* and *first* steps survive;
the middle collapses first — recent and founding context are the
decision-relevant ends.

## 3. Paging as the escape hatch

When the long tail legitimately needs depth, page instead of cut (file
02's sketch, completed):

```python
@mcp-host-side tool
def history_page(page: int) -> str:
    """Read older agent steps. Pages are 4 steps; page 0 is oldest."""
    chunk = CLOSED[page * 4: (page + 1) * 4]
    return "\n".join(chunk) + f"\n[page {page}/{(len(CLOSED)+3)//4 - 1}]"
```

Memory access becomes a *tool call the agent pays for* — the default
context stays bounded, and deep-dive cost lands only on trajectories that
need it. The battery adds one case: the agent uses `history_page` at most
once per episode.

## 4. The property suite is the fitter's spec

| Property | Assertion |
|---|---|
| P1 budget | every layer ≤ its (possibly slack-boosted) budget |
| P2 total | all layers + reserve ≤ window |
| P3 id survival | every `[u\d+]` in input appears in output |
| P4 number survival | decimal/percent tokens survive |
| P5 determinism | same input → byte-identical output |
| P6 priority | cuts never touch layers before the first overflowing one |

```python
@given(st.layers(), st.budgets())
def test_fitter_properties(layers, budgets):
    out = fit_context(layers, budgets)
    assert_p1(out, budgets); assert_p2(out)
    assert_p3(layers, out); assert_p4(layers, out)
    assert_p5(layers, budgets); assert_p6(layers, out)
```

Six properties, one test function — the fitter is now refactor-proof:
any prompt-template change must still satisfy them.

## Exercises

1. Implement the fitter + six compressors; wire the property suite; fix
   until green over 200 generated cases.
2. Ledger drill: token-account 5 real trajectories before and after the
   fitter; report per-layer spend — the optimization target is now data.
3. Paging drill: force a 12-step trajectory; verify the agent pages at
   most once, and the paged-in steps actually appear in the final answer's
   reasoning (grep the trace).

## Pitfalls

- Fitters that "usually fit" — the budget assert is hard; overflow must
  fail loudly in tests, never silently in prod.
- Compressing the open step — partial observations mid-decision produce
  confident nonsense; the priority list exists to prevent exactly this.
- Paging without a battery case — the escape hatch becomes the default
  path the first time the budget is set too tight.

## Resources

- [`../02-tools-and-memory/04-context-budgeting.md`](../02-tools-and-memory/04-context-budgeting.md)
  — the budget table and fitter sketch this file completes.
- Hypothesis docs — the property-test harness for P1–P6.
