# Sprint Roadmap — W17–24 Exit Artifacts

**What you'll learn:** the extension weeks' roadmap: each sprint's exit
artifact defined before the sprint starts — the roadmap that makes the
extension weeks deliverable instead of exploratory.

## 1. The sprint table

| Sprint | Theme | Exit artifact | Gate |
|---|---|---|---|
| W17–18 | Deep agents / advanced orchestration | a new working topology + its battery | battery green |
| W19–20 | Advanced eval / red-team rounds 2–3 | the red-team report + new defenses | escape <5% |
| W21–22 | Production deployment | deployed app + monitored | acceptance green |
| W23–24 | Capstone polish | final report + demo | the five bars (file 04) |

| Column | Rule |
|---|---|
| theme | one sentence |
| exit artifact | a committed file/report the sprint *must* produce |
| gate | the check that says the artifact is real |

The exit artifacts convert the roadmap from intentions to commitments —
a sprint without an exit artifact is a wish.

## 2. The extension weeks' priorities (from your weak slices)

The W16 slice analysis and the W15 signals set the priorities:

| Priority source | Sprint it feeds |
|---|---|
| the weakest slice (W16-02) | the first deep-dive sprint |
| the largest red-team escape class | the red-team rounds |
| the production signals' alarms | the deployment sprint |

The roadmap is *derived from your data* — the same evidence-driven
planning as every decision memo in the program.

## 3. The roadmap's discipline (the standing rules)

```text
[ ] every sprint has one exit artifact (not three)
[ ] every exit artifact has a gate (a check that says done)
[ ] the gates join the CI inventory (W14-04-05 onboarding)
[ ] the roadmap is committed and reviewed at each sprint's end
```

## 5. The roadmap's risk register (what could derail each sprint)

| Sprint | Top risk | Mitigation |
|---|---|---|
| W17–18 orchestration | scope creep into new frameworks | the W12 verdict holds; extend, don't migrate |
| W19–20 red-team | escape rates don't fall | budget the fixes; report honestly |
| W21–22 deployment | hosting costs exceed the budget | the W15 cost model gates the scale |
| W23–24 polish | quality regressions from late changes | the freeze process gates changes |

The risk register is the roadmap's honesty — each sprint's most likely
derailment named with its mitigation. The register is reviewed at each
sprint's end; risks that fired get post-mortems.

## 6. The roadmap's review cadence (the standing schedule)

| When | Review | Output |
|---|---|---|
| each sprint's end | the exit artifact vs its gate | the roadmap row's verdict |
| monthly | the risk register review | risks re-scored |
| per release | the five bars re-measured | the scorecard updated |

The cadence is the roadmap's heartbeat — each review produces a
recorded verdict, and the risk register's re-scoring keeps the
mitigations honest. The cadence is committed in the roadmap's header;
missed reviews are visible in the file's history.

## Exercises

1. Fill the sprint table with your themes, exit artifacts, and gates;
   commit as `doc/capstone/roadmap.md`.
2. Gate-onboarding drill: the first sprint's gate joins CI via the W14
   onboarding procedure — the roadmap and the gates integrate from day
   one.
3. Review drill: at the first sprint's end, review the exit artifact
   against its gate; the review's verdict is recorded in the roadmap.
4. Risk drill: add one risk per sprint from your own history; the
   mitigation column cites the program's artifacts.
5. Cadence drill: write the §6 schedule; the first monthly review
   scheduled with the risk register on the agenda.

## 7. The roadmap pin note (the extension weeks' manifest)

**Task:** extend `reports/sdk-versions.md` with the roadmap block: the
sprint themes, their exit artifacts, their gates, and the cadence
schedule (file 01-06 of W13 for the review rhythm).

**Worked approach:** the roadmap's pin records the extension plan —
the same manifest discipline as every artifact, applied to time.

**Pass criterion:** note committed; the first sprint's gate in CI.

## Pitfalls

- Hierarchical "because it sounds smarter" — the manager is a token tax
  with a plan-quality risk; earn it with an unknown-order requirement.
- Sequential pipelines that secretly need runtime branching — the list
  order lies; move to hierarchical or a Flow with conditions.
- Manager plans unasserted — a skipped task is a silent missing
  deliverable; coverage assertions or it did not happen.