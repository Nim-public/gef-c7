# Exercises — Multimodal RAG Patterns

Expanded set with worked approaches. Everything builds on the harness and
queries you already own; the deliverable is the routing table with gold
labels.

## 1. Contract audit (from 01-traditional-rag-review)

**Task:** write your capstone's five-clause contract with amendments
marked; for each amendment, name the artifact (file + test) that verifies
it. Two amendments maximum for v1.

**Worked approach:** the audit table is three columns (clause, amendment,
verification). More than two amendments for v1 is the scope-creep
signature — defer the rest to the memo's triggers.

**Pass criterion:** the table committed to the capstone README's
architecture section.

## 2. P1 vs P2 vs merged (from 02, 03)

**Task:** on your 25-query set, measure R@10 for: (a) P1 captions-only,
(b) P1 OCR-merged, (c) P2 unified space. Report per query-class means
(natural vs charts vs exact-term).

**Worked approach:** the interesting cell is (b) on chart queries —
expect +10–20 R@10 points over (a). The domain split is the finding that
feeds the router's gold labels.

**Pass criterion:** 3×3 table (pattern × query class) committed to
`reports/pattern-eval.md`.

## 3. P3 quota simulation (from 04)

**Task:** instrument the router with a 10% P3 quota; replay 100 synthetic
queries with your class distribution; report P3 usage, degradation flags,
and the token cost of the P3 answers issued.

**Worked approach:** token cost = images×576 + snippet + answer tokens
(file 04's table); the simulation turns the quota from policy into a
measured cost line for the memo.

**Pass criterion:** usage ≈ quota; every degraded answer flagged; cost
line in the memo.

## 4. Router holdout (from 05)

**Task:** write 10 *new* phrasings for your query classes (not in the gold
set); measure router accuracy on them; then compute accuracy on the gold
set — the gap is your memorization score.

**Worked approach:** if holdout accuracy drops >10 points, the regexes are
overfit — replace the most demo-specific patterns with class-generic ones
and re-measure.

**Pass criterion:** both accuracies reported; the gap ≤10 points.

## 5. Capstone: the architecture section (from all files)

**Task:** write the capstone README's "Architecture" section: the contract,
the two v1 amendments, the routing table (with gold-label sources), the P3
quota, and the degradation ladder — one page, every number cited.

**Worked approach:** this section is what the Week-10 agent and your
evaluators read first; it must stand alone without the week's files. Every
cited number links to a `reports/` artifact.

**Pass criterion:** the section passes the "teammate test": they can name
your retrieve path, quota policy, and fallback behavior from it alone.

## Pitfalls recap

- Pattern comparisons on fewer than 5 queries per class — the class means
  are noise; 25+ queries total is the floor.
- Quota simulation without token accounting — the quota's purpose *is* the
  cost bound; measure it.
- Architecture sections that cite no artifact — regenerate the numbers or
  delete the claims.
