# 04 — Agentic RAG with LangChain

> Week 14 index: [README.md](README.md)

**Session 2 project:** *Agentic RAG with LangChain — 1. Intelligent Routing: AI agents automatically decide which knowledge sources to query based on user intent and context. 2. Multi-Step Reasoning: break complex questions into sub-tasks, retrieve relevant data, and synthesize comprehensive answers. 3. Dynamic Knowledge Selection: adaptively choose between vector databases, APIs, and documents for optimal information retrieval. 4. Self-Improving Pipeline: agents learn from interactions to refine retrieval strategies and improve response accuracy over time.*

---

## What you'll learn

- Agentic RAG in LangChain: retrieval as a *decision*, routing across multiple knowledge sources
- Multi-step reasoning over decomposed questions (query planning)
- The honest version of "self-improving": feedback loops that store what worked
- Graph vs agent implementations of the same four capabilities (W13's Self-RAG graph revisited)

## 1. The four capabilities, mapped to mechanics

| Schedule capability | Actual mechanism | Built in |
|---|---|---|
| Intelligent routing | a router (rules → LLM classifier) picks knowledge source(s) | W6-04, now LLM-native |
| Multi-step reasoning | decompose → retrieve per sub-question → synthesize | W5-03 fusion, agentic |
| Dynamic knowledge selection | tools per source (vector, SQL, web/API) | W9-02's multi-column + W6 tools |
| Self-improving pipeline | log outcomes → refine queries/knowledge → re-evaluate | W10-02 episodic memory + W16 evals |

The honest framing (W12-05 §5): the *pipeline* doesn't learn; the *system* improves because you feed logged outcomes back into retrieval rules and eval sets. Claim that version.

## 2. The build: three-source routing agent

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def vector_search(query: str) -> str:
    """Semantic search over capstone documents (policies, handbooks, guides)."""
    return json.dumps(hybrid_search(query, k=5)["hits"], default=str)[:2000]  # W4/W5

@tool
def table_lookup(question: str) -> str:
    """Numeric/aggregational questions over capstone tables (Text2SQL, read-only)."""
    return json.dumps(run_query(question), default=str)[:2000]                # W6-03

@tool
def web_fallback(query: str) -> str:
    """Search the public web — ONLY for questions outside capstone data."""
    return web_search_stub(query)                      # gated: see W10-04 HITL

router_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[vector_search, table_lookup, web_fallback],
    system_prompt=(
        "Routing rules: capstone facts → vector_search; numbers/aggregations → table_lookup; "
        "only if both fail AND the question is public-knowledge → web_fallback. "
        "Decompose compound questions into separate tool calls. "
        "Cite [doc:id] for vector results and the SQL for table results."),
)
```

Your three storage halves (W6-02's map) become three tools; the routing rules from W6-04 become `system_prompt` lines the agent follows dynamically.

## 3. Multi-step reasoning: decompose → retrieve → synthesize

Compound questions ("compare the refund policy with actual refund volumes *this quarter*") need planning:

```python
DECOMPOSE_PROMPT = """Break this question into independent sub-questions, each answerable
by ONE tool. Return JSON: {"sub_questions": ["...", "..."]}

Question: {q}"""

def decompose(q: str) -> list[str]:
    return json.loads(llm.with_structured_output(Decomposition).invoke(q)).sub_questions
```

Two implementations of the same idea:

- **Agent-driven** (above): the model decomposes and calls tools itself — flexible, less predictable (W3-05)
- **Graph-driven** (W13's Self-RAG): decomposition, retrieval, grading, and synthesis as explicit nodes — the same capability with the control flow *pinned* (W13-01 §4's `add_conditional_edges`)

Ship the graph for known flows; the agent for open-ended tails — the W12-05 conclusion, now with both implementations built.

## 4. Self-improving: the feedback loop

```python
# 1. log every retrieval + outcome (W10-04 JSONL)
{"q": "...", "route": "vector", "hits": 5, "helpful": true, "miss_reason": null}

# 2. weekly analysis → retrieval config changes
#    - questions failing on vector → add BM25 weight / new synonyms (W4-04)
#    - repeated identical query → cache the answer (W15-04)
#    - new doc types appearing → update metadata filters (W5-03)

# 3. eval-set growth: every 👎 becomes a labeled case (W9-05 stretch)
```

Mechanisms that genuinely self-improve, ranked by honesty: **(a)** eval-set growth from logs (always real), **(b)** retrieval parameter/rule updates from failure analysis (real, human-in-loop), **(c)** query expansion few-shots updated from successful reformulations (real), **(d)** "the agent learns" (only with episodic memory + retraining — W16's fine-tuning, and still bounded).

## 5. Evaluation

- Routing accuracy on 25 mixed questions (three sources × intent types) — the W6-04 harness, agentic edition
- Faithfulness/relevancy (W5-05) on synthesized multi-source answers
- Trajectory metrics (W10-04): steps, decompositions, redundant retrievals
- **Regression**: the self-RAG graph from W13-01 must produce identical node paths on its eval set — your two implementations must not silently diverge

## Exercises

1. Build the three-source agent; run 25 routing cases; produce the routing-accuracy table vs the W6-04 rules and the W13 graph.
2. Decomposition probe: 5 compound questions; compare agent-decomposed sub-questions vs your hand decomposition. Score coverage.
3. Implement the feedback log + a weekly "failure report" (top miss reasons by route); propose one retrieval change per failure class.
4. Self-RAG graph parity: port the agent's routing rules into the W13-01 graph's conditional edges; run both on the harness — same answers?
5. Injection across sources: an attack embedded in a *web result* (web_fallback) — does the W3-02 delimiting hold when context comes from outside your corpus? (It must — W9-03's rule at web scale.)

## Pitfalls

- **"Self-improving" without eval sets** — improvements you can't measure are anecdotes; the JSONL→eval-set pipeline is the actual improvement mechanism
- **Router drift between implementations** — agent and graph versions diverge silently; run both on the same harness monthly
- **web_fallback as an escape hatch** — outside answers mixed with internal facts breaks grounding (W4-01); separate and label the source
- **Decomposition loss** — sub-questions that drop constraints ("this quarter") produce confidently wrong aggregates (W6-03's date rule per sub-question)
- **Tool description rot** — three sources, three descriptions, updated independently; version them together (W10-02)

## Resources

- LangChain [agentic RAG tutorials](https://python.langchain.com/docs/tutorials/) — routing + self-RAG in LCEL/LangGraph
- W13-01 (Self-RAG graph) + W6-04 (router) + W5-03 (fusion) — the composed prior work
- Anthropic, *Building effective agents* — the routing + evaluator-optimizer patterns formalized
- LangSmith [dataset/eval docs](https://docs.smith.langchain.com/) — where the feedback loop's eval sets live
