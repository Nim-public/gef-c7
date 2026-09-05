# Exercises — Capstone Task: The Data Agent

Expanded set with worked approaches. The deliverable: the assembled
agent, 15 gold-labeled cases scored, verification proven by mutation,
and the final framework memo.

## 1. Assembly + smoke (from 01-agno-assembly)

**Task:** assemble the agent from W12 components; run the smoke test
(canned + real); verify config stamps on every trajectory row.

**Worked approach:** the assembly is composition of tested units — the
smoke test is the W10-06 pattern, third application. The config stamp
carries the component versions, making every later comparison
attributable.

**Pass criterion:** smoke green both modes; stamps on 100% of rows.

## 2. The 15-case run (from 02-eval-cases)

**Task:** write the gold answers from your data; run all 15 cases × 3;
score by the case-type rules (exact numbers, citations, refusals);
commit as the baseline.

**Worked approach:** gold first, runs second — the anti-retro-labeling
rule. The scoring parser (numbers with separators/currency) is itself
tested; a scoring bug is a false eval.

**Pass criterion:** 15×3 runs; the score table committed; the baseline
gate (W11 file 05-04) extended with the numeric-exact metric.

## 3. Verification mutation (from 03-verification-nodes)

**Task:** the independence drill — make verify re-use the same query;
show drift goes undetected; restore independence; show detection. Then
the value drill: disable verify; count numeric failures across 6–10.

**Worked approach:** the independence proof by *absence* is the
verification node's characterization test — it shows exactly what the
node contributes.

**Pass criterion:** both drills produce numbers; the verify node's
value quantified in the comparison report.

## 4. The final framework memo (from 04-comparison-vs-w11)

**Task:** write the framework decision into the boundary memo: the
mechanism per path (SDK/Agno), the shared system list, the ported-ideas
ledger, and the revisit triggers.

**Worked approach:** the memo is the fourth comparison's verdict —
citing the table, the parity numbers, and the verification value. It is
the capstone's standing architecture record.

**Pass criterion:** memo committed; every claim cites an artifact.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Assembly + smoke + stamps | assembly tests | 3 |
| 15 cases, gold verified, scored | eval table | 4 |
| Verification mutation drill | comparison report | 4 |
| Framework memo final | boundary memo | 4 |
| Numeric exact-match in the gate | gate config | 2 |

**Pass bar:** 14/17 to proceed to file 06 (checkpointing). The eval
table (4-pointer) is the capstone's quality record — the last week's
gates hang on it.

## 7. The 15-case scoring walkthrough (the reviewer's page)

**Task:** write `reports/eval-walkthrough.md`: one case per scoring type
(numeric, citation, refusal, ambiguous) walked end-to-end — the query,
the agent's artifacts, the score, and why. The page is how the rubric
becomes legible.

**Worked approach:** the walkthrough is the eval's documentation-by-
example: one numeric case showing exact-match parsing, one citation
case showing unit resolution, one refusal case showing the honest
phrase family. A reviewer who reads it can score case 16 themselves.

**Pass criterion:** four walked cases, one per scoring type; every
scoring rule from §2 appears in at least one walkthrough.

## 6. The data-agent pin note

**Task:** extend `reports/sdk-versions.md` with the data-agent stack:
assembly component versions (from the pin table), the 15-case set
version, the scoring parser version, and the eval-rerun command.

**Worked approach:** the data agent is the capstone's quality record —
the pin note ties the eval table to the exact component versions it was
scored against.

**Pass criterion:** note committed; the eval rerun reproduces the score
table.

## Pitfalls recap

- Gold labels from model outputs — facts from data, always.
- Verification without independence — the mutation drill proves the
  property exists.
- Framework memos without artifact citations — the verdict is the
  tables, not the adjectives.