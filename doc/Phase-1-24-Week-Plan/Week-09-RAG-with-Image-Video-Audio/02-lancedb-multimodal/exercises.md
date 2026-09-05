# Exercises — LanceDB for Multimodal AI

Expanded set with worked approaches. Migrate the cataloger's store, then
prove the migration with sweeps and a hybrid eval.

## 1. Migration with proof (from 01-multi-vector-tables)

**Task:** migrate the cataloger (matrix + SQLite) to one LanceDB table;
verify on 10 queries that per-column vector search returns *identical*
rankings to the brute-force matrix path (cosine, same k).

**Worked approach:** identical ranks are the acceptance bar — cosine over
float32 is deterministic, so any rank difference is a normalization or
schema bug (object dtype from None-mixed columns is the usual culprit;
check `table.schema`).

**Pass criterion:** 10/10 identical top-5 lists; schema shows
fixed-size-list float32.

## 2. IVF-PQ at your scale, honestly (from 02-ivf-pq)

**Task:** build IVF-PQ on the units table (nlist=32, m=48 for 384-d);
sweep per file 03; then answer: does the index beat flat at *your* n?
Write the verdict in one sentence.

**Worked approach:** at n ≤ 10k, flat search is ~1–3 ms — the index must
beat that *at acceptable recall* (R@10 ≥ 0.95). If it does not (likely),
your verdict: "flat in production, IVF-PQ skills banked for scale" — that
is a correct engineering answer, not a failure.

**Pass criterion:** sweep table + verdict sentence in
`reports/lancedb-sweep.md`.

## 3. GT regression fixture (from 03)

**Task:** commit the flat-GT fixture (50 seeded queries + their exact
top-10) as a parquet; add a test that the *current* index configuration
reproduces R@10 ≥ threshold against it.

**Worked approach:** the fixture pins corpus version (manifest hash in the
filename); the test is your index's regression gate — when the corpus or
index config changes, GT regenerates and the old fixture retires.

**Pass criterion:** test green at the chosen cell; red when you set
nprobe=1 (proving the gate works).

## 4. Hybrid search eval (from 04)

**Task:** build the 5+5 query set (FTS-wins vs vector-wins); implement the
router (regex for exact tokens → FTS-lean, else 50/50 RRF); report R@10
for vector-only, FTS-only, and routed-fused.

**Worked approach:** the router's win condition is *no loss* on either
query class — matched on paraphrases, matched on codes. If fusion loses on
the vector-friendly class, rebalance (k, list lengths) before blaming RRF.

**Pass criterion:** the 3-row R@10 table; router ≥ max(single) on both
classes.

## 5. Capstone: the store decision (from all files)

**Task:** add the storage row to the encoder decision memo: engine
(LanceDB), index config (flat vs IVF-PQ + numbers), hybrid router policy,
and the migration status from exercise 1.

**Worked approach:** cite the sweep report and the migration proof; the
row is one line per decision with its deciding number, same discipline as
Week 08's memo.

**Pass criterion:** memo row cites `reports/lancedb-sweep.md` and the
migration test; no uncited claims.

## Pitfalls recap

- Migrations verified by "it ran" instead of identical-rank checks — equality is the proof, counts are not.
- Sweeps with unseeded queries — the fixture discipline from file 03 applies to every table you will ever show.
- Hybrid evals against vector-only GT — relabel or hand-label; the metric's meaning changed.
