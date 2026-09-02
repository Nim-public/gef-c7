# 02 — Tracing, Guardrails & LangSmith

> Week 15 index: [README.md](README.md)

**Session 1 topics:** *Can trace/debug with LangSmith (or equivalent) and add guardrails.*

---

## What you'll learn

- LangSmith end-to-end: trace ingestion, dataset runs, evaluations, and dashboards
- Platform guardrails (moderation, PII, topic filters) layered with your own (W5-04)
- The observability upgrade path: JSONL → LangSmith → dashboards/alerts
- PII and retention policy for traces (production obligation, not optional)

## 1. LangSmith in five minutes

```powershell
pip install langsmith
setx LANGSMITH_TRACING=true
setx LANGSMITH_API_KEY="lsv2_..."
setx LANGSMITH_PROJECT="capstone"
```

With the LangChain/Agents SDK stacks, **every run traces automatically** (W11-05/W14-01) — traces, spans, tokens, latencies, tool calls land in the project dashboard. Your W10-04 JSONL and this dashboard are the same data; the dashboard adds aggregation, search, and team visibility.

```python
import langsmith as ls

@ls.traceable(name="capstone-turn")
def turn(question: str) -> str:
    hits = retriever(question, k=5)
    answer = chain.invoke({"context": format(hits), "question": question})
    return answer
```

What you get beyond W10-04's JSONL: full input/output payloads per span, run trees across agents/chains, latency/cost charts, dataset-linked experiments (§2), and alerting hooks.

## 2. Datasets + evaluations in LangSmith

Your W10-04 golden cases become **datasets**; every code/prompt change runs against them:

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset("capstone-agent-regression")
for case in json.load(open("eval/agent_cases.jsonl")):
    client.create_example(inputs={"goal": case["goal"],
                                 "reference": case["expected"]},
                          dataset_id=dataset.id)

# evaluate a new version:
results = client.run_on_dataset(
    dataset_name="capstone-agent-regression",
    llm_or_chain_factory=lambda: build_agent(),   # the candidate
    evaluation=eval_config,                        # your judge + programmatic checks (W10-04)
)
```

This is the W10-04/W11-05 regression suite, hosted: every change → one run → diffable scores. The W16 week formalizes the same loop for RAG metrics.

## 3. Guardrails at the platform layer

Your W5-04 guardrail sandwich, now with platform services:

| Guard | Your implementation | Platform option |
|---|---|---|
| input moderation | regex/keyword battery (W3-02) | OpenAI Moderation API, Bedrock Guardrails |
| PII scrubbing | NER + regex (W2-02) | presidio / provider PII filters |
| topic scope | classifier | Bedrock/Azure content filters, policy configs |
| output validation | citation checker (W5-04) | provider guardrail verdict hooks |
| prompt-injection screening | W3-02 battery | guardrail prompt-attack filters |

Layering rule (unchanged): platform filters are one *layer* — your own validators still run, because you control them and can test them (W5-04). Log every trip with the same schema, whichever layer caught it.

## 4. Trace hygiene (the production obligations)

| Concern | Policy |
|---|---|
| **PII in traces** | scrub before export (W2-02's cleaner on payloads) or self-host |
| **Retention** | traces expire (30 days default) — export weekly to your store (W10-04) |
| **Secrets** | never in prompts → never in traces (W3-02) |
| **Sampling** | 100% in dev; sample 5–20% in prod unless debugging (cost + storage) |
| **Access** | traces contain user data; project-level access control |

## Exercises

1. Enable LangSmith on your W14 assistant; run the 15-case eval; find the p95 run in the dashboard and explain its latency from the span waterfall.
2. Create the regression dataset (§2) from your `agent_cases.jsonl`; run it on two prompt versions — produce the diff report.
3. Add platform moderation to the intake (§3); rerun the W3-02 battery — which layer catches which attack first? (Layering audit, W5-04.)
4. Trace-scrub pipeline: intercept traces and redact email/phone/IDs (your W2-02 PII functions) — verify on 5 runs containing synthetic PII.
5. Failure dashboard: define 5 alert conditions (tool-error rate > 10%, guard-trip spike, p95 > SLA, budget aborts, empty-answer rate) — write the queries against your trace store.

## Pitfalls

- **Tracing only in dev** — prod incidents arrive as "it returned something weird" with no spans; always-on + sampling policy
- **Guardrail layering without an owner** — platform filter + your regex + the model's own refusal can *conflict*; define precedence and log which layer fired
- **Datasets that never grow** — a static regression set goes stale; feed production failures into it (W12-05's self-improvement, done honestly)
- **PII in dashboards** — traces are shared more than logs; scrub by default
- **Alert fatigue** — five alerts that fire daily are noise; tune thresholds on your p50/p95 (W10-04 baseline)

## Resources

- [LangSmith docs](https://docs.smith.langchain.com/) — tracing, datasets, evaluations, dashboards
- OpenAI [moderation guide](https://platform.openai.com/docs/guides/moderation) + Bedrock Guardrails / Azure AI Content Safety docs — the platform filter layer
- W5-04 (your guardrails), W10-04 (instrumentation), W11-05 (traces) — the layers composed here
- OpenTelemetry GenAI semantic conventions — the vendor-neutral trace schema (where this all converges)
