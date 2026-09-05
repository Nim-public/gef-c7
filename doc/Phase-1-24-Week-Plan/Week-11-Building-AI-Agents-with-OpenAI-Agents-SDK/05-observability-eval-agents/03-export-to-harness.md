# Export to Harness — Merged W10-04 + Trace Rows

**What you'll learn:** the merged trajectory schema: your W10 capture
(seams) joined with SDK traces (spans) into one store the scorecards and
regression gates read — with a parity test that keeps the union honest.

## 1. The merged schema

| Field | Source | Notes |
|---|---|---|
| run_id, query, outcome | your seams | unchanged |
| steps, tokens_in/out | spans (primary) | fitter ledger = cross-check |
| tools, handoffs | spans | handoffs are new |
| errors, hints | registry audit (your seams) | hint text lives here only |
| budgets | fitter ledger (your seams) | per-layer, span-blind |
| guardrail_trips | spans | + audit detail |
| span_count, nested_depth | spans | the nested-cost numbers |
| versions (config, rubric, hints) | AGENT_CONFIG | stamp |

```python
def merge_row(seam_row: dict, span_row: dict) -> dict:
    row = {**seam_row}
    for k in ("steps", "tokens_in", "tokens_out", "tools", "handoffs",
              "guardrail_trips"):
        row[k] = span_row.get(k, seam_row.get(k))
    row["token_parity"] = abs(row["tokens_in"] - seam_row.get("tokens_in", 0)) \
                          <= 0.05 * max(seam_row.get("tokens_in", 1), 1)
    return row
```

The `token_parity` flag is the parity test's per-row witness: two capture
paths must agree within 5%, or one of them is lying about the run.

## 2. The parity test (the merge's acceptance gate)

```python
def test_capture_parity(seam_rows, span_rows):
    for s, t in zip(seam_rows, span_rows):
        assert s["run_id"] == t["run_id"]
        assert s["steps"] == t["steps"], f"step mismatch {s['run_id']}"
        assert abs(s["tokens_in"] - t["tokens_in"]) <= 0.05 * max(s["tokens_in"], 1)
        assert set(t["tools"]) <= set(s["tools"]) | {"handoff-only"}
```

The tolerance exists because span usage accounting and your fitter count
slightly differently (system prompts, retries). A *systematic* gap is a
bug (double-counting, missed spans); a bounded jitter is expected — the
test distinguishes them by sign and consistency.

## 3. What the merged store enables

| Consumer | Uses |
|---|---|
| W10 scorecards | unchanged — same schema |
| topology health (anti-patterns) | handoffs + nested depth (new fields) |
| router tax | triage-turn tokens (now visible per run) |
| nightly judge | runs from either capture path |
| regression gate (file 04) | the merged rows |

The merge is what makes Week 11's features *measurable in the old
harness* — the scorecards never learned about handoffs; the store did.

## 4. The one-command harness

```bash
py scripts/agent_harness.py --from-traces data/traces/ --merge data/agent/trajectories.parquet
```

```text
# harness output (v2)
| metric            | value |
|---|---|
| runs              | 30    |
| success_rate      | 0.80  |
| p50 steps         | 3     |
| handoff runs      | 11    |
| token_parity      | 30/30 |
| guardrail trips   | 2     |
```

## Exercises

1. Implement `spans_to_row` + `merge_row`; run the parity test over 30
   runs; document the systematic gaps you find (and their sign).
2. Field-addition drill: add `nested_depth` to the schema; regenerate the
   scorecard; confirm old consumers ignore the new field gracefully.
3. Source-of-truth drill: for tokens, declare spans primary and the
   fitter secondary in the metric dictionary; add a dictionary row for
   `token_parity` itself.

## Pitfalls

- Two stores growing independently — the merge *is* the store; the parity
  test is what keeps it one store.
- Parity tolerance set to 0% — span accounting legitimately differs by a
  few tokens; 5% is the honest bound.
- Schema additions that break old consumers — additive-only; the drill
  proves it.

## Resources

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md)
  — the schema being extended.
- Your metric dictionary (W10-04 exercises) — the source-of-truth
  declarations.