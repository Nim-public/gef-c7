# Tracing — Spans, Dashboards, Local Export

**What you'll learn:** the SDK's built-in tracing: the trace/span model
(generation, tool, handoff, guardrail spans), the dashboard, and the
local export path that feeds your trajectory store — W10's harness, now
free.

## 1. The trace model

```text
trace (one run, workflow_name="gef-c7-rag")
├─ span: agent "RAG agent"            (generation)
│    └─ span: tool "retrieve"          (args, result, timing)
├─ span: handoff → "answerer"         (if any)
│    └─ span: generation               (tokens, model)
└─ span: guardrail "citation_check"   (pass/tripwire)
```

| Span type | Captures | Replaces your W10... |
|---|---|---|
| generation | model call, tokens | fitter's token ledger |
| tool | name, args, result, duration | registry audit log |
| handoff | from → to agent | (new — W10 had one agent) |
| guardrail | check name, outcome | gate/audit annotations |

One run = one trace = one row in your trajectory store — the W10 schema
maps field-for-field onto span data.

## 2. Where traces go

| Destination | Setup | Use |
|---|---|---|
| OpenAI dashboard | default (needs key) | interactive inspection |
| external (OTel) | processor package | your observability stack |
| local export | `trace.export()` / custom processor | your parquet + JSONL |

```python
from agents.tracing import Trace, custom_trace_processors
# local processor: append every trace's export() dict to a JSONL
def to_jsonl(trace):
    d = trace.export()
    if d:
        TRACES_JSONL.write_text(
            json.dumps(d) + "\n", encoding="utf-8")
```

For capstone privacy: tracing to the dashboard needs an API key you may
not want on your corpus metadata — `set_tracing_export_api_key("sk-...")`
separates the *tracing* key from the *model* key, and a custom processor
keeps everything local.

## 3. Traces → trajectory rows (the harness merge)

```python
def trace_to_trajectory(trace_export: dict) -> dict:
    steps = tokens_in = tokens_out = 0
    tools = set()
    for span in walk_spans(trace_export):
        if span["type"] == "generation":
            steps += 1
            tokens_in += span_usage(span, "input")
            tokens_out += span_usage(span, "output")
        elif span["type"] == "tool":
            tools.add(span["name"])
    return {"steps": steps, "tokens_in": tokens_in,
            "tokens_out": tokens_out, "tools": sorted(tools)}
```

The W10 schema is unchanged; its *capture* moves from seams you built to
spans the SDK gives you. The fitter's ledger and the registry audit
remain the sources of truth for budgets and hints — tracing is the
second, free copy.

## 4. Debugging with spans (the replay workflow)

Failed-run root cause, in span order:

1. **Find the turn** — the last generation span before failure.
2. **Read the tool span** — args the model chose vs your schema.
3. **Check guardrail spans** — tripwire name and reason.
4. **Token ledger** — which layer ate the budget (fitter cross-check).

The dashboard makes this interactive; local export makes it greppable;
your week-10 replay discipline (predict-actual diffs) applies unchanged
to spans.

## Exercises

1. Run one task; export the trace locally; reconstruct the W10 trajectory
   dict from spans; diff against your hand-built trace — field-for-field.
2. Privacy drill: verify no prompt content or absolute paths appear in the
   exported trace (the W9 firewall, now at the trace layer).
3. Dashboard vs local: run one failure with both; time the root-cause
   hunt each way; record the tradeoff in `reports/tracing.md`.

## Pitfalls

- Traces as the *only* store — they are transport-shaped, not query-shaped;
  your parquet stays the analysis surface.
- Exporting traces with corpus-identifying metadata to a public dashboard —
  same firewall as observations; sanitize or keep local.
- Double-counting tokens (span ledger + fitter ledger) — pick one source
  of truth per metric and name it in the dictionary.

## Resources

- SDK tracing guide + `Trace.export` reference (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md)
  — the schema being merged.
