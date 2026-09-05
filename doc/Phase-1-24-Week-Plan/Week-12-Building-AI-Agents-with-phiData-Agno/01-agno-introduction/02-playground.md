# Playground & AgentOS — UI, Run History, Tool Inspection

**What you'll learn:** the UI layer Agno gives you: the classic
Playground and the newer AgentOS — what each shows (runs, tool calls,
metrics), how to serve it, and where its observability ends.

## 1. Serving agents with a UI

```python
from agno.playground import Playground

app = Playground(agents=[rag_agent, analytics_agent]).get_app()
# uvicorn playground:app --reload  → http://localhost:7777

# the newer surface:
from agno.os import AgentOS
agent_os = AgentOS(agents=[rag_agent])
app = agent_os.get_app()
agent_os.serve(app="demo:app", port=9001)
```

| Surface | What it gives you | Capstone use |
|---|---|---|
| Playground | chat UI, run history, tool-call inspection per message | interactive debugging, demo day |
| AgentOS | FastAPI app + config endpoint + REST/stream clients | programmatic access (Week 10's tool contract) |

The Playground replaces your Week-09 Gradio explorer for *agent* demos —
run history and per-run tool inspection are built in. Your Gradio app
remains the *corpus* explorer; the Playground is the *agent* console.

## 2. What the run history shows

| Panel | Content | W10 equivalent |
|---|---|---|
| messages | user/assistant turns | history tier |
| tool calls | name, args, result per call | registry audit |
| metrics | tokens in/out, duration | fitter ledger |
| session | persisted across runs | `SQLiteSession` |

Everything the trajectory store captured is visible interactively —
which is the fastest debugging loop in the program: query → run → click
the tool call → read the args. The export path (to parquet) is still
yours for the scorecards; the Playground is the *interactive* half.

## 3. The limits — where the UI ends

| Need | Playground answer | Your answer |
|---|---|---|
| regression gates | no | the W11 suites (pytest) |
| metric trends | live view only | trajectory parquet + tables |
| guardrail tripwire forensics | visible in run | your post-mortem workflow |
| eval set scoring | not built | the W10-04 harness |

The division of labor is the same as Week 09: the UI is for *looking*,
the harness is for *knowing*. A demo built only on the Playground has no
regression story; a harness with no UI has no demo story. You have both.

## 4. Serving patterns (local → shared)

```python
# local dev:  playground.serve / agent_os.serve (reload=True)
# shared:     FastAPI app behind uvicorn on your host (W9-01 deployment file)
# API:        AgentOSClient(base_url="http://localhost:9001")
```

The AgentOSClient gives a typed client over the served app — the same
role your Gradio `api_name` endpoints played in W9-01. The tool contract
page (W9-05) gains one row: the Playground's REST surface is a *third*
consumer of the same handlers (UI, API, agent).

## Exercises

1. Serve your ported agent in the Playground; run the 10-task eval
   manually; click through one tool call per run — the interactive
   validation of what the traces captured.
2. Boundary drill: name three debugging tasks the Playground cannot do
   that your harness can (regression gate, parity test, taxonomy) — the
   UI/harness division, written down.
3. Client drill: connect `AgentOSClient` to the served agent; call your
   retrieval tool; verify the response matches the tool contract schema.

## 5. The UI strategy (three consoles, one store)

| Console | Shows | Store role |
|---|---|---|
| Gradio explorer (W9) | corpus units, metadata | read-only over parquet |
| Playground/AgentOS | agent runs, tool calls | interactive view of traces |
| Your harness tables | metrics, regressions | the analysis surface |

Three consoles, one trajectory store — the strategy is that every UI is
a *projection* of the store, never a second copy. The drills above are
what keep that promise honest: the UI's runs must agree with the store's
rows on the same queries, or one of them is lying.

## Pitfalls

- Playground as the system of record — it is a console; the store is the
  record.
- Publicly serving a Playground bound to your corpus — the deployment
  rules from W9-01 apply (secrets, queue limits, auth).
- Demoing tool inspection without `show_tool_calls=True` — the flag is
  the feature; check it before the review.

## Resources

- Agno Playground + AgentOS docs (context7: `/agno-agi/docs`).
- [`../../Week-09-RAG-with-Image-Video-Audio/01-gradio-multimodal-apps/04-deployment-patterns.md`](../../Week-09-RAG-with-Image-Video-Audio/01-gradio-multimodal-apps/04-deployment-patterns.md)
  — the deployment checklist this extends.