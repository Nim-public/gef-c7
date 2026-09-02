# 03 — Project: Customer Support Ticket Router

> Week 13 index: [README.md](README.md)

**Session 1 project:** *Customer Support Ticket Router — develop an intelligent system that triages and routes support tickets: 1. Intent classification for ticket categorization. 2. Urgency assessment based on content analysis. 3. Knowledge base search for existing solutions. 4. Escalation logic for complex issues. 5. Auto-response generation for common problems.*

---

## What you'll learn

- The session project, built over **your capstone components** (W5 RAG, W6 SQL, W11 guardrails)
- Five graph nodes mapped to the five requirements — with state design
- Escalation logic as conditional edges (W10-04's HITL, graph edition)
- Comparison: this graph vs the W11 handoff router vs the W6-04 deterministic router

## 1. The design (five requirements → five nodes)

```
START ─► classify (intent+urgency) ─► route ─┬─► kb_search ─► draft_reply ─► qa_check ─► END
                                             ├─► data_lookup ─► draft_reply
                                             └─► escalate ─► END
```

State:

```python
from typing import Annotated, TypedDict
from pydantic import BaseModel

class TicketState(TypedDict):
    ticket: str
    category: str          # billing | technical | account
    urgency: str           # low | medium | high
    documents: list[str]
    sql_result: str
    draft: str
    escalated: bool
    citations: list[str]
    log: Annotated[list[str], lambda a, b: a + [b]]    # append-only audit trail
```

## 2. classify — structured extraction (the intent + urgency node)

```python
from pydantic import BaseModel
from openai import OpenAI
client = OpenAI()

class Classification(BaseModel):
    category: str          # billing | technical | account
    urgency: str           # low | medium | high
    reasoning: str

def classify(state: TicketState):
    resp = client.beta.chat.completions.parse(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "system", "content":
                   "Classify support tickets. category in (billing, technical, account); "
                   "urgency low/medium/high — high only if: service down, money at risk, "
                   "or safety. Output reasoning in one sentence."},
                  {"role": "user", "content": state["ticket"]}],
        response_format=Classification,
    )
    c = resp.choices[0].message.parsed
    return {"category": c.category, "urgency": c.urgency,
            "log": [f"classified={c.category}/{c.urgency}: {c.reasoning}"]}
```

Compare with Week 2's zero-shot classifier (fast, fixed labels) — the LLM version adds *reasoning* and handles novel phrasing; your W2 model remains the cheap pre-filter (file 02's pattern). W11-02's `output_type` did the same job — LangGraph just puts the parse *in a node you own*.

## 3. route — escalation logic as conditional edges (requirement 3/4)

```python
def route(state: TicketState) -> str:
    if state["urgency"] == "high":
        return "escalate"                          # requirement 4: escalation
    if state["category"] in ("billing", "account"):
        return "data_lookup"                       # W6 Text2SQL arm
    return "kb_search"                             # requirement 3: KB search

workflow.add_conditional_edges("classify", route,
    {"escalate": "escalate", "data_lookup": "data_lookup", "kb_search": "kb_search"})
```

Escalation node (requirement 4):

```python
def escalate(state: TicketState):
    return {"escalated": True,
            "draft": (f"This ticket ({state['category']}, {state['urgency']} urgency) "
                      "has been escalated to a human specialist. Reference: "
                      f"{hash(state['ticket']) % 100000:05d}."),   # audit id
            "log": [f"escalated: {state['urgency']} {state['category']}"]}
```

## 4. kb_search + data_lookup + draft (requirements 3/5)

```python
def kb_search(state: TicketState):
    hits = search_knowledge(f"{state['category']}: {state['ticket']}", k=5)  # W9-05
    return {"documents": [h["text"] for h in hits["hits"]],
            "citations": [h["id"] for h in hits["hits"]],
            "log": [f"kb hits: {len(hits['hits'])}"]}

def data_lookup(state: TicketState):
    r = run_query(f"{state['category']} status and history for this ticket: {state['ticket']}")
    return {"sql_result": f"{r['sql']}\n{r['rows']}", "log": ["data_lookup done"]}

def draft_reply(state: TicketState):
    src = state.get("documents") or [state["sql_result"]]
    resp = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "system", "content":
                   "Draft a 4-sentence reply. Ground every claim in the provided material. "
                   "Cite [doc:id] where used. If material is insufficient, say what's needed."},
                  {"role": "user", "content": f"Ticket: {state['ticket']}\n\nMaterial:\n" + "\n".join(src)}])
    return {"draft": resp.choices[0].message.content}

def qa_check(state: TicketState):                   # W5-04 output guard, as a node
    ok = all(c in str(state) for c in state.get("citations", [])) or state["escalated"]
    return {"log": [f"qa_check passed={ok}"]}
```

`qa_check` as a *node* (not an exception path) keeps the graph inspectable — the audit trail in `log` shows the check ran.

## 5. Wire, run, evaluate

```python
router = workflow.compile()
result = router.invoke({"ticket": "I was charged twice for my subscription this month."})
print(result["draft"], "\n", result["log"])
```

Evaluation (your harnesses, graph edition):

- **W10-04 trajectory metrics**: node path per ticket, tokens, latency
- **W5-05 Ragas** on `draft` vs reference answers for 20 labeled tickets
- **W2-02/W3-02 battery**: injection tickets ("ignore instructions…") must route to escalate/deflect — assert in pytest
- **Route accuracy**: 20 tickets vs human labels — compare against the W6-04 router *and* the W11-02 handoff router (three-way table for the capstone README)

## Exercises

1. Build the full router over your capstone categories; run 10 tickets; print each node path.
2. High-urgency drill: 3 "service down" tickets — verify all escalate *before* any retrieval (edge ordering as a security property).
3. Add a `clarify` node: tickets with missing required info route to a clarification question instead of a draft (the W12-05 clarification turn, graph edition).
4. Three-way router comparison: W6-04 rules vs W11-02 handoffs vs this graph on the same 20 tickets — accuracy, latency, and auditability. Table for the README.
5. Regression cases: save 3 good + 3 adversarial tickets as graph tests (assert node paths) — the file 05 pattern, graph edition.

## Pitfalls

- **Classification drift under paraphrase** — the same ticket phrased 3 ways classifying differently; test with paraphrase sets (W5-04 consistency)
- **Escalation bypass** — a "high urgency" flag *after* routing is useless; urgency gates the first conditional edge
- **Drafting from thin material** — the KB-arm with zero hits must route to escalate/clarify, not generate
- **Audit trail optional** — `log` as a reducer field is what makes the graph reviewable; without it you're back to W11's opaque runs
- **Copy-pasting W11 agents into nodes unchanged** — nodes should compose *your* validated functions (W6/W9), not re-prompt from scratch

## Resources

- LangGraph [Customer Support / ticket-routing examples](https://langchain-ai.github.io/langgraph/tutorials/) — the session project's reference implementations
- LangGraph [structured outputs](https://langchain-ai.github.io/langgraph/) — Pydantic node outputs (classify node)
- W2-02 (classification), W5-04 (guards), W10-04 (HITL), W11-02 (handoff comparison) — the composed pieces
- [Structured outputs with `client.beta.chat.completions.parse`](https://platform.openai.com/docs/guides/structured-outputs) — the classify node's parsing
