# 01 — Agno (phiData) Introduction

> Week 12 index: [README.md](README.md)

**Session 1 topics:** *Deploying phiData and defining agent structures. Exploring the built-in phiData playground.*

---

## What you'll learn

- What Agno/phiData is and where it sits against your W10/W11 implementations
- Agent structure in Agno: model, instructions, tools, knowledge, storage
- Running agents: `print_response`, streaming, and the web playground
- The framework-mapping table you've been building since W10

## 1. What Agno/phiData is

Agno (formerly **phiData**) is a batteries-included agent framework: same primitives as the OpenAI Agents SDK (W11) plus built-in **knowledge bases** (RAG with pluggable vector DBs), **storage/memory**, prebuilt **toolkits** (search, finance, SQL, …), an **agent UI/playground**, and **teams** (multi-agent, previewed for W13's crew work).

Against your timeline: W10 = the loop by hand; W11 = lean primitives; **W12 = the loop + batteries**; W13 = explicit graph control.

## 2. First agent

```powershell
pip install agno openai
```

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You are the capstone assistant.",
        "Answer concisely; cite sources when tools provided them.",
        "If unsure, say so — never invent capstone facts.",
    ],
    markdown=True,
)

agent.print_response("What is RAG in two sentences?", stream=True)
```

The Agent fields map directly onto concepts you own:

| Agno field | Your concept |
|---|---|
| `instructions` | the W3-02/W10-05 constitution |
| `tools=[...]` | W10-02's registry (framework executes + feeds observations) |
| `knowledge=...` + `search_knowledge=True` | RAG (W4) as a built-in tool |
| `add_history_to_context=True, num_history_runs=5` | W1-07 history trimming, prebuilt |
| `markdown=True` | output formatting contract (W3-01) |

## 3. The playground

```powershell
pip install "agno[playground]"
```

```python
# playground.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground

assistant = Agent(name="Capstone assistant", model=OpenAIChat(id="gpt-4o-mini"),
                  markdown=True)

app = Playground(agents=[assistant]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground.py", port=7777)
```

```powershell
ag app          # starts the playground UI pointed at your server
```

What the playground gives you: chat UI, **run history**, tool-call inspection, session management — the W10-04 observability story with a UI. What it hides: the loop internals (your W10 knowledge is what lets you read its behavior critically).

*(Verify the current CLI — Agno renames tooling occasionally; the docs' quickstart is authoritative.)*

## 4. Agent structures: the framework's opinion

Agno encourages composable structure — an agent's powers are *assembled*:

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[...],                  # constitution (W3)
    tools=[YFinanceTools(), custom_toolkit],  # capabilities (W10-02)
    knowledge=knowledge,                 # RAG (file 02 this week)
    search_knowledge=True,
    storage=SqlAgentStorage(table_name="agent_sessions", db_file="tmp/agents.db"),
    add_datetime_to_context=True,        # the model has no clock (W6-03 lesson!)
    add_history_to_context=True,
    num_history_runs=3,
)
```

The framework's contribution vs W11: **declarative assembly** — you declare what the agent has, it wires schemas, execution, history, and observability. The contribution vs your W10 loop: prebuilt integrations (vector DBs, toolkits) you'd otherwise write (W10-02's registry becomes configuration).

## 5. The mapping table (complete it — it's your W13/W14 anchor)

| Concept | W10 hand-rolled | W11 OpenAI SDK | W12 Agno |
|---|---|---|---|
| Agent definition | messages + loop | `Agent(...)` | `Agent(...)` |
| Loop | your `for` + FINAL | `Runner.run` | framework-internal |
| Tools | `ToolRegistry` | `@function_tool` | toolkit classes / plain functions |
| RAG | your W4/W9 stack | via tools/MCP | `Knowledge` + `search_knowledge=True` |
| Memory | history + scratchpad (W10-02) | `Session` | `storage` + `add_history_to_context` |
| Tracing | JSONL (W10-04) | traces | playground/logs |
| UI | none/Gradio (W9-01) | none | **playground** |

## Exercises

1. Build the first agent; ask 3 capstone questions with `stream=True`. What does streaming change about perceived latency (W1-07)?
2. Port your W10-05 constitution into `instructions` (as a list of rules). Run the W10 injection battery — does Agno's loop + constitution hold without guardrails? Record for file 06.
3. Add `add_datetime_to_context=True` and ask "orders from last month" — compare with the W6-03 date-handling problem you solved manually.
4. Run the playground; use the tool-call inspector on a tool-using answer. Which span information from W11-05 traces appears here?
5. Complete the mapping table's last row for *observability*: playground vs SDK traces vs your JSONL — what can you debug in each?

## Pitfalls

- **phidata vs agno confusion** — old tutorials use `from phi.agent import Agent`; current package is `agno`. Pin the version you learn against.
- **Playground as the only observability** — a UI without exported logs can't feed W16 evals; keep the W10-04 JSONL habit
- **Knowledge/search flags set but no knowledge configured** — silent no-op; verify a retrieval actually fires
- **Framework defaults ≠ your eval settings** — temperature/model defaults drift from your W10-04 baseline; pin everything you measure
- **One agent, all tools** — Agno makes assembly easy; the least-privilege rule (W10-04) still applies per agent

## Resources

- [Agno docs](https://docs.agno.com) — agents, knowledge, tools, playground (current API source)
- Agno examples repo — knowledge + LanceDB + toolkit walkthroughs (this file's snippets follow them)
- W10-01/02 and W11-01 — the mapping table's other columns
- [GitHub: agno-agi/agno](https://github.com/agno-agi/agno) — changelogs for the phiData→Agno rename
