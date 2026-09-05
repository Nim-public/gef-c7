# Exercises — Synthetic Data

Expanded set with worked approaches. The deliverable: expanded seeds
with provenance, a covered persona grid, a red-team battery, and the
four-gate validation report.

## 1. Seed expansion (from 01-seed-expansion)

**Task:** expand 10 seeds (5 log-derived, 5 failure-cluster) with the
variation axes; measure the axis spread; set the dedup threshold.

**Worked approach:** the axis spread is the diversity measure — count
which of the five axes each variant varies. The dedup threshold is set
where echoes die; both numbers go in the validation report.

**Pass criterion:** 10 seeds × 5–8 variants; axis spread ≥3 per variant;
the dedup threshold recorded.

## 2. The persona grid (from 02-persona-grids)

**Task:** design the 4×4 grid with voice constraints and weights;
generate to coverage ≥1.0 per cell; the voice drill (blind matching).

**Worked approach:** the grid designs coverage *before* generation —
the coverage ratio per cell drives the top-up loop. The voice drill is
the personas' validation: a blind reader matching ≥75% means the voice
constraints landed.

**Pass criterion:** all cells ≥1.0 (or explicitly deprioritized); the
voice drill ≥75%.

## 3. Red-team generation (from 03-adversarial-generation)

**Task:** generate 10 attacks per class; hand-review 30% for validity;
run the battery; the escape rate per class computed.

**Worked approach:** the escape rate is the red-team score — per
defense layer, per attack class. Every escape gets a fix-and-rerun; the
loop compounds.

**Pass criterion:** 5 classes × 10 attacks; 30% hand-reviewed; escape
rates per class recorded; fixes landed for every escape.

## 4. The validation battery (from 04-validation)

**Task:** run the four gates on one expansion batch + one red-team
batch; produce the validation report; the leakage drill with a planted
copy.

**Worked approach:** the planted-copy drill proves the leakage gate —
an 8-gram copy caught is the audit working. The distribution drill
validates the persona grid's weights against the output.

**Pass criterion:** 4/4 gates run; the planted leak caught; the
distribution comparison committed.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Expansion: axis spread + dedup threshold | expansion report | 3 |
| Persona grid: coverage + voice drill | grid report | 4 |
| Red-team: 5 classes, escape rates, fixes | red-team report | 4 |
| Validation: 4 gates + leakage drill | validation report | 4 |
| Pin note (synthetic data stack) | pin note | 2 |

**Pass bar:** 15/18 to proceed to file 03 (fine-tuning). The validation
battery (4-pointer) is the synthetic week's gate — unvalidated synthetic
data is noise with confidence.

## 6. The synthetic-data pin note (the batch manifest)

**Task:** extend `reports/sdk-versions.md` with the synthetic stack:
expansion prompt version, persona grid version, attack taxonomy version,
and the validation-battery command — one block.

**Worked approach:** the synthetic stack generates data at scale — the
pin note records which prompt/grid/taxonomy versions produced which
batches, and the validation command that gated them.

**Pass criterion:** note committed; the validation command green for the
current batches.

## 8. The synthetic-data review page

**Task:** write `reports/synthetic-review.md`: the expansion results
(seeds, variants, axis spread), the persona grid coverage, the red-team
escape rates, and the validation report — the synthetic week's evidence
page.

**Worked approach:** the page composes files 01–04 into one sheet: every
batch's four gates, the grid's coverage, and the red-team escape rates.
The reviewer question — "why trust data the model wrote?" — is answered
by the gates and the provenance.

**Pass criterion:** the page answers the trust question in one read;
every batch cites its validation report.

## Pitfalls recap

- Expansion beyond the diversity budget — echoes crowd out variety; the
  dedup threshold is the wall.
- Personas as stereotypes without voice constraints — the blind-matching
  drill is the personas' proof.
- Red-team data that skips the variation axes — the defenses overfit one
  attack flavor; weaponize the file 01 discipline.