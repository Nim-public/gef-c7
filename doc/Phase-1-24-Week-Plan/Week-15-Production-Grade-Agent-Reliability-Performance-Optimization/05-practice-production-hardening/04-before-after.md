# Before/After — p95, $/task, Quality

**What you'll learn:** the production week's final table: every metric
before and after hardening, with the deltas attributed to the ledger —
p95 latency, cost per task, and quality all improving or honestly
traded.

## 1. The table

| Metric | Before (W14 baseline) | After (W15) | Δ | Attribution |
|---|---|---|---|---|
| success rate | 0.80 | 0.87 | +0.07 | reliability layer |
| p50 latency | 3.1 s | 2.9 s | −6% | caching |
| p95 latency | 6.2 s | 4.8 s | −23% | budget + retries |
| $/task | 0.021 | 0.014 | −33% | caching + routing |
| quality (judge) | 6.8 | 6.9 | +0.1 | parity (no regression) |
| spend-rail trips | unbounded | 2% | bounded | RunBudget |

Fill from your runs — the attribution column cites the ledger (file 03)
and every delta is explainable. A metric that *worsened* gets a row too
(verification tokens) with its justification: honesty costs tokens and
is worth it.

## 2. The quality row (the trade's guard)

| Check | Before | After | Verdict |
|---|---|---|---|
| 15-case exact-match | 12/15 | 12/15 | no regression |
| citation gate | 100% | 100% | no regression |
| judge total | 6.8 | 6.9 | +0.1 (noise or better) |

The quality row is the trade's guard: cost and latency improvements
that regress quality fail the memo. The 15-case set and the judge are
the arbiters — the same artifacts as every week, one more column.

## 3. The table's presentation (the demo page)

```markdown
## Production hardening results (W15)
[baseline: reports/baseline-w15.json]
[ledger: reports/optimization-ledger.md]

| metric | before | after | Δ | attribution |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

Every number is reproducible: py scripts/accept.py --full
```

The presentation cites the baseline and the ledger, links the
acceptance command, and states the quality guard. It is the capstone's
production chapter — the before/after table *is* the hardening week.

## 5. The before/after's audit trail (the table's evidence chain)

| Table cell | Evidence chain |
|---|---|
| before value | `reports/baseline-w15.json` + its run ids |
| after value | the eval run ids + the ledger rows |
| Δ | arithmetic on the two, shown |
| attribution | the ledger row + its isolated runs |

The evidence chain is the table's auditability — every cell traces to
committed artifacts, and the chain is walkable by a reviewer in minutes.
The chain is also the anti-fraud mechanism: a number that cannot show
its chain is removed from the table.

## 6. The quality deep-dive (the trade's fine print)

| Quality check | Before | After | Method |
|---|---|---|---|
| numeric exact-match | 12/15 | 12/15 | the parser |
| citation gate | 100% | 100% | the pairing audit |
| judge rubric | 6.8 | 6.9 | calibrated judge |
| refusal honesty | 5/5 | 5/5 | the insufficiency battery |
| parity vs graph | 15/15 | 15/15 | the W13 test |

The deep-dive breaks "quality" into its five measurable faces — the
guard is only as strong as its narrowest check, and the table shows
which check is binding. The verification tokens' premium bought the
numeric row's stability; the trade's fine print is the memo's
justification.

## 7. The before/after pin note (the table's manifest)

**Task:** extend `reports/sdk-versions.md` with the before/after record:
the baseline JSON hash, the after-state run ids, the quality-guard
results, and the table-regeneration command.

**Worked approach:** the table is the week's headline — the pin note
makes it reproducible: the baseline hash, the after run ids, and the
command that regenerates the markdown.

**Pass criterion:** note committed; the regeneration command reproduces
the table byte-identically.

## Exercises

1. Run the after-state eval; fill the table; verify the attribution
   column against the ledger.
2. Quality-guard drill: confirm the quality row shows no regression; if
   it does, the optimization that caused it reverts (the trade's rule).
3. Demo-page drill: render §3 into the capstone README; every number
   traces to the ledger and the baseline.
4. Chain drill: pick three cells; walk each evidence chain live for a
   reviewer — the walk is the table's acceptance test.
5. Deep-dive drill: fill §6 for your after-state; the narrowest check
   gets a named watch-item for Week 16.