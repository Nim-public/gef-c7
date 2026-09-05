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