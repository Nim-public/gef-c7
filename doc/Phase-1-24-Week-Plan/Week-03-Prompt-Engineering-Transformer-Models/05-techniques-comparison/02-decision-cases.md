# 05.2 — Decision Cases

> Subfolder index: [README.md](README.md) · Parent: [../05-techniques-comparison.md](../05-techniques-comparison.md)

---

## What you'll learn

- Worked lever decisions across real scenarios — the reasoning shown
- The trap catalog: the failure patterns teams actually hit
- The evidence format for each decision

## 1. Case: the facts trap

**Scenario:** the model states "our refund window is 30 days" but the policy is 5.

| Option | Analysis |
|---|---|
| Fine-tune on policy docs | works briefly; new policy → model still wrong; unversioned knowledge |
| RAG with citations | correct after re-index; auditable; fresh |
| Prompt the policy | works for ONE policy; unmanageable at scale |

**Decision: RAG** — facts change, so facts belong in the retrievable layer. The fine-tune option is recorded as *rejected with the rot mechanism named* — the rejection reasoning is the deliverable (W3-05's table with your project's rows).

## 2. Case: the style problem

**Scenario:** the model's answers are correct but sound like a robot; users stop using it.

| Option | Analysis |
|---|---|
| Prompt the tone | fast, works until context pressure |
| Fine-tune on 500 styled answers | durable style, measurable, costs GPU-hours |
| Distill a styled teacher | strongest style, most work |

**Decision ladder:** prompt → few-shot style examples (W3-01) → fine-tune if the eval shows prompting plateaued. The ladder is climbed with evidence at each rung, not skipped to the top.

## 3. Case: the cost problem

**Scenario:** quality is fine; p95 is 9 s and $0.04/query.

| Lever | Expected effect |
|---|---|
| prompt restructure + caching | −30–60% input cost (W15-04) |
| route easy queries to SLM | −40–70% blended cost (W15-04) |
| vLLM serving | 2–5× throughput (W15-03) |
| quantization | −50–75% memory (W22-03) |

**Decision: optimization first** — same quality, cheaper; then revisit quality with the savings budget.

## 4. Case: the security review

**Scenario:** the security team asks how the agent can't exfiltrate data.

| Control | Evidence |
|---|---|
| egress allow-list (E7-04) | proxy logs, zero external destinations |
| tool gates (W10-04) | the approval workflow + denial logs |
| output validation (W5-04) | the citation/schema checker battery |
| no secrets in context (W3-02) | secret scan on all prompts |

The review passes on *evidence*, not architecture diagrams — each control's test result is the artifact.

## Exercises

1. Decision memos: write the four §-level decisions for your capstone in the same format (options, analysis, decision, evidence) — 1 page each.
2. The rejected-options audit: for each decision, name the option you rejected and the mechanism that made it wrong — the reasoning trail reviewers probe.
3. The pivot drill: your data source changes next month — which levers does that re-open, and what re-decisions follow?
4. Evidence ledger: consolidate every lever decision into one table (decision, evidence, date, owner) — the living record.

## Pitfalls

- **Decisions without rejected options** — the analysis is the value; "we chose RAG" without "why not fine-tuning" invites re-litigation
- **Lever decisions made by enthusiasm** — the newest technique is not the right lever; the failure mode is
- **Unpriced decisions** — every option carries a cost estimate; decisions without costs aren't decisions
- **The once-and-forever decision** — levers are revisited as traffic/quality/costs change; date every decision

## Resources

- W3-05 parent (the table), W15-04/05, W16-01 — composed here
- The Gekhman et al. fine-tuning-hallucination evidence (W3-05's resource) — the facts-trap proof
