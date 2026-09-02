# 05 — Agentic RAG with phiData

> Week 12 index: [README.md](README.md)

**Session 2 topic:** *Building a custom toolkit for advanced data handling and retrieval-augmented generation (RAG) — applied: the agent decides the retrieval strategy.*

---

## What you'll learn

- Agentic RAG: the agent *chooses* the retrieval strategy per question (vs W4's fixed pipeline)
- The three-way decision: knowledge search vs SQL vs clarify — implemented as agent behavior
- Fusing agentic answers with your evaluation harness (W5-05 measures agents too)
- Where this sits on the W3-05 lever table, and when *not* to make RAG agentic

## 1. Fixed RAG vs agentic RAG

| | W4–5 pipeline RAG | W12 agentic RAG |
|---|---|---|
| retrieval decision | hardcoded (always hybrid, top-k) | the agent picks tool(s) per question |
| question types | one shape (prose) | mixed shapes (prose, numeric, both, none) |
| predictability | high — the W4 contract | lower — model-driven (W3-05) |
| fixable by | prompt/retriever tuning | prompt + tool descriptions + routing rules |

Your W6-04 router already made this decision *deterministically*. Agentic RAG hands the same decision to the model — justified when question shapes are genuinely open-ended (user mixes "how many", "explain", "compare" unpredictably).

## 2. The build: one agent, three powers

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from capstone_toolkit import CapstoneToolkit       # file 03

agent = Agent(
    name="Capstone RAG agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[CapstoneToolkit()],
    knowledge=knowledge,                            # file 02 (optional: knowledge + tools)
    search_knowledge=False,                         # retrieval via the TOOLKIT instead,
                                                    # so formatting/filtering stays yours
    instructions=[
        "Strategy per question:",
        "1. Prose/policy/explanation → search_knowledge.",
        "2. Counts/sums/comparisons → sql_query.",
        "3. Mixed questions → both, then synthesize; cite each source type.",
        "4. Neither answers → 'I don't have that information.'",
        "Cite [id] for documents and the SQL for tables.",
    ],
    markdown=True,
)
```

The design choice to notice: retrieval via the **toolkit** (not `search_knowledge=True`) keeps your hybrid implementation, filters, thresholds, and citation format (W5-03/W4-05) — the framework's knowledge search is convenient, but your harness already proves *your* pipeline. Use both approaches in the eval and let the numbers argue.

## 3. What "agentic" adds over the router

Your W6-04 router was rule-based/zero-shot: one question → one arm. The agent adds:

1. **Multi-step synthesis** — "compare refund policy (docs) with actual refund volumes (tables)" = two calls, one answer
2. **Self-correction** — empty SQL result → try `search_knowledge` before giving up (the error-phrasing loop, W10-05)
3. **Clarification** — ambiguous question → ask the user (an agent turn, not a pipeline branch)
4. **Query decomposition** — a compound question split into a search and a SQL call with different phrasings (W5-03's fusion, now model-driven)

Each of these is a *trajectory property* — measure with W10-04's harness, not vibes.

## 4. Evaluating agentic RAG (the W5-05 harness, extended)

| Metric | Fixed RAG (W5) | Agentic RAG adds |
|---|---|---|
| faithfulness/relevancy (Ragas) | ✓ | ✓ — same |
| context precision/recall | of the fixed top-k | per *chosen* tool's output |
| tool-selection accuracy | n/a (no choice) | router accuracy over the 3 strategies |
| steps/cost per answer | fixed | **variable — report p50/p95** |

```python
# eval row (merged W10-04 + W5-05 style)
{"question": q, "route": chosen_tools, "expected_route": exp_route,
 "answer": ..., "faithfulness": ..., "steps": n, "tokens": t}
```

Route accuracy + Ragas + cost, on your 25-question harness — that's the agentic-RAG eval table for the capstone README.

## 5. When agentic RAG is wrong (W3-05's rule, sharpened)

- **Known, fixed question shapes** → the deterministic router (W6-04) is cheaper, faster, testable
- **Latency SLAs < 2 s** → an agent turn adds an LLM roundtrip per decision
- **High-volume simple queries** → fixed pipeline; escalate only on low confidence (W5-04)
- **The agent ignores instructions under load** — measure instruction-following on 100+ runs before trusting strategy rules (W10-04)

The honest capstone framing: *fixed hybrid RAG for the 80%, agentic routing for the 20% open-ended tail* — with the router vs agent boundary measured, not guessed.

## Exercises

1. Build the agent (§2) with toolkit-only retrieval; run your 25-query W4 harness through it (agent in the loop). Compare hit quality vs direct hybrid search — what did the extra LLM layer cost/improve?
2. Route accuracy: 20 mixed questions; log which strategy the agent chose vs the W6-04 router's answer. Where do they disagree — and who's right?
3. Multi-step synthesis demo: "compare the refund policy (docs) with actual refund request volumes (tables)" — verify both sources are cited and neither is invented.
4. Self-correction probe: break `sql_query` (rename a column); does the agent's second attempt fix the column (W6-03's repair loop, agent-driven)?
5. Cost table: fixed pipeline vs agentic RAG on your 25 questions — tokens, steps, p95 latency. Write the routing recommendation for the capstone.

## Pitfalls

- **Agentic for everything** — the loop is a latency/cost tax on questions a pipeline answers perfectly (W3-05)
- **Two RAG systems drifting** — the framework's Knowledge *and* your toolkit retriever with different chunkings; one source of truth (file 02)
- **Unmeasured routing** — "the agent usually picks right" is not a metric; log and score every route
- **Clarify-loops** — the agent asking the user endless clarifying questions; cap clarification turns in instructions
- **Citations lost in synthesis** — multi-source answers must keep per-source citations (W4-01's contract, multi-arm edition)

## Resources

- Agno [Knowledge + hybrid search docs](https://docs.agno.com) — the framework layer
- W6-04 (router), W5-03/05 (retrieval + evals), W10-04/05 (trajectory harness + context rules) — composed here
- LangGraph Self-RAG examples (W13 preview) — the graph-shaped version of adaptive retrieval
- Anthropic, *Building effective agents* — the routing pattern formalized
