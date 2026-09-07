# 08.3 — Feasibility & the Mentor Pitch

> Subfolder index: [README.md](README.md) · Parent: [../08-capstone-task-formalize-scope.md](../08-capstone-task-formalize-scope.md)

---

## What you'll learn

- The feasibility checks as *experiments you run this week* (not opinions)
- The red-flag catalog and the go/no-go decision
- The 5-slide mentor pitch that survives a reviewer

## 1. Feasibility checks = experiments

Each check is a 30–60 minute experiment with a pass/fail output:

| Check | Experiment | Pass |
|---|---|---|
| **Data access** | export/download 100+ rows today | file in hand, schema readable |
| **Extraction** | run W1-04 extraction on 3 sample docs | >80% of pages clean (file W1-04 audit) |
| **Scrubbing** | run the PII scrubber on 20 records | zero unmasked PII in output |
| **Baseline** | train the W1-05 classifier on your labels | per-class F1 ≥ 0.6 |
| **Cost** | estimate tokens × price for one full query (W1-01.5) | ≤ budget per interaction |
| **Latency** | time one end-to-end prototype query | ≤ your SLA (e.g., 5 s) |
| **Eval** | label 20 reference answers | agreement across 2 labelers ≥ 80% |

A check that fails isn't a project-killer — it's a **decision input**: switch source, change scope, or add a mitigation. The failure to avoid is *not running* the checks.

## 2. The red-flag catalog

| Red flag | Why fatal | Mitigation |
|---|---|---|
| data behind approvals you don't control | timeline hostage | plan B source or scope change |
| no ground truth and none buildable | nothing is evaluable | build 20 labels first (W16-01) |
| "we'll collect data during the capstone" | no base to iterate on | start with public data, swap later — in writing |
| success metric undefined | no way to know if it works | define one number before building |
| one person holds all data knowledge | bus factor 1 | document exports + schemas (W1-04) |
| pipeline depends on a deprecated API | time bomb | pin + fallback (W2-01) |

Each red flag maps to a mitigation *in writing* — the scope doc's risks section (W1-08 §2's format).

## 3. The 5-slide mentor pitch

| Slide | Content | The question it answers |
|---|---|---|
| 1. Problem | user, cost, volume — numbers | "why does this exist?" |
| 2. Demo-able capability | input → output, one sentence, one example | "what will we see?" |
| 3. Architecture | your W16-06 frozen stack on one diagram | "how does it work?" |
| 4. Evidence | the metrics table (W15-05-style) + eval design | "how do you know?" |
| 5. Risks & plan | top-3 risks with mitigations, the sprint plan | "what could go wrong?" |

Slide discipline: every slide has **one number or one diagram** — prose slides are where claims hide. Rehearse with the weakest-question-first rule: open the Q&A with the question you most fear.

## 4. The go/no-go decision (explicit)

```markdown
## Decision: GO (as of 2026-11-20)
- All 7 feasibility checks passed (evidence: feasibility.md)
- 2 accepted risks: portal export may change schema (mitigation: adapter);
  12% of tickets need manual routing (mitigation: escalation path)
- NO-GO triggers for v2: eval agreement < 70%, data access revoked,
  baseline F1 < 0.5 after data cleanup
```

The go decision names its **no-go triggers** — the conditions under which you'd stop or pivot. Explicit triggers convert sunk-cost debates into checks.

## Exercises

1. Run all 7 feasibility checks on your project this week; produce the evidence file (one row per check: result, artifact link, date).
2. Red-flag scan: score your project against the §2 catalog — any flags present? Write the mitigation for each before the mentor session.
3. Build the 5 slides; rehearse with a peer playing the harshest reviewer — collect the 3 hardest questions and answer them in writing.
4. No-go trigger design: define 3 explicit triggers for your project with measurable conditions (e.g., "baseline F1 < 0.5 after data cleanup").
5. Pitch teardown: watch a product pitch (any demo day video); classify its slides against §3's table — what did it do that yours doesn't?

## Pitfalls

- **Pitching before checking** — the first mentor question will be a failed feasibility check you skipped
- **Risks without owners** — every mitigation needs a name and a date
- **The demo-prompt hedge** — rehearsing only the happy path; the demo dies on the first unexpected input (W10-01's max-steps lesson)
- **Metrics on synthetic-only data** — demo numbers must come from real data runs (W16-02's honesty rule)
- **No decision recorded** — go/no-go with triggers, in writing, dated

## Resources

- W1-08 parent (template + red flags), W16-06 (1:1 checklist), W12-04 (comparison discipline) — composed here
- W15-05/W14-06 (the baseline tables slide 4 cites)
- The scope doc (file 01) — the pitch's source material
