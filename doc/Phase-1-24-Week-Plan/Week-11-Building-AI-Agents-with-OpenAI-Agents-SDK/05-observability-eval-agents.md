# 05 — Observability & Evaluation for Agents

> Week 11 index: [README.md](README.md)

**Session topics:** *Tracing and debugging with built-in SDK tools (S1). Environment/observability aspects threaded through the SDK sessions.*

---

## What you'll learn

- The SDK trace model: traces, spans, and what each span records
- Debugging a failed run from its trace (the replay workflow)
- Exporting traces for your own eval harness (joining SDK spans with W10-04's JSONL)
- Trajectory regression suites: pinning good and bad runs as tests

## 1. The trace model

Every `Runner.run` produces a **trace** containing hierarchical **spans**:

| Span type | Records |
|---|---|
| `Agent` span | which agent ran, its instructions hash |
| generation span | model, input tokens, output tokens, latency, raw request/response |
| tool/function span | tool name, args, result, error |
| handoff span | from-agent → to-agent |
| guardrail span | verdict + tripwire flag |

Reading order when debugging: find the *last* generation span before a failure → was the observation malformed? → walk back to the tool span that produced it → check its args. Nine times out of ten the bug is a **bad tool arg** or a **mis-formatted observation** (W10-05), and the trace shows both.

## 2. The replay workflow (debugging a failed run)

```python
from agents import Agent, Runner, gen_trace_id

with agents.trace("debug: triage fail #17"):
    result = Runner.run_sync(triage_agent, failing_input)
print(f"https://platform.openai.com/traces/{gen_trace_id()}")
```

1. Open the trace (dashboard, or your exported file)
2. Locate the wrong tool call → inspect the *args* the model produced
3. Ask: bad description? missing schema constraint? polluted observation? (W10-02/05 categories)
4. Fix → **re-run the same input** with the same seed/settings → compare traces side by side
5. When fixed, *keep the failing case* in the regression suite (§4)

The discipline from W10-04 carries over: **one trajectory = one replayable unit**. The trace makes it replayable; your suite makes it mandatory to stay fixed.

## 3. Exporting traces into your harness

Traces are on by default (API key required). For programmatic access:

```python
from agents.tracing import Trace, custom_trace_processing
import json

def export_trace(trace) -> dict:
    return {
        "trace_id": trace.trace_id,
        "spans": [
            {"type": s.span_data.__class__.__name__,
             "name": getattr(s, "name", None),
             "started": str(s.started_at), "ended": str(s.ended_at)}
            for s in trace.spans
        ],
    }
```

(Depending on SDK version you may use a trace processor callback — check the tracing guide — the goal is identical: spans land in *your* JSONL next to the W10-04 metrics.)

Joining with your own logs gives the full eval row:

```python
row = {**w10_metrics,            # success, steps, tokens p95, tool errors (W10-04)
       **export_trace(trace),    # spans for the same run
       "task_id": case["id"]}
```

That merged row is what W15's reliability work and W16's capstone eval consume.

## 4. Trajectory regression suites

Pin trajectories as tests (the W10-04 exercise, now with trace assertions):

```python
# eval/agent_cases.jsonl → pytest
CASES = load_cases("eval/agent_cases.jsonl")   # {id, goal, expected_tools, answer_shape}

@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_trajectory(case):
    with agents.trace(f"regression:{case['id']}"):
        result = Runner.run_sync(triage_agent, case["goal"])
    used = {s.name for s in spans(result) if s.type == "tool"}
    assert used == set(case["expected_tools"]), f"tool drift on {case['id']}"
    assert shape_ok(result.final_output, case["answer_shape"])
```

What to assert, in increasing strictness:

1. **Termination** — run completes under `max_turns`
2. **Tool family** — right tools used (order optional)
3. **Answer shape** — schema/citations present (W6-03/W11-02 `output_type`)
4. **Content anchors** — key facts present (don't over-pin wording)
5. **Cost/latency ceilings** — tokens and wall-time under budget (W10-04's three dimensions, as assertions)

## 5. Observability beyond the SDK (the vocabulary for W15)

| Concept | What it is | SDK analog |
|---|---|---|
| Trace | one full run | `agents.trace` |
| Span | one step/event | generation/tool/handoff spans |
| Metrics | aggregates over traces | your JSONL → p50/p95 tables |
| Evals | scored traces against expectations | §4's suite + W5-05 judge |
| Dashboard | UI over all of the above | platform.openai.com/traces / LangSmith / Langfuse |

The W15 reliability week scales this exact stack (limits, retries, monitoring) — nothing conceptually new arrives then; it's this file under load.

## Exercises

1. Run 5 tasks with tracing on; open the dashboard traces. Identify per trace: model span, tool span, handoff span — and the token counts per generation.
2. Debug by replay: plant a bug (tool returns swapped columns, W6-03 style); find the failing run from its trace *alone*; fix; show side-by-side traces.
3. Export spans → JSONL → merge with W10-04 metrics; produce one merged eval row per run.
4. Build the 5-level regression suite (§4) over your 10 W10 cases; report which level catches a deliberate regression (swap two tool descriptions and rerun).
5. Budget assertions: add tokens-per-run and wall-time ceilings from your W10-04 p95s (×1.5 headroom); find the case that violates them first.

## Pitfalls

- **Traces read as logs, not spans** — the hierarchy (agent → generation → tool) *is* the debugging tool; flat-scrolling misses causality
- **Fixing without pinning** — a fix without a regression case re-breaks within weeks (§4 exists to prevent exactly this)
- **Over-pinning wording** — asserting exact model phrasings makes suites flaky; assert shape/anchors/ceilings
- **Tracing disabled by default in prod configs** — invisible agents can't be debugged; if you must disable (PII/export policy), export locally first (W10-04's logging duty)
- **One eval metric to rule them all** — success rate hides cost/latency regressions; keep the three dimensions separate (W10-04)

## Resources

- [Tracing guide](https://openai.github.io/openai-agents-python/tracing/) — trace/span model, processors, sensitive-data handling
- [Results & run detail](https://openai.github.io/openai-agents-python/results/) — `RunResult`, `RunResultStreaming` introspection
- W10-04/05 — your instrumentation, now joined with SDK traces
- LangSmith / Langfuse docs — the hosted dashboards this vocabulary targets in W15
