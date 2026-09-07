# Trajectory Instrumentation — Logs, Tokens, Steps per Run

**What you'll learn:** the trajectory schema that turns every agent run
into a measurement row: steps, tokens, tools, outcome — captured at the
registry, not retro-fitted.

## 1. The trajectory schema (one row per run)

```python
TRAJECTORY = {
    "run_id": "r_20260905_0042",     # UTC-stamped, unique
    "query": "Which chart shows Q3 margin?",
    "steps": 3,                       # loop iterations
    "model_calls": 3,
    "tokens_in": 4120,                # per fitter's ledger, summed
    "tokens_out": 380,
    "tools": ["retrieve", "get_unit_text"],   # as a set
    "tool_calls": 2,
    "errors": 0,                      # ToolError + recovery count
    "outcome": "success",             # success | refused | failed | degraded
    "answer_chars": 412,
    "citations": ["u042"],
    "duration_ms": 2860,
    "trace": [...]                    # the full step list (file 02's entry)
}
```

Every field is derived from artifacts you already produce: the loop's
trace, the fitter's ledger, the registry's audit log. Instrumentation is
*assembly*, not new capture.

## 2. Capture at the seams, not in the loop

| Field | Source | Seam |
|---|---|---|
| steps, tools, tool_calls | loop's trace | return value of `run_react` |
| tokens_in/out | fitter per-step counts | summed at run end |
| errors | registry audit (`log_call`) | count of error entries |
| outcome | classifier over trace+answer | post-run function |
| duration | `time.perf_counter` at run level | the ledger wrapper (W9-04) |

```python
def outcome_of(trace: list[dict], answer: str, audit: dict | None) -> str:
    if looks_looped(trace) or "budget exhausted" in answer:
        return "degraded"
    if audit and not audit.get("ok", True):
        return "failed"
    if not extracted_citations(answer):
        return "refused"
    return "success"
```

The outcome classifier is four deterministic checks — no LLM judging here
(that is file 04's calibrated job). Keep the two layers apart: *outcomes*
are rule-based facts; *quality* is judged, calibrated, and labeled as
such.

## 3. The per-run store (episodic memory, from file 03)

```python
def log_trajectory(t: dict, out: Path = Path("data/agent/trajectories.parquet")):
    row = {k: v for k, v in t.items() if k != "trace"}
    df = pd.DataFrame([row])
    if out.exists():
        df = pd.concat([pd.read_parquet(out), df])
    df.to_parquet(out)                    # append-only; version in filename
```

The parquet is the episodic store (file 03's tier 3) *and* the eval
corpus: every metric table in file 02 is a groupby over this file. Store
traces separately (JSONL, one per run) — parquet for metrics, JSONL for
replay.

## 4. Instrumentation acceptance test

The harness is done when this passes on any run:

```python
def test_trajectory_complete(t: dict):
    required = {"run_id", "query", "steps", "tokens_in", "tools",
                "outcome", "trace"}
    assert required := required  # placeholder removed in real code
    assert required.issubset(t)  # every field present
    assert t["steps"] == len(t["trace"])
    assert t["outcome"] in {"success", "refused", "failed", "degraded"}
```

(Delete the stray placeholder line when copying — the two asserts are the
test.)

## Exercises

1. Wire the schema into your loop; run 5 trajectories; verify every field
   populates from existing seams (no new capture code).
2. Outcome-classifier drill: hand-label 10 runs, then compare the
   rule-based classifier — disagreements are classifier bugs, fix before
   judging.
3. Store drill: 25 runs in the parquet; produce one groupby (outcome ×
   mean steps) — file 02's first table, free.

## Pitfalls

- Instrumenting inside the model-call wrapper — capture at seams (return
  values, audit log) or refactors break the harness.
- Outcome labels assigned by the LLM silently — rules first, judge later,
  clearly separated.
- Traces stored in the parquet — schema churn; JSONL for traces, parquet
  for metrics, always.

## Resources

- Your fitter ledger (file 02) and registry audit — the two capture
  sources.
- [`../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md`](../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md)
  — the table/header conventions this store follows.
