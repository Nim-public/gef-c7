# 04 — OpenTelemetry Observability

> E8 index: [README.md](README.md)

**Core topics:** *OTel GenAI conventions, dashboards, and the alert set that matters.*

---

## What you will be able to do after this week

- [ ] Emit OTel GenAI-conformant traces for agents, tools, and retrievers
- [ ] Build the dashboard: the metrics that matter, per feature
- [ ] Configure the alert set (and its tuning discipline from W15-02)
- [ ] Unify vendor traces (LangSmith) with OTel into one observability story

## 1. Why OTel (the vocabulary argument)

LangSmith (W15-02), the Agents SDK traces (W11-05), and Agno's logs each speak their own dialect. **OpenTelemetry's GenAI semantic conventions** define the standard span model — one instrumentation, any backend (Jaeger, Grafana Tempo, Datadog, Langfuse):

| Span attribute (GenAI convention) | Meaning |
|---|---|
| `gen_ai.system` | provider ("openai") |
| `gen_ai.request.model` | model id |
| `gen_ai.usage.input_tokens` / `output_tokens` | token accounting (E8-03's ledger source) |
| `gen_ai.prompt.0.content` / `gen_ai.completion.0.content` | messages (with redaction, W15-02) |
| tool spans | `tool.name`, `tool.arguments`, `tool.result` |

## 2. Instrumenting your stack

```python
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider(resource=Resource.create({"service.name": "capstone-agent"}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("capstone")

def handle_turn(user_id: str, question: str) -> str:
    with tracer.start_as_current_span("agent.turn") as span:
        span.set_attribute("user.id", hash_id(user_id))
        span.set_attribute("gen_ai.request.model", MODEL)
        with tracer.start_as_current_span("retrieval"):
            hits = search_knowledge(question, k=5)
        span.set_attribute("gen_ai.usage.input_tokens", usage.prompt_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", usage.completion_tokens)
        return answer
```

Hierarchical spans mirror the W11-05 model: `agent.turn` → `retrieval` + `generation` + `tool.*` — the trace tree your dashboards and alerts consume. Redaction (W15-02) applies to every attribute.

## 3. The dashboard (metrics that matter)

| Panel | Query shape | Source |
|---|---|---|
| p50/p95 latency per feature | span duration by `feature` attr | E8-03 ledger + traces |
| tokens & $ per feature | token attrs × price table (E8-03) | traces |
| tool-error rate | tool spans with error / total | traces |
| cache-hit share | cached/total input tokens (W15-04) | traces |
| route distribution | router decisions (W14-04) | traces |
| guard-trip rate | guardrail spans (E7) / intake logs | W5-04 |
| escalation & 👍/👎 | user signals (W9-05) | product events |

Build it in Grafana over the OTel backend — one place where latency, cost, quality, and safety sit together (the W10-04 three-dimensions rule, visualized).

## 4. The alert set (from W15-02, tuned)

| Alert | Condition | Severity |
|---|---|---|
| error-rate spike | tool errors > 10% over 10 min | page |
| latency regression | p95 > baseline ×1.5 over 30 min | page |
| budget pressure | feature at 80% monthly budget | ticket |
| guard-trip spike | trips ×3 over baseline | investigate |
| empty-answer rate | insufficiency escape > 15% | investigate |
| cost anomaly | daily spend > forecast ×1.5 | ticket |

Tuning discipline (W15-02): each alert's threshold derives from your baseline p50/p95 ×headroom; every page must be actionable; monthly review kills noisy alerts (W10-04's metrics review, ops edition).

## Exercises

1. Instrument your W14 assistant with OTel spans (agent/retrieval/tool hierarchy); export to a local Jaeger (`docker run jaegertracing/all-in-one`); walk one trace.
2. Dashboard build: four panels from §3 in Grafana over your traces; include the cached-token share panel (W15-04's proof).
3. Alert tuning: simulate a tool-error spike (inject failures, W15-01); verify the page fires — then generate benign noise and verify it *doesn't*.
4. Unified story: export the same runs to LangSmith *and* OTel; reconcile token counts between them (any drift = an instrumentation bug).
5. SLO definition: write latency/cost/quality SLOs for your capstone's two flagship features — with the error budget implied by each.

## Pitfalls

- **Trace all, alert none** — observability without the alert set is a museum; §4 is the payoff
- **Unredacted OTel attributes** — full prompts in spans replicate the W15-02 PII problem at platform scale
- **Cardinality explosion** — `user.id` as a span attribute without hashing creates millions of time series; hash/bucket (E8-03's user attribution)
- **Vendor-lock instrumentation** — LangSmith-only traces can't feed the Grafana SLOs; OTel is the portable layer, vendors the optional views
- **Sampling decisions made silently** — 5% prod sampling (W15-02) must be a *documented policy* with the PII rationale

## Resources

- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — the span/attribute spec
- [OTel Python docs](https://opentelemetry.io/docs/instrumentation/python/) — SDK, exporters, resources
- W15-01/02/05 (limits, tracing, baselines) + E8-03 (ledger) — composed here
- Grafana [tempo/loki docs](https://grafana.com/docs/) — the visualization layer
