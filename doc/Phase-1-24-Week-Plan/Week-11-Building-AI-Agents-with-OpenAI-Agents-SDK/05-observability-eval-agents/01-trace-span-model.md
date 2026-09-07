# Trace & Span Model — Generation, Tool, Handoff, Guardrail Spans

**What you'll learn:** the four span types your SDK runs emit, what each
records, and the W10 schema mapping that makes traces a first-class
trajectory source.

## 1. The span catalog

| Span type | Fields you use | W10 equivalent |
|---|---|---|
| generation | model, usage (in/out tokens), output | fitter's token ledger |
| tool/function | name, args, result, duration, error | registry audit log |
| handoff | from_agent, to_agent | (new — W10 had one agent) |
| guardrail | name, triggered, output_info | gate/audit annotations |
| response | raw model response | raw_responses |

```python
def walk_spans(export: dict):
    for span in export.get("spans", []):
        yield span
        yield from walk_spans(span.get("children", []))
```

One trace per run; spans nest where the run nests (agent-as-tool →
nested spans). The walker above flattens them with depth preserved —
file 03's nested-cost warning depends on it.

## 2. Field extraction per span type

```python
def spans_to_row(export: dict) -> dict:
    row = {"steps": 0, "tokens_in": 0, "tokens_out": 0,
           "tools": [], "handoffs": [], "guardrail_trips": 0}
    for s in walk_spans(export):
        t = s.get("span_type") or s.get("type")
        if t == "generation" or t == "response":
            row["steps"] += 1
            u = s.get("model_usage") or {}
            row["tokens_in"] += sum(v.get("input_tokens", 0) for v in u.values())
            row["tokens_out"] += sum(v.get("output_tokens", 0) for v in u.values())
        elif t == "function" or t == "tool":
            row["tools"].append(s.get("name"))
        elif t == "handoff":
            row["handoffs"].append(s.get("to_agent"))
        elif "guardrail" in str(t):
            row["guardrail_trips"] += int(bool(s.get("triggered")))
    row["tools"] = sorted(set(row["tools"]))
    return row
```

The field names vary by SDK version — *pin the version* (your AGENT_CONFIG)
and pin this extractor to it; the unit test (file 04) is what notices a
span-shape change.

## 3. What traces add over your seams (and what they can't)

| Signal | Traces | Your seams |
|---|---|---|
| step/token counts | yes | yes |
| nested delegation cost | yes (spans) | partially |
| handoff graph | yes | no |
| fitter layer budgets | no | yes |
| error hint content | partial | yes (registry) |

The merge (file 03) takes the union: traces for topology and cost shape,
seams for budget/hint detail. Neither alone reproduces the W10 schema.

## 4. Trace hygiene (the firewall, again)

| Risk | Control |
|---|---|
| corpus-identifying metadata in traces | local-only export, or metadata allowlist |
| prompt content in span data | sanitize at the processor (W9 firewall) |
| API keys in trace metadata | separate tracing key (`set_tracing_export_api_key`) |
| unbounded trace storage | retention window + JSONL rotation |

Traces are model-visible data leaving your process — the W9 observation
firewall applies one layer up. The allowlist pattern: export only the
span types and fields the harness reads.

## Exercises

1. Run one task; flatten the trace with `walk_spans`; print the span
   catalog (type × count) — the run's shape, in one table.
2. Mapper hardening: pin the SDK version; write the unit test that fails
   when span fields rename (fixture export dict committed).
3. Hygiene drill: plant a system-prompt marker in a tool result; verify
   the sanitized export excludes it while the dashboard (or raw) trace
   shows the unfiltered path only locally.

## Pitfalls

- Extractors written against an unpinned SDK — span shapes move between
  versions; the fixture test is the seatbelt.
- Traces treated as the analysis store — they are transport; the parquet
  stays queryable.
- Hygiene skipped because "it's just local files" — the export path is
  exactly how things leak; the allowlist is the control.

## Resources

- SDK tracing reference (span types, processors) (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md)
  — the schema these spans feed.