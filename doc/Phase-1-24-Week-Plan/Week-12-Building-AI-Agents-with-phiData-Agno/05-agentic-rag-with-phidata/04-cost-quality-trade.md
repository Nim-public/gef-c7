# Cost & Quality Trade — Token and Latency Tables

**What you'll learn:** the agentic-RAG price tag: per-class token and
latency comparisons against fixed RAG, the breakdown of where agentic
spends its extra tokens, and the trade table that goes in the decision
memo.

## 1. The cost table

| Class | Mode | p50 tokens | p50 latency | R@5-equivalent |
|---|---|---|---|---|
| simple lookup | fixed | 3.1k | 2.1 s | 0.85 |
| simple lookup | agentic | 4.4k | 2.9 s | 0.86 |
| multi-hop | fixed (2×) | 7.2k | 3.8 s | 0.55 |
| multi-hop | agentic | 8.1k | 4.6 s | 0.71 |
| chitchat | fixed | 3.4k | 2.2 s | n/a (wasted) |
| chitchat | agentic | 0.9k | 0.8 s | n/a |

Fill with your numbers — the shape is what transfers: **agentic costs
more where fixed was already right, and wins where fixed was wrong.**
The blended cost is the weighted sum over your class distribution.

## 2. Where agentic's extra tokens go

| Component | Fixed | Agentic | Why the delta |
|---|---|---|---|
| retrieval calls | 1 | 1.6 avg | model iterates |
| tool-result tokens in context | 1 batch | each call's results | fitter handles, still costs |
| routing overhead | 0 (regex) | ~150 tok (decision turn) | the control-flow transfer |
| answer | same | same | — |

```python
def blended_cost(dist: dict[str, float], cost_by_class_mode: dict) -> float:
    return sum(p * cost_by_class_mode[c][m] for c, p in dist.items()
               for m in [mode_of(c)])   # per your boundary memo's mapping
```

The breakdown exists because the *fix* differs by component: routing
overhead is intrinsic; extra retrieval calls are a stop-rule problem
(file 02-03's battery); repeated context stuffing is a fitter problem.

## 3. The quality side (what the extra tokens buy)

| Metric | Fixed | Agentic | Verdict |
|---|---|---|---|
| answer groundedness | high (always cited) | high *if* searched | floor required |
| coverage (multi-hop) | miss-prone | strong | agentic's win |
| refusal honesty | strong | strong (battery) | tie |
| route robustness on novel queries | weak | strong | agentic's win |

The trade is not "cost up, quality down" — it is *cost up on easy
queries, quality up on hard ones*. The class table (§1) is where the
blend is chosen.

## 4. The decision-memo table (the deliverable)

```markdown
## Agentic RAG trade (W12)
| class | mode | why |
|---|---|---|
| simple lookup | fixed | −30% tokens, same quality |
| multi-hop | agentic | +16 pts quality, +12% tokens |
| chitchat | agentic w/ floor | −74% tokens (skip works) |
| exact-term | fixed (regex pre-router) | recall-critical |
Blended: +8% tokens, +9 pts quality vs all-fixed.
```

The same memo discipline as W11's verdict: numbers, per-class decisions,
a blended row, a revisit trigger.

## 5. The quality measurement (the other half of the trade)

Cost without quality measurement is half a decision. The quality rows:

| Metric | Instrument | Source |
|---|---|---|
| groundedness | citation gate pass rate | harness |
| coverage (multi-hop) | R@5-equivalent per hop | eval set |
| refusal honesty | absent-fact battery | insufficiency battery |
| route robustness | head-to-head (file 03) | route table |

The agentic verdict needs *both* tables — cost up is only acceptable
where quality up is measured. The two tables land side by side in the
decision memo (file 01's row), each citing its instrument.

## Exercises

1. Measure both modes over the eval set; produce the §1 table with your
   numbers; compute the blended row over your class distribution.
2. Component drill: attribute the agentic delta — routing vs extra
   retrieval vs context stuffing (the fitter's ledger splits it).
3. Memo drill: write the §4 table; one class must stay fixed (justify
   with recall numbers) or the memo is incomplete.

## Pitfalls

- Cost tables without the class split — the blended number hides the
  whole point (agentic wins the tail).
- Quality measured only on easy queries — agentic's wins are on hard
  ones; the eval set's multi-hop rows carry the verdict.
- Token deltas accepted without breakdown — routing overhead is
  intrinsic, spirals are fixable; the component drill tells you which
  you have.