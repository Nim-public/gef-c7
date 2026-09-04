# 05.3 — Eval & Reporting

> Subfolder index: [README.md](README.md) · Parent: [../05-capstone-task-search-engine.md](../05-capstone-task-search-engine.md)

---

## What you'll learn

- The 25-query eval set: construction, labeling, and maintenance
- The metrics table: the before/after that drives decisions
- The failure taxonomy: classifying what went wrong and why

## 1. The eval set construction

| Kind | Count | Source |
|---|---|---|
| paraphrase questions | 10 | rephrase corpus facts in natural language |
| identifier queries | 5 | exact SKUs, error codes, names |
| multi-constraint | 5 | two+ conditions that must both match |
| unanswerable | 5 | no matching content in the corpus |

The mix ensures the eval tests all query classes (W4-04's probe taxonomy). The labels: hand-verified relevant chunk ids per query — the human labeling is the ground truth that all automated metrics reference.

## 2. The metrics table

| System | Hit rate @5 | MRR | Precision @5 |
|---|---|---|---|
| BM25 only | | | |
| Semantic only | | | |
| Hybrid (RRF) | | | |
| Hybrid + metadata filter | | | |

Plus: p50/p95 latency, index size, ingest time. The table is the search engine's report card — every future change re-runs it.

## 3. The failure taxonomy

| Class | Symptom | Fix |
|---|---|---|
| **missing content** | the answer isn't in the corpus | add the document |
| **chunking loss** | the answer spans two chunks | adjust size/overlap/strategy |
| **embedding miss** | right doc, wrong embedding match | different embedder or hybrid arm |
| **keyword miss** | paraphrase query, exact-match corpus | the semantic arm covers it |
| **threshold too high** | good matches below the threshold | recalibrate (file 02 §3) |
| **filter too strict** | correct doc excluded by metadata | review the filter rules |

Each failure maps to a specific pipeline stage — the diagnosis is the fix. The failure classes come from the W4-04 probe suite; the eval set surfaces which classes dominate.

## Exercises

1. Build the 25-query eval set; hand-verify the labels; produce the labeling notes.
2. Run all systems; produce the metrics table; identify the winning system and the margin.
3. The failure deep-dive: take the 5 worst queries; trace each through the pipeline to find the failure class; write one fix per class.
4. The threshold recalibration: after adding 20 new documents, re-calibrate the threshold — does the old threshold still work?
5. The growth projection: at current corpus growth rate, when does the index need an upgrade (IVF → IVF-PQ)? (W4-03's scaling curve.)

## Pitfalls

- **Labels from the system's own output** — circular evaluation; label from the corpus, not from the search results
- **Metrics without baselines** — "0.72 hit rate" means nothing without the comparison; always report the baseline alongside
- **The eval set stale** — new document types appear; the eval set must cover them or the metrics lie
- **Fixes without re-measurement** — every change re-runs the harness; unmeasured fixes are hypotheses (W3-01's A/B rule)
- **The report without the failure analysis** — the numbers say what; the analysis says why — both are needed

## Resources

- W4-04 (the harness), W4-03 (the indexes), W4-02 (the chunking) — the components evaluated
- W5-03 (the reranking upgrade), W5-05 (the Ragas extension) — the next steps
- W16-01 (the versioning discipline) — the eval set's lifecycle
