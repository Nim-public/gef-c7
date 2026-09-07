# Exercises — Eval Strategy & Ragas

Expanded set with worked approaches. The deliverable: the four metrics
implemented as diagnoses, the slice tables, the signal catalog, and the
versioned eval set.

## 1. The four metrics (from 01-ragas-revision)

**Task:** implement the four metrics on your 15-case set; produce the
diagnosis-tree path per case; group cases by leaf.

**Worked approach:** the diagnosis tree is the metrics' action layer —
each case lands on a leaf, and leaves group into fixes. The claim-
splitter is the faithfulness metric's real work; improve it before
trusting the scores.

**Pass criterion:** four metrics × 15 cases; leaf groups committed; the
most common leaf named as the next fix.

## 2. Slice analysis (from 02-slice-analysis)

**Task:** build the route × doc-type slice table; mark the weakest
slice; apply its mapped action; re-run and confirm the improvement.

**Worked approach:** the weak slice's fix comes from the slice-to-action
mapping — the fix is a named week's artifact, not an improvisation. The
re-run proves the mapping or corrects it.

**Pass criterion:** the table committed; the weakest slice improved (or
the mapping corrected with evidence).

## 3. Offline/online bridge (from 03-offline-vs-online)

**Task:** implement the signal catalog's thresholds; cross one with
synthetic traffic; walk the six bridge steps; the eval set gains the
case family.

**Worked approach:** the bridge is the self-improving loop with a faster
trigger — the six steps turn a live signal into a permanent guard. The
gold-label step is the honest one (facts from data).

**Pass criterion:** the signal dashboard table; the bridged case family
in the eval set's changelog.

## 4. Dataset versioning (from 04-dataset-versioning)

**Task:** restructure into the version model; write the changelog;
create the dev/held-out split; verify class-distribution parity.

**Worked approach:** the freeze is the discipline — v1 becomes immutable
and the changelog explains v2. The held-out split's parity check
(stratified by class) prevents a skewed reserve.

**Pass criterion:** versions frozen; changelog committed; the split
parity verified.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Four metrics + diagnosis tree | per-case leaves | 4 |
| Slice table + weakest slice fixed | slice report | 4 |
| Signal catalog + bridge walked | dashboard + changelog | 3 |
| Version model + held-out split | version files | 4 |
| Metric dictionary updated | dictionary | 2 |

**Pass bar:** 15/18 to proceed to file 02 (synthetic data). The
diagnosis tree (4-pointer) is the eval week's action layer — scores
that name fixes, not just numbers.

## 6. The eval-strategy pin note (the eval layer's manifest)

**Task:** extend `reports/sdk-versions.md` with the eval layer: metric
implementations (yours vs Ragas, versioned), slice gates, signal
thresholds, and the dataset governance page — one block.

**Worked approach:** the eval layer's manifest records which metric
implementations and threshold sets the scores came from — the same pin
discipline as every policy artifact.

**Pass criterion:** the manifest lists the eval stack with green
commands as recorded.

## 7. The eval-strategy review page

**Task:** write `reports/eval-strategy-review.md`: the diagnosis tree,
the slice gates, the signal dashboard, and the governance page — the
eval week's face, composing files 01–04.

**Worked approach:** the review composes the drills into one evidence
sheet — the reviewer question is "how do you know the scores mean
anything?" and each section answers with its calibration or governance
evidence.

**Pass criterion:** the page answers the trust question in one read,
citing the drills and the governance checks.

## Pitfalls recap

- Faithfulness without claim splitting — one-sentence answers score
  artificially high; the splitter is the metric.
- Slice tables with three dimensions — cells too small to read; slice
  by at most two.
- Held-out slices that leak into prompt tuning — the rotation and the
  split parity check are the control.