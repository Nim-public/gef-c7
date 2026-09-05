# Replay Debugging — Failed-Run Root Cause Workflow

**What you'll learn:** the debug loop for a failed agent run: bisect the
trace by span, replay the failing call in isolation, and fix at the
layer the evidence names — descriptions, budget, guardrail, or data.

## 1. The workflow, four questions

```text
1. WHERE did it stop?   → last successful span before the failure
2. WHAT did the model see? → that span's inputs (messages, tool results)
3. WHAT did it try?      → the failing span's args and error
4. WHICH layer owns it?  → description | budget | guardrail | data
```

```python
def bisect_failure(export: dict) -> dict:
    spans = list(walk_spans(export))
    last_ok = None
    for s in spans:
        if s.get("error"):
            return {"failing_span": s, "context": last_ok}
        if s.get("type") in ("generation", "function"):
            last_ok = s
    return {"verdict": "no-error-in-trace; check outcome classifier"}
```

The bisection is mechanical; the *reading* is the skill — each failure
layer has a signature:

| Signature | Layer | Fix locus |
|---|---|---|
| tool args off-schema, description vague | description | file 02 A/B |
| budget exhausted mid-retrieval | budget | fitter/trim rules |
| guardrail tripwire on good output | guardrail too strict | rubric/threshold |
| 0 hits for a known-present fact | data | indexing/sidecars (W9) |

## 2. Replay: the failing call, isolated

```python
def replay_span(span: dict, agent) -> None:
    """Re-run just the failing generation with the same inputs."""
    msgs = span["input_messages"]              # from the export
    r = Runner.run_sync(agent, msgs)           # temperature 0 for determinism
    print(r.final_output, r.new_items)
```

Replay beats re-run: the *same inputs* through the failing step, nothing
else. Temperature 0 first (determinism check: does it fail identically?),
then temperature variation to see if the failure is stochastic — which
splits failures into "logic bug" vs "sampling risk" (the latter needs a
prompt/eval fix, not a code fix).

## 3. The failure taxonomy, from your own runs

| Class | Signature | Owner |
|---|---|---|
| tool misuse | wrong arg shapes/values | description (file 02) |
| budget death | MaxTurns/handler fired | fitter or task design |
| guardrail trip | payload shows the reason | threshold or model |
| data miss | 0 hits, unit exists | ingest/sidecars (W9) |
| model drift | Tier-2 flip on unchanged code | pin/rerun baseline |

Every failure in your store gets one of these labels — the label column
in the trajectory parquet is how debugging becomes a dataset (the drift
chart from file 03's nightly report).

## 4. The post-mortem artifact

```markdown
# Failure r_20260905_0042 — post-mortem
- Symptom: task 8 answered without citations
- Bisect: generation span 3 (answerer), tool span prior returned 0 hits
- Replay: same input, same miss; temperature-independent
- Layer: data — the chart's OCR sidecar was empty (V8 miss, W9)
- Fix: re-OCR that unit; add battery case: "chart query on u047"
- Regression: outcome classifier now flags 0-hit answers as `refused`
```

One paragraph, four layers named, one test added. The post-mortem is the
debugging loop's *output* — without it, the same failure returns next
week wearing new tokens.

## Exercises

1. Plant a failure (bad description → tool misuse); run the workflow;
   produce the post-mortem in the §4 format.
2. Replay determinism drill: replay the failing span 5× at temperature 0
   and 5× at 0.7; classify the failure as deterministic vs sampling.
3. Taxonomy drill: label all failed runs in your store with the §2
   taxonomy; the distribution tells you where Week 12's effort goes.

## Pitfalls

- Debugging at the answer layer first — the trace bisection is the order;
  answers hide the mechanism.
- Post-mortems without the added test — the same failure *will* recur;
  the test is the memory.
- Replay with changed inputs ("let me just tweak the query") — that is a
  new run, not a replay; isolate the original inputs.

## Resources

- Your trace store + W10 harness; SDK replay primitives (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/04-failure-phrasing.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/04-failure-phrasing.md)
  — the layer the fix usually lands in.