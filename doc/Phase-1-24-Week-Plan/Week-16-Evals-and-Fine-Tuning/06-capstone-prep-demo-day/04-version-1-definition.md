# Version 1.0 Definition — The Five Bars

**What you'll learn:** the Version 1.0 definition: five measurable bars
that declare the capstone done — quality, reliability, cost, safety,
and documentation — each with its evidence and its gate.

## 1. The five bars

| Bar | Metric | Threshold | Evidence |
|---|---|---|---|
| 1. Quality | eval-set exact-match + judge | ≥85% numeric, judge ≥7 | the eval runs |
| 2. Reliability | success rate + trip rates | ≥90% success, rails <5% | the reliability ledger |
| 3. Cost | $/task | within the budget table | the optimization ledger |
| 4. Safety | red-team escape rate + containment | <5% escapes, zero leaks | the red-team rounds |
| 5. Documentation | the freeze checklist + all pin notes | 100% current | the freeze report |

The bars are the capstone's definition of done — five measurable
thresholds, five evidence artifacts. Every bar cites its gates and
drills from the program; "done" is a measurement, not a feeling.

## 2. The bars' gates (each bar is CI-checked)

| Bar | Gate | Source |
|---|---|---|
| quality | the value gate (W11 file 05-04) | the eval runs |
| reliability | the trip-rate gates (W15 file 01) | the budget ledger |
| cost | the budget table (W15 file 04) | the optimization ledger |
| safety | the federated injection battery (W14-05) | the red-team rounds |
| documentation | the freeze checklist (file 01) | the freeze report |

The gates convert the bars from goals to enforcement — the acceptance
command checks all five, and a red bar blocks the 1.0 tag.

## 3. The 1.0 tag (the process)

```text
1. run accept.py --full            → all six gates PASS
2. verify the five bars            → all five thresholds met
3. tag v1.0                        → the commit is the release
4. the release notes               → the five bars' evidence, linked
5. the roadmap continues           → 1.0 is a milestone, not the end
```

The tag is a git commit with the five bars' evidence linked — the same
release discipline as any software project, earned by 16 weeks of
gates.

## 5. The 1.0 scorecard (the five bars, measured)

```markdown
# Version 1.0 scorecard — [date]

| bar | threshold | measured | evidence |
|---|---|---|---|
| quality | ≥85% numeric, judge ≥7 | 87%, 7.1 | eval runs |
| reliability | ≥90% success, rails <5% | 93%, 2% | reliability ledger |
| cost | within budget table | 0.014/task | optimization ledger |
| safety | <5% escapes, 0 leaks | 3%, 0 | red-team rounds |
| documentation | freeze 100%, pins current | 10/10, current | freeze report |

verdict: 1.0 ✓ — tag [hash]
```

The scorecard is the 1.0 definition's measurement — five bars, five
thresholds, five evidence links. It is the release's receipt; the tag
is earned, not declared.

## 6. The 1.0-adjacent work (what 1.0 explicitly excludes)

| Excluded | Why | Where it goes |
|---|---|---|
| multi-user deployment | a different reliability class | the deployment sprint |
| fine-tuned models in production | the capstone uses the base + RAG | the extension weeks |
| real-time voice | the cascade is demo-grade | the voice roadmap |
| mobile/edge | a different serving stack | out of scope |

The exclusions are the 1.0 definition's boundary — the definition of
done includes what 1.0 *is not*. Each exclusion names its future home;
the exclusions prevent the scope creep that the freeze process exists
to block.

## 7. The 1.0 pin note (the release's manifest)

**Task:** extend `reports/sdk-versions.md` with the 1.0 block: the
scorecard's measured values, the gate versions, the release-notes
location, and the tag command.

**Worked approach:** the 1.0 pin is the release's record — the scorecard
is derived from the gates, and the pin ties the tag to its evidence.

**Pass criterion:** note committed; the tag command rehearsed.

## Exercises

1. Measure all five bars; produce the 1.0 scorecard; the gaps named with
   owners and weeks.
2. Gate drill: verify each bar's gate fires on a planted violation —
   the bars are enforced, not aspirational.
3. Tag rehearsal: simulate the 1.0 process end-to-end on a scratch
   branch; the release notes generated; the process rehearsed before
   the real tag.
4. Scorecard drill: render §5 from the gates' outputs; the measured
   values must match the gate logs — the scorecard is derived, not
   hand-written.
5. Exclusion drill: write §6; each exclusion's future home cited; the
   exclusions reviewed against the boundary memo's scope statement.