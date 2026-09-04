# 01.4 — Measurement

> Subfolder index: [README.md](README.md) · Parent topic: [../01-advanced-chunking.md](../01-advanced-chunking.md)

---

## What you'll learn

- The sweep reporting format: the table that makes chunking decisions auditable
- The statistical discipline: n, variance, and the significance question
- The reporting template

## 1. The reporting template

```markdown
## Chunking sweep results — corpus v3, eval v1, 25 queries

| Config | Hit rate @5 | MRR | n_chunks | Ingest time |
|---|---|---|---|---|
| recursive-800/100 (baseline) | 0.68 | 0.52 | 890 | 45s |
| semantic (thr=0.5) | 0.71 | 0.55 | 720 | 3m |
| recursive + contextual headers | 0.79 | 0.61 | 890 | 46s |
| structural (md headers) | 0.76 | 0.58 | 610 | 52s |

**Winner:** recursive + contextual headers (+11 points hit rate, zero extra ingest cost)
**Rejected:** semantic chunking (small gain, 4× ingest cost)
```

## 2. The statistical discipline

| Check | Why |
|---|---|
| same eval set across configs | the only variable is the chunking |
| ≥20 queries | below 20, ±5-point swings are noise |
| report n | "85% on 5 cases" ≠ "85% on 50 cases" |
| held-out queries | eval queries not seen during tuning |
| the same embedder across configs | the only variable is the chunking |

The significance question: is +7 points on 25 queries meaningful? With a sign test on 25 paired results, 18/25 wins is significant at p<0.05. Below that, it's noise.

## 3. The reporting discipline

```python
def sweep_report(configs: list[dict], eval_results: list[dict]) -> str:
    lines = ["| Config | Hit@5 | MRR | Chunks |", "|---|---|---|---|"]
    for c, r in zip(configs, eval_results):
        marker = " **← selected**" if c.get("selected") else ""
        lines.append(f"| {c['name']} | {r['hit_rate']:.2f} | {r['mrr']:.2f} | {c['n_chunks']}{marker} |")
    return "\n".join(lines)
```

The report is generated from the data, not typed by hand — reproducible and consistent.

## Exercises

1. Run the sweep across all chunking configs you've implemented; produce the report.
2. The significance test: for the best-vs-baseline delta, compute the sign-test p-value; is it significant?
3. The reproducibility check: re-run the winning config; verify identical results (same seed, same embedder, same data).
4. The cost-benefit summary: for each config, the quality gain vs the ingest cost — the Pareto frontier.

## Pitfalls

- **Reporting only the winner** — the full table shows the trade-offs; the winner without the alternatives is cherry-picking
- **Sweeping with different embedders** — the embedder must be constant across chunking configs (W5-02's confound rule)
- **Forgetting the reproducibility info** — embedder revision, corpus version, eval version — all pinned in the report
- **The winner never re-validated** — the corpus changes, the winner may not; re-sweep quarterly

## Resources

- W4-05 (the harness), W16-01 (versioning), W5-01 (the techniques) — composed here
- E10-01 (benchmark literacy) — the same reporting discipline at research scale
