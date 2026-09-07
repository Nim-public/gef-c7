# 05.4 — SLM vs API: The Measured Decision

> Subfolder index: [README.md](README.md) · Parent: [../05-small-language-models.md](../05-small-language-models.md)

---

## What you'll learn

- The benchmark protocol for the routing decision (W15-04, applied to model choice)
- The cost model with amortization
- The privacy and compliance dimension
- The final decision table for your capstone

## 1. The benchmark protocol

```python
CASES = load_cases("eval/slm_vs_api.jsonl")     # 30 cases across 5 task classes

def benchmark(system_fn, name):
    rows = []
    for case in CASES:
        t0 = time.perf_counter()
        out = system_fn(case)
        rows.append({"task": case["task_class"], "latency": time.perf_counter() - t0,
                     "correct": grade(out, case), "cost": cost_of(out, system_fn.name)})
    return aggregate(rows, name)
```

The protocol rules (W5-05/W16-01 discipline): same cases, same grading, both systems on the same hardware day, n reported, slices per task class. The classes: extraction/classification, summarization, tool-call JSON, reasoning, creative — because the size classes fail *differently per task* (W2-05 §1's table).

## 2. The cost model with amortization

```python
def monthly_cost(queries_day: int, tokens_per_query: int, tier: str) -> dict:
    q = queries_day * 30
    if tier == "api-mini":
        return {"marginal": q * tokens_per_query * 0.15 / 1e6, "fixed": 0}
    if tier == "slm-cpu-server":
        return {"marginal": 0, "fixed": 40}        # a small always-on box
    if tier == "gpu-server":
        return {"marginal": 0, "fixed": 350}
```

The break-even: API cost scales linearly with volume; hardware is a step function. At 1M queries/day × 400 tokens: API ≈ $60+/day vs a $300/mo box — the crossover is a few weeks of traffic. Below 10k/day, the API is cheaper *and* better — the honest conclusion the routing table must state.

## 3. Privacy and compliance (the non-cost dimension)

| Question | API | Local SLM |
|---|---|---|
| Can data leave the org? | provider's terms | your control |
| PII in prompts | governed by DPA | never leaves |
| Audit access | provider logs | your logs (W10-04) |
| Model updates | provider-driven (E8-01 pinning mitigates) | your choice |
| Certification (SOC2/ISO) | provider's attestations | yours to build |

For regulated workloads (health, finance, legal), local SLMs are often the *only* answer regardless of quality — the W15-04 routing table gains a hard constraint row: "egress allowed? no → local, period."

## 4. The final decision table (for your capstone README)

| Dimension | API | Local SLM | Your measurement |
|---|---|---|---|
| task accuracy (sliced) |  |  |  |
| p50/p95 latency |  |  |  |
| $/1k queries |  |  |  |
| privacy/egress | provider terms | full control |  |
| determinism | provider infra | your infra |  |
| ops burden | low | high |  |

## Exercises

1. Run the protocol (§1): 30 cases × {API, Ollama-SLM} — the sliced accuracy/latency/cost table.
2. The privacy constraint test: your compliance scenario (E5-04's) — which dimension of §3 decides, independent of cost?
3. Hybrid design: local first, API escalation on low confidence (W15-04) — implement, measure the escalation rate and the blended cost.
4. Failure-mode comparison: kill the network during local and API runs — availability behavior documented per tier.
5. Write the model-strategy section of your capstone README: the tier table, the routing rule, the privacy constraints, and the break-even — the E8-03 forecast with hardware included.

## Pitfalls

- **Cost compared without quality** — a cheap wrong answer is expensive; the slices table carries accuracy beside cost
- **Local serving without ops** — updates, monitoring, capacity (W15's rules) — the "free" tier has a labor cost
- **Escalation without observability** — the hybrid needs per-tier metrics or the blend is undebuggable (E8-04)
- **Privacy as a claim without a test** — egress monitoring (E7-04) proves the local tier's isolation; claims don't
- **One benchmark day** — drift (E8-04) applies to local models too (Ollama updates); re-run periodically

## Resources

- W2-05 parent, W15-04 (routing), E8-03 (cost), E7-04 (egress) — composed here
- [Ollama OpenAI compatibility](https://ollama.com/blog/openai-compatibility) — the endpoint details
- [LocalAI](https://localai.io/) — an alternative local OpenAI-compatible stack
