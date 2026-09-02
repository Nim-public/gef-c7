# Extension E8 — LLMOps at Scale

> Extensions overview: [../README.md](../README.md)

**Builds on:** W15 (production) · W14 (frameworks) · W16-01 (eval versioning)

**Practice build:** [05-practice-llmops.md](05-practice-llmops.md)

---

## Why this extension matters

W15 hardened a *single* agent; this week operates the *system* around it: model/prompt registries, CI/CD for prompts and agents, A/B and shadow deployment, cost management, and OpenTelemetry-grade observability. The theme: **every artifact that changes behavior gets versioned, gated, and monitored** — models, prompts, tools, schemas, eval sets.

## What you will be able to do after this week

- [ ] Run a model/prompt registry: versioned artifacts with lineage and rollback
- [ ] Build prompt/agent CI/CD: evals gate every change automatically
- [ ] Run A/B and shadow deployments for agent changes safely
- [ ] Manage cost: per-feature token accounting, budgets, and optimization ledger
- [ ] Ship OpenTelemetry GenAI traces and alert on the right signals

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-registry-cicd.md](01-registry-cicd.md) | Registries, lineage, prompt CI/CD | 3 h |
| 2 | [02-ab-shadow-testing.md](02-ab-shadow-testing.md) | A/B, shadow, canary deployments | 3 h |
| 3 | [03-cost-management.md](03-cost-management.md) | Token accounting, budgets, FinOps | 2–3 h |
| 4 | [04-otel-observability.md](04-otel-observability.md) | OTel GenAI conventions, dashboards, alerts | 2–3 h |
| 5 | [05-practice-llmops.md](05-practice-llmops.md) | The full loop on your capstone (practice) | 4 h |

## Environment setup

```powershell
pip install opentelemetry-sdk opentelemetry-exporter-otlp mlflow
```

## Self-check before E9

1. Your triage prompt changed silently in a hotfix. Which registry mechanism would have caught it (W3-02's versioning, enforced)?
2. Shadow deployment shows the new agent's *quality* matches but its *cost* is 3×. Do you ship? What does the W15-05 table say?
3. Per-feature cost attribution: which of your capstone features burns 60% of tokens — and do you know without adding instrumentation?
4. What's the OTel GenAI span for a tool call — and which three attributes must it carry for your W10-04 metrics to reconstruct?
5. Your memory-based agent (E9 preview) changes behavior over time *by design*. How do you evaluate a system whose baseline moves?
