# Exercises — Prompt & Context Engineering

Expanded set with worked approaches. The deliverable: a tested
constitution, the fitter in production, and A/B evidence for your hints.

## 1. Constitution certification (from 01-agentic-constitution)

**Task:** write your 7-rule constitution; run the four battery cases at
3 runs each; produce the rule→case→result table; then the token diet
(compressed version) with pass rates.

**Worked approach:** the certification is the constitution's acceptance
test — a rule that fails its case gets reworded *before* any other
prompt work. The diet keeps only rules whose cases pass 3/3 without
them.

**Pass criterion:** 7/7 cases green on the full version; the diet's
savings reported in tokens with no case regression.

## 2. Observation spectrum coverage (from 02-observation-formatting)

**Task:** implement all six rows of the observation-spectrum table as
formatter functions; Tier-1 battery cases for each; verify no case leaks
paths or system text.

**Worked approach:** the six rows are the formatter's contract — one
function each, one battery case each, plus the leak check (regex for
absolute paths, `data/`, and system markers) on every output.

**Pass criterion:** 6/6 formatters + cases green; leak check clean over
100 generated observations.

## 3. The fitter in production (from 03-context-fitter)

**Task:** wire `fit_context` into the loop; run your 25-query eval; prove
P1–P6 hold on *real* layers (not just generated ones); report the
per-layer spend table.

**Worked approach:** the property suite runs on synthetic cases in CI;
the real-layer check is a one-off assertion pass over your trajectories —
both matter, because real corpora produce layer shapes generators miss.

**Pass criterion:** properties hold on all 25 real runs; spend table
committed; the optimization target named from the data.

## 4. Hint A/B, end to end (from 04-failure-phrasing)

**Task:** run the A/B on your two most common failure sites (from the
trajectory store's error counts); adopt winners; bump `HINT_VERSION`;
re-run the 25-query eval and report the aggregate recovery delta.

**Worked approach:** the loop is measure → reword → re-measure, with the
version stamp making the comparison clean. Expect 0.5–1.5 steps of
aggregate recovery improvement if your baseline hints were generic.

**Pass criterion:** A/B tables committed; trajectory store shows the
version boundary; aggregate delta reported.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Constitution certified (7/7 cases) | battery results | 4 |
| Observation spectrum: 6 formatters + cases | tests/ | 3 |
| Fitter properties on 200 synthetic + 25 real cases | property suite | 4 |
| A/B tables + HINT_VERSION boundary | reports/hint-ab.md | 3 |
| Token spend table with named target | reports/context-spend.md | 2 |

**Pass bar:** 12/16 to proceed to file 06 (the full agent). The
certification (4-pointer) is the deliverable — an untested constitution
is prose, not engineering.

## 7. The prompt architecture diagram

**Task:** draw the final prompt-architecture diagram (as text) in
`reports/prompt-architecture.md`: constitution → fitter layers →
observation formats → hint variants, with each block's version string
and token budget.

**Worked approach:** the diagram is the week's map — every block is a
tested artifact with a version, and the arrows are the fitter's priority
order. It is the picture file 06's assembly references.

**Pass criterion:** diagram (ASCII or mermaid) committed; every block's
version matches the trajectory-store stamps.

## 6. The prompt regression suite

**Task:** collect every prompt artifact you touched this week
(constitution, 6 observation formatters, hint variants) into one
pytest-marked suite (`-m prompts`) that runs in <60 s — the suite that
runs before any prompt edit merges.

**Worked approach:** the suite's speed comes from the canned LLM; its
coverage comes from the week's battery cases. Any prompt change without a
green run is a revert, the same rule as code.

**Pass criterion:** suite <60 s; one deliberate prompt break caught by
the right case (constitution case, formatter leak, or hint regression).

## Pitfalls recap

- Battery cases written for the rules you find easy — the failing rule is
  the one that needs the case.
- Formatters tested only on clean data — the six rows include the ugly
  states (0 hits, errors, truncation) by design.
- A/B conclusions from n=2 — ten runs per variant or the noise wins.
