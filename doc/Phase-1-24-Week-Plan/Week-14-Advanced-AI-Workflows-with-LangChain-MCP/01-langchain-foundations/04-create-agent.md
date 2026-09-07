# create_agent — The Modern Agent API, Mapped

**What you'll learn:** `create_agent`: LangChain's modern agent factory —
model string, tools, `response_format`, middleware, checkpointer — and
the W10/W11 mapping that makes it legible.

## 1. The factory

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="openai:pinned-model-id",
    tools=[retrieve_tool, get_unit_text_tool],
    response_format=Answer,
    middleware=[my_retry_middleware],
    checkpointer=SqliteSaver.from_conn_string("data/checkpoints.db"),
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": query}]},
    config={"configurable": {"thread_id": "task-3"}},
)
result["structured_response"]     # Answer instance
```

| `create_agent` arg | W10/W11 equivalent |
|---|---|
| `model` string | the model wrapper + provider resolution |
| `tools` | the registry's schemas |
| `response_format` | W11 `output_type` (strict, same validators) |
| `middleware` | your fitter/retry/gate layers |
| `checkpointer` | W13 checkpointing (same API — it *is* LangGraph) |

The last row is the structural finding: `create_agent` returns a
LangGraph graph — your W13 week is the substrate, and the checkpoint/
interrupt/thread skills transfer 1:1.

## 2. Middleware — the cross-cutting layers, formalized

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse

class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3):
        super().__init__(); self.max_retries = max_retries

    def wrap_model_call(self, request, handler) -> ModelResponse:
        for attempt in range(self.max_retries):
            try:
                return handler(request)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                log_retry(attempt, e)
```

| Middleware | Replaces your... |
|---|---|
| retry (`wrap_model_call`) | the W10 retry policy |
| summarization | the fitter's history trim |
| human-in-the-loop | the gate interrupts (W13 file 06) |
| dynamic prompt | per-step context assembly |

Middleware is the SDK's extension seam — your W10 cross-cutting layers
(fitter, gates, logging) become middlewares. The port is mechanical
*because* they were written as separable policies.

## 3. Threads and memory (W13, one import away)

```python
config = {"configurable": {"thread_id": "eval-task-3"}}
r1 = agent.invoke({"messages": [{"role": "user", "content": q1}]}, config)
r2 = agent.invoke({"messages": [{"role": "user", "content": q2}]}, config)
# r2 continues r1's conversation — same thread_id
```

Sessions, checkpointing, and time travel from Week 13 all apply —
`create_agent` agents *are* LangGraph graphs. The memory-tier rules
(W10 file 02-03) and the fitter's budget carry over via middleware.

## 4. The mapping freeze (four frameworks, one table)

| Concept | W10 (yours) | W11 SDK | Agno | LangChain |
|---|---|---|---|---|
| loop | `run_react` | `Runner.run` | `Agent.run` | graph runtime |
| tools | registry | `@function_tool` | `@tool`/Toolkit | `@tool`/middleware |
| typed output | validators | `output_type` | `output_schema` | `response_format` |
| memory | fitter + list | sessions | db sessions | checkpointer+middleware |
| observability | harness | traces | AgentOS | LangSmith/streams |

## Exercises

1. Port your W11 agent to `create_agent`; run the battery; the outcome
   column must match W11's (the mapping table's proof).
2. Middleware drill: port the retry layer as middleware; verify the
   fault-injection test from W10 still catches failures through it.
3. Thread drill: multi-turn via `thread_id`; the W13 session drills
   re-run green.

## Pitfalls

- Middleware that swallows exceptions — retry middleware must re-raise
  on final failure; silent swallowing is the W10 anti-pattern.
- `response_format` on tool-heavy agents — the structured answer comes
  after the tools; verify the model's tool calls still fire (test it).
- Mapping freeze skipped — the fourth framework without a mapping table
  is four half-understood tools.