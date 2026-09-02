# 01 — LangChain Foundations: Templates, LCEL, Structured Output, Agents

> Week 14 index: [README.md](README.md)

**Session 1 topics:** *What is LangChain. Building Blocks: Prompt Templates, Different Types of Chains, Agents.*

---

## What you'll learn

- The LCEL composition model — the `|` operator and what it standardizes
- Prompt templates as versioned, tested artifacts (W3-02's file-based prompts, framework edition)
- Structured output (Pydantic-validated chains)
- The modern `create_agent` API and when to reach for it

## 1. What LangChain is (after five weeks of context)

LangChain is the **integration and composition layer**: model providers, vector stores, document loaders, and tools behind one interface, composable via LCEL (LangChain Expression Language). By now you've hand-built everything it packages — W3 prompts, W4 RAG, W10 loops, W11 agents — so this week is about *mapping*, not new concepts.

| Your concept | LangChain primitive |
|---|---|
| f-string prompts (W1/W3) | `ChatPromptTemplate` |
| chained calls (W3-01) | LCEL `|` pipelines |
| `output_type` JSON contracts (W11) | `with_structured_output(Pydantic)` |
| W10-01 loop / W11 `create_agent` | `create_agent` (LangGraph-powered) |
| W10-03 MCP server | `langchain-mcp-adapters` (file 05) |
| W4 retrievers | `VectorStoreRetriever`, loaders |

## 2. Prompt templates

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are the capstone analyst. Answer ONLY from the provided context."),
    ("user", "Context:\n{context}\n\nQuestion: {question}"),
])

filled = prompt.invoke({"question": "What is the refund timeline?", "context": "..."})
print(filled.to_messages())        # the rendered messages — inspectable, testable
```

Rules carried over from W3-02, unchanged: templates live in files/git, no secrets, delimit untrusted data, and *validate rendered output* (`.invoke` raises on missing variables — better than f-string's silent `None`).

## 3. LCEL: chains as pipelines

The `|` operator composes runnables; every stage supports streaming, batching, async, retries, and fallbacks uniformly:

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm | StrOutputParser()

print(chain.invoke({"question": "...", "context": "..."}))
```

Chain patterns you'll use this week:

```python
# sequential stages (W3-01's chaining, LCEL edition)
summarize = summary_prompt | llm | StrOutputParser()
analyze   = analysis_prompt | llm | StrOutputParser()
pipeline  = {"summary": summarize, "question": RunnablePassthrough()} | analyze

# structured output — Pydantic validation in the pipeline (W5-04's guards, built in)
from pydantic import BaseModel, Field

class Triage(BaseModel):
    category: str
    urgency: str
    reasoning: str

triage_chain = triage_prompt | llm.with_structured_output(Triage)
verdict = triage_chain.invoke(...)          # returns a validated Triage object

# fallbacks + retries at the composition level
robust = triage_chain.with_retry(stop_after_attempt=2).with_fallbacks([backup_chain])
```

`.with_retry` / `.with_fallbacks` are the W10-04 reliability practices as one-liners — and file 15-01 stress-tests them.

## 4. Structured output

```python
from pydantic import BaseModel, Field

class ProductReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    sentiment: str
    key_points: list[str]

review_chain = llm.with_structured_output(ProductReview)
review_chain.invoke("Analyze this review: 'Great product, 5 stars, fast shipping'")
# ProductReview(rating=5, sentiment='positive', key_points=['fast shipping'])
```

Validated Pydantic objects replace W6-03's hand-rolled JSON parsing — same contract, library-enforced. The agent API extends this: `create_agent(..., response_format=ToolStrategy(Schema))` or `ProviderStrategy` for structured *agent* outputs.

## 5. `create_agent` — the modern agent

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather],
    system_prompt="Use tools for facts; answer concisely.",
)

result = agent.invoke({"messages": [{"role": "user", "content": "Weather in Pune?"}]})
print(result["messages"][-1].content)
```

`create_agent` is the W10 loop with the W11 ergonomic surface — and it's built on **LangGraph** under the hood (W13-01's graph, generated for you). Custom tools are plain functions with docstrings (W10-02's rules); MCP servers attach via adapters (file 05).

## 6. Which LangChain layer for which job

| Need | Reach for |
|---|---|
| one prompt + parse | `ChatPromptTemplate | llm | Pydantic` |
| multi-step fixed flow | LCEL sequence (with fallbacks/retries) |
| tool-using assistant | `create_agent` |
| explicit branching/loops | **LangGraph directly** (W13 — LangChain agents compile to it) |
| your existing validated code | wrap as a tool; don't rewrite |

## Exercises

1. Port your W10-05 constitution into a `ChatPromptTemplate` file-loaded chain; run the W3-02 injection battery through it. What does LangChain add to the template workflow (variables, validation)?
2. Build the triage chain with `with_structured_output`; break it (feed a 10k-char ticket) and add `.with_retry` + a fallback chain. Show the recovery.
3. LCEL streaming: `for chunk in chain.stream(...)`: — compare with W1-07's manual streaming loop.
4. Re-implement W10-01's agent with `create_agent` + your two tools; run the W10 10-task suite. Table: LOC, success, tokens.
5. Map your W11-03 orchestration patterns (handoff/chaining/delegation) onto LangChain primitives — which maps cleanly, which fights the framework?

## Pitfalls

- **LCEL opacity** — a long `|` chain hides failure stages; name and test each segment (W3-01's seam rule)
- **Template variable collisions** — `{}` in JSON examples inside templates needs escaping; same f-string lesson (W3-01)
- **`with_structured_output` swallowing retries** — pair with `.with_retry`; validation errors are retryable
- **Agent for fixed pipelines** — LCEL chains *are* your pipeline; agents add nondeterminism (W3-05)
- **Version churn** — LangChain's API moves fast (the agent API regenerated recently); pin versions, read the current docs (this file follows the current `create_agent` API)

## Resources

- [LangChain docs](https://docs.langchain.com/oss/python/langchain/overview) — quickstart, prompts, structured output, agents
- [LCEL concepts](https://python.langchain.com/docs/concepts/lcel/) — runnables, streaming, fallbacks
- LangSmith docs (file 15-02's tracing layer)
- W3-01/02 + W10-02/05 — everything being mapped here
