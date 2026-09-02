# 05 — Weekly Task: phiData Agent for Data-Intensive Capstone Tasks

> Week 13 index: [README.md](README.md) · **Due: before Week 14 (by 12 Dec)**

**Task (from the schedule):** *Integrate a phiData agent to handle data-intensive tasks in your capstone project.*

This task connects Week 12's framework to your capstone's *structured* half: the Agno agent (with your toolkits) becomes the official handler of data-intensive questions — and you evaluate it head-to-head against the W11 SQL specialist, using the W10-04 trajectory harness.

---

## 1. Deliverable

```
phidata-agent/
  agent.py               # Agno agent with your toolkits + knowledge (W12 files assembled)
  eval/
    cases.jsonl          # 15 data-intensive tasks (from your W6/W10 eval sets)
    run_eval.py          # trajectory harness (W10-04) — Agno edition
    results.md           # comparison table vs W11 + failure analysis
  README.md              # integration notes, decisions
```

Demo: 3 data-intensive questions answered with SQL audit trails + one chart + one clarified ambiguity.

## 2. Requirements (graded)

### Agent integration
- [ ] Agno agent assembled from your W12 components: `CapstoneToolkit` (SQL + retrieval), `Knowledge` over your docs, datetime injection, history
- [ ] Constitution as `instructions` (grounding, citation, insufficiency rules — W12-02 §4)
- [ ] Runs on ≥15 data-intensive tasks from your existing eval sets (W6-03's SQL questions + W10-04's mixed tasks)

### Evaluation
- [ ] Metrics: success rate, route (tool sequence) accuracy, steps p50/p95, tokens p95, tool-error rate — same schema as W10-04
- [ ] Numeric grounding check: every number in answers traceable to tool rows (W12-04 §3's `numbers_supported`)
- [ ] Comparison table vs the W11-02 `sql_agent` on identical cases

### Analysis (README)
- [ ] Where Agno beats the SDK path (toolkit ergonomics? knowledge wiring? playground debugging?)
- [ ] Where it doesn't (guardrails? trace export? loop control?) — with evidence
- [ ] Decision: which framework your capstone *ships* for data tasks, and why

## 3. The 15 data-intensive cases (design guide)

| # | Shape | Example |
|---|---|---|
| 1–5 | single aggregation | "total revenue by region last quarter" |
| 6–8 | multi-step (aggregate → compare → trend) | "which region declined month-over-month" |
| 9–10 | SQL + prose hybrid | "refund policy (docs) vs refund volumes (tables)" |
| 11–12 | chart requests | "monthly orders as a bar chart" |
| 13–14 | ambiguous → clarify or state assumptions | "top customers" (by what metric?) |
| 15 | unanswerable from data | insufficiency escape |

Score success = correct numbers (from tool rows, verified) + correct routing + audit trail present.

## 4. Rubric

| Area | Weight |
|---|---|
| Agent integration (toolkits, knowledge, constitution) | 25% |
| Evaluation rigor (15 cases, merged metrics, numeric grounding) | 30% |
| Comparison vs W11 specialist (same cases) | 25% |
| README decisions + framework verdict | 15% |
| Demo (3 flagship trajectories) | 5% |

## 5. README integration section (answer explicitly)

1. **Assembly**: which W12 pieces (Knowledge/Toolkit/storage) and which capstone systems they wrap
2. **Grounding stack**: the three defense layers active on numeric answers (W12-04 §3)
3. **Comparison verdict**: Agno vs OpenAI Agents SDK for data-intensive tasks — by your measurements, not marketing
4. **Failure modes** (≥3) with trajectory evidence
5. **W14 bridge**: your MCP server (W10-03) + this agent — what does LangChain's MCP adapter change about how the capstone exposes tools? (One paragraph — W14 opens with it.)

## 6. Stretch (pick one)

- Streaming analytics: `print_response(stream=True)` into a Gradio block (W9-01) with the SQL shown live
- The playground as a team demo: multi-session histories for three personas (support, analyst, auditor) over the same knowledge
- Add a `verify_number` tool (W12-04 §3) and measure: hallucinated-number rate before/after across the 15 cases

Office Hours (10 Dec): bring the comparison table. Week 14 (LangChain + MCP) generalizes the tool layer you've now built three times (registry → SDK tools → Agno toolkit) — your evidence decides what the capstone keeps.
