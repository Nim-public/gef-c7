# 05.1 — The Six Levers

> Subfolder index: [README.md](README.md) · Parent: [../05-techniques-comparison.md](../05-techniques-comparison.md)

---

## What you'll learn

- Each lever's mechanism, cost, latency-to-change, and blind spots
- The composition rules: which levers stack, which conflict
- The levers as a maturity ladder for your capstone

## 1. The levers, deep

| Lever | Mechanism | Changes | Can't change | Latency to change |
|---|---|---|---|---|
| **Pre-training** | next-token on trillions of tokens | knowledge, language ability | your private data | months, $M |
| **RLHF/instruct** | SFT demos + preference pairs | persona, helpfulness, refusals | private facts | months |
| **RAG** | retrieve documents into context | facts available at ask-time | model behavior/style | minutes |
| **Agents/tools** | LLM calls tools, loops | capabilities — actions, live data | the model's judgment quality | days |
| **Optimization** | caching, batching, routing, quantization | speed/cost at same quality | quality | days |
| **Fine-tuning** | gradient updates on examples | style, format, narrow skills | private facts (rot), general knowledge | days–weeks |
| **Distillation** | small model imitates teacher | capability density per dollar | frontier reasoning | weeks |

## 2. The composition rules

**Stack well:** RAG + fine-tuned-format (facts from retrieval, style from adapters); agents + optimization (routing per tool); distillation of an agentic teacher.

**Conflict:** fine-tuning *facts* conflicts with RAG *facts* (two sources of truth); over-tuned style conflicts with RAG-cited tone (the model argues with its own context); aggressive quantization + heavy fine-tuning compounds quality loss.

**The one-lever mistake:** "accuracy is low → fine-tune" when the real failure is retrieval (W3-05's diagnosis order: data → LR/schedule → capacity → regularization, applied to levers).

## 3. The evidence rule

Every lever decision cites an experiment: the W4-05 harness for retrieval changes, the W1-05 eval for classifier changes, the W5-05 metrics for generation quality. A lever adopted without a measured before/after is a hypothesis, not a decision — and hypotheses get re-litigated every sprint.

## Exercises

1. The lever audit: for each of your capstone's current components, name the levers already pulled and the evidence for each.
2. The anti-lever inventory: three levers you explicitly did NOT pull, with the reason — the discipline reviewers respect.
3. The composition check: find one place where two of your levers conflict (e.g., fine-tuned tone vs RAG-cited tone) — resolve with a rule.
4. The cost-of-change table: for each lever, estimate the engineering days to change it in your capstone — the table drives the sprint plan.

## Pitfalls

- **Lever envy** — adopting the exciting lever (fine-tuning) over the boring one (better retrieval) that actually fixes the failure
- **Levers without baselines** — you can't measure a lever's effect without the harness (W4-05's eval set)
- **Simultaneous lever pulls** — two changes at once = attribution impossible (W5-02's confound rule)
- **The pre-training fantasy** — no capstone needs lever 1; if your plan says "pre-train", re-read the levers

## Resources

- W3-05 parent (the decision table), W16-01 (the evidence discipline) — composed here
- Gekhman et al., *Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?* — the fine-tune-the-facts evidence
- Lewis et al., *RAG* — the retrieval-over-params argument
