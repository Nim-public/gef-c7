# Exercises — Practice: Multimodal RAG over Your Data

Stretch tasks and the self-review rubric for the week's capstone-shaped
deliverable. The rubric grades committed artifacts only.

## 1. Corpus prep certification (stretch)

**Task:** the prep audit produces a one-page `reports/corpus-certification.md`:
unit counts per class, sidecar coverage, caption version, crop provenance
rate, gate status — the artifact that says "this corpus is served-ready".

**Worked approach:** the certification is generated (never hand-written)
and re-runs in <2 min; anything slower means the prep pipeline needs a
cache, not a longer deadline.

**Pass criterion:** certification regenerates identically on a clean clone
after ingest.

## 2. Store utility proof (stretch)

**Task:** the fields store must pay rent: 3 structured-fact queries
answered *only* via fields; if any fails, either fix extraction or demote
the store to filters-only — decide with numbers.

**Worked approach:** the rent test is the store's reason to exist; a store
that only filters is still useful but must be documented as such in the
architecture section.

**Pass criterion:** 3/3 or documented demotion, in the README.

## 3. Safety battery expansion (stretch)

**Task:** add 5 battery rows: two new injection phrasings, one poisoned-
unit case, one quota-exhaustion case, one empty-corpus case; all green in
CI.

**Worked approach:** new rows come from *imagined attackers*, not from
your own query list — phrasings you would not type yourself make the
battery stronger than the demo.

**Pass criterion:** 5 new rows green; battery runtime still <30 s
(route-tagged subset for fast CI).

## 4. Eval tables as regression gate (stretch)

**Task:** wire `eval_multimodal.py` into CI with the three thresholds
(R@10 ≥ baseline −0.05, faithfulness ≥0.8, p95 ≤ baseline ×1.2); verify
the gate catches an injected regression (e.g., nprobe=1).

**Worked approach:** the injected regression is the proof the gate works —
same mutation-test discipline as the Week-07/08 suites.

**Pass criterion:** gate red on injection, green on restore; baselines
untouched by hand.

## 5. Self-review rubric (grade before the week ends)

| Criterion | Evidence | Points |
|---|---|---|
| Corpus certification, gates green | reports/corpus-certification.md | 3 |
| Three stores + invariant test | tests/ + table schema | 3 |
| Battery: routes + injection + quota | battery file + CI log | 4 |
| Three eval tables committed, cited | reports/eval-tables.md | 3 |
| Tool contract v1 (schema + errors + budget) | doc/capstone/tool-contract.md | 3 |

**Pass bar:** 13/16 to enter Week 10. The battery (4-pointer) is the
week's real deliverable — it is the safety net the agent week will hang
its tools on.

## 6. The handoff page for Week 10

**Task:** write `doc/capstone/agent-handoff.md` (one page): the tool
contract summary, the routing table, the quota, the degradation ladder,
and the three eval tables' headline numbers — everything a Week-10 agent
builder needs without opening this week's folders.

**Worked approach:** every line cites its source artifact; the page is
generated where possible (tables) and hand-written only for the contract
summary. The Week-10 session starts by reading this page — make it the
single entry point.

**Pass criterion:** a teammate answers "what tools exist, what do they
return, when do they degrade?" from the page alone.

## 7. The week's retrospective note

**Task:** append to `doc/capstone/retrospective.md`: three things the
week's numbers changed about your plan (e.g., sidecar work prioritized,
quota lowered, store demoted), each citing the artifact that forced the
change.

**Worked approach:** the retrospective is the memo's living journal —
numbers in, plan changes out. Three entries with citations beats a page
of impressions.

**Pass criterion:** three entries, each with a `reports/` citation and a
one-line plan consequence.

## Pitfalls recap

- Certification hand-written — regenerate or it lies within a week.
- Battery rows from demo queries — attackers do not read your demo script.
- Rubric evidence missing from `git status` — if it is not committed, it
  does not exist.
