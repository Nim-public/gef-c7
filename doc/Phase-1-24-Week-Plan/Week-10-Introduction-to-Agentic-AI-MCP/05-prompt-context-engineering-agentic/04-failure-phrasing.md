# Failure Phrasing — A/B Measured Rewording

**What you'll learn:** error hints are prompt-engineering variables with
measured effects: an A/B protocol for phrasings, the effect sizes you can
expect, and the maintenance loop that keeps hints calibrated to your
model.

## 1. The A/B protocol, per failure site

```python
VARIANTS = {
    "unknown_id": {
        "A": "Error: unit not found.",
        "B": ("unit_id 'X' not found. Valid ids look like u042 or u042::r2 "
              "(region crops). Call retrieve() first to list ids."),
    },
    "zero_hits": {
        "A": "No results.",
        "B": ("No units matched. Try broader terms, drop the modality "
              "filter, or check spelling of names/codes."),
    },
}

def ab_test(site: str, n: int = 10) -> dict:
    res = {}
    for variant, text in VARIANTS[site].items():
        runs = [run_with_forced_error(site, text) for _ in range(n)]
        res[variant] = {"recovery_steps": mean(r.steps_to_recover for r in runs),
                        "success": mean(r.outcome == "success" for r in runs)}
    return res
```

Forced errors make the test deterministic: a canned LLM that always hits
the failure site; the *model under test* still runs for real. Recovery
steps is the metric; success rate is the guardrail.

## 2. What phrasings move the needle (typical deltas, verify on yours)

| Site | Weak → strong change | Effect on recovery steps |
|---|---|---|
| unknown id | add valid id shapes + next action | 2.8 → 1.1 |
| zero hits | add fallback strategies | 2.4 → 1.3 |
| schema violation | name the field and type | 2.2 → 1.1 |
| timeout | add "narrow the query" | 2.0 → 1.2 |
| repeated call | name the repetition explicitly | loop exits 1–2 steps sooner |

The pattern in every winner: *state the constraint, show the shape, name
the next action*. Hints that explain without directing produce polite
loops.

## 3. Hint maintenance — hints rot like descriptions

| Trigger | Action |
|---|---|
| model bump | re-run the A/B on all sites (1 evening) |
| recovery steps regress >0.5 | inspect the site's trace; rephrase |
| new tool added | its error hints enter the A/B rotation |
| reject reasons from HITL (file 04) | mine for new hint content |

```python
HINT_VERSION = "hv3"      # stamped into trajectories

def log_hint_version(t: dict) -> dict:
    return {**t, "hint_version": HINT_VERSION}    # A/B results stay comparable
```

The version stamp makes hint changes auditable in the trajectory store —
recovery-step trends split cleanly across hint versions.

## 4. The phrasing rules, distilled from the winners

1. **Constraint first** — "ids look like u042", before any apology.
2. **Shape over prose** — show the pattern, not a sentence about it.
3. **One next action** — "call retrieve() first", never a menu.
4. **No blame, no filler** — "Invalid: k must be 1–20" beats "Oops! It
   seems the value was unfortunately out of range."
5. **Bounded length** — hints over ~40 tokens get skimmed; measure at 200
   chars.

## Exercises

1. Run the A/B on two failure sites from your traces; commit the table
   with recovery steps and success rates per variant.
2. Winner-integration drill: adopt the winning phrasings; bump
   `HINT_VERSION`; verify the trajectory store splits cleanly across the
   version boundary.
3. Rule-application drill: rewrite one hint from scratch using the five
   rules; predict its recovery steps before the A/B — calibrating your
   own prompt-engineering intuition is the meta-skill.

## Pitfalls

- A/B with n=1 per arm — recovery steps are noisy; 10 runs per variant
  minimum, report the mean and range.
- Hints edited without version stamps — trends become unattributable.
- Phrasings optimized for *your* taste rather than the model's recovery —
  the metric decides, not the prose.

## Resources

- [`../02-tools-and-memory/02-tool-registry.md`](../02-tools-and-memory/02-tool-registry.md)
  — the hint sources; [`../04-measuring-agents-patterns/`](../04-measuring-agents-patterns/)
  — the recovery-step metric.
- Your trajectory store — the A/B's measurement substrate.
