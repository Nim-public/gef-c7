# 01 — Evaluation Strategy: Ragas Revision, Cloud Evals, Versioning

> Week 16 index: [README.md](README.md)

**Session 1 topics:** *Revise Ragas metrics & workflows for RAG (faithfulness, answer relevancy, context precision/recall). Cloud evals: Vertex AI GenAI Eval, Azure Prompt Flow evals, Bedrock Evaluations/Guardrails. Offline vs online evals; LLM-as-judge; dataset/versioning strategy.*

---

## What you'll learn

- Ragas, revised — the four metrics as a *diagnosis system* (W5-05's table, hardened)
- Offline vs online evaluation, and where each belongs in your capstone
- LLM-as-judge calibration as a first-class process
- Dataset & versioning strategy: the artifact that makes all of it repeatable
- The cloud eval platforms: what they add over local Ragas

## 1. Ragas revision — the four metrics as diagnosis

W5-05 introduced them; here's the revision checklist — run the suite, then *read as diagnosis*:

| Pattern in your scores | Diagnosis | First fix (cheapest) |
|---|---|---|
| context recall low, precision fine | right *kind* of content missing | chunking/embedding upgrade (W5-01/02) |
| context precision low, recall fine | right chunks buried under noise | reranking (W5-03), reduce k |
| faithfulness low, contexts good | model inventing beyond context | prompt contract (W4-01), temperature ↓, k ↓ |
| answer relevancy low | wrong question understood | query rewrite (W5-03 fusion) / router (W12-05) |
| all low | eval set or pipeline broken | inspect 5 raw cases by hand first |

Ragas mechanics (W5-05 code unchanged): `evaluate(ds, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])` with judge LLM + embeddings pinned (temperature 0, version recorded). What revision adds: run it **per pipeline slice** (per route, per doc type — W12-05's table) and **per version** — the scores only mean something next to a previous version's scores.

## 2. Offline vs online evaluation

| | Offline (pre-deploy) | Online (in production) |
|---|---|---|
| Data | fixed labeled sets (golden + adversarial) | live traffic, sampled |
| Metrics | Ragas, judge scores, programmatic checks | 👍/👎, escalation rate, retention, task completion |
| Catches | regressions before release | what golden sets can't imagine |
| Cadence | every change (W15-02 CI) | continuous dashboards (W15-02) |

Your capstone already produces the online signal: W9-05's 👍/👎 logging and W10-04's run logs. The strategy to write down: **golden set gates deploys; online signals feed the golden set** (W12-05's self-improvement loop, formalized). Add A/B: a new retrieval version runs behind a flag on 10% of traffic until its online signals match.

## 3. LLM-as-judge, calibrated (the revision)

W5-05's rules, now operationalized:

1. **Pin the judge** (model, temperature, prompt version) like any component
2. **Validate the judge against human labels** — score agreement (Cohen's κ or agreement rate) on 30 cases before trusting it; re-validate when the judge model changes
3. **Use rubrics, not vibes** — score against written criteria (the W10-04 trajectory rubric pattern)
4. **Position-bias control** for pairwise comparison (A/B swapped, average)

## 4. Dataset & versioning strategy (the deliverable)

| Artifact | Version | Contents |
|---|---|---|
| eval dataset | `v3` (semantic version) | questions + reference answers + expected sources + adversarial cases |
| judge prompt | git hash | rubric text |
| judge model | pinned id + temp | — |
| pipeline under test | git hash + config | retriever, prompt, model ids |

Rules: **immutable versions** (append-only; fixes create v3.1, never edit v3); every version documents *what changed and why*; **slices** (by route/doc type/urgency) tracked per version; a `CHANGELOG-eval.md` mapping score jumps to causes ("v3: +40 adversarial injection cases — faithfulness p95 unchanged, route accuracy −2%").

Your capstone already has the raw material: W9/W10/W12 JSONL logs → golden cases; W2/W3 batteries → adversarial cases; W5-05's 30-row set → the seed.

## 5. Cloud eval platforms (what they add)

| Platform | Shape | Adds over local Ragas |
|---|---|---|
| **Vertex AI GenAI Evaluation** | GCP-managed metric runs | managed judge LLMs, GCP integration, scale |
| **Azure AI Foundry / Prompt Flow evals** | Azure-managed flows + eval | enterprise deployment alignment, content-safety metrics |
| **AWS Bedrock Evaluations/Guardrails** | Bedrock-managed | runs against Bedrock models, built-in guardrail metrics |

Decision guidance: local Ragas (free, full control, your pinned judge) for development and CI; a cloud platform when your deployment already lives there (model, compliance, or team alignment) — the *metrics and discipline are identical*; only the runner changes. Never adopt a cloud evaluator whose judge you can't inspect against your golden labels (§3).

## Exercises

1. Slice your W5-05 eval run by route and doc type (the §1 table). Which slice is weakest? Fix the cheapest failing stage; show the before/after table.
2. Judge validation: label 30 cases by hand; compute agreement between your judge and you (and κ). Below 0.6 → fix the judge rubric before trusting any score.
3. Version an eval set: create `eval_v2` adding 10 adversarial + 10 slice-coverage cases; write the CHANGELOG entry; rerun the suite — what moved?
4. Offline/online audit: from your W9-05 👍/👎 log, find 3 questions your golden set doesn't cover; add them. What % of live traffic does your golden set actually represent?
5. Cloud eval trial: run 10 cases through one cloud platform's evaluator (Vertex/Bedrock/Azure free tier); compare its scores to your local Ragas run — where do they disagree and why?

## Pitfalls

- **Slices ignored** — an aggregate faithfulness of 0.9 hides a 0.3 slice that's your demo's core flow
- **Judge changed silently** — model or prompt drift invalidates every historical score comparison (§4's versioning exists for this)
- **Online metrics without offline sets** — 👎 signals with no golden case → no fix, no regression test
- **Overfitting the golden set** — tuning prompts until the set maxes out makes it a training set; keep a held-out slice (W3-05's evaluation discipline)
- **Eval set without distribution notes** — document what the set covers (routes, doc types, difficulty) or coverage gaps stay invisible

## Resources

- [Ragas docs](https://docs.ragas.io) — metrics + `evaluate` workflows (W5-05's source)
- Vertex AI [GenAI Evaluation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview) · Azure [AI Foundry evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/) · [Bedrock Evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)
- LangSmith [datasets & evaluations](https://docs.smith.langchain.com/) (W15-02) — the CI runner for local sets
- W5-05, W10-04, W12-05 — the three eval artifacts this file formalizes
