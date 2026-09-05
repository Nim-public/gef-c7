# Agent Definition — Loop, Tools, Memory, Control-Flow Transfer

**What you'll learn:** the one-line definition that separates agents from
every pipeline you have built, the four components every agent has, and
the vocabulary the rest of the program uses.

## 1. The definition

> **An agent is a system where an LLM decides the control flow of tool
> calls at runtime.**

The single test: *who writes the if-statement?* In a pipeline, you wrote
it (`if route == "P1": ...`); in an agent, the model writes it, per
query, as tool-call decisions. Everything else — memory, planning,
reflection — is an extension of this one transfer.

## 2. The four components, minimally

| Component | Minimal form | Grows into |
|---|---|---|
| Loop | `while not done: llm(tools, history)` | budgets, reflection, replanning |
| Tools | dict of name → callable (+ schema) | MCP servers (file 03) |
| Memory | the message list | scratchpad, episodic, semantic (file 02) |
| Stop policy | max steps + no-tool-call | budget + goal checks, HITL gates |

```python
def run_agent(query: str, tools: dict, max_steps: int = 6) -> dict:
    history = [{"role": "user", "content": query}]
    for step in range(max_steps):
        resp = llm(messages=history, tools=list(tools.values()))
        if not resp.tool_calls:                      # model chose to answer
            return {"answer": resp.content, "steps": step + 1}
        for call in resp.tool_calls:                 # model chose control flow
            obs = tools[call.name](**call.args)
            history.append(tool_result(call, obs))
    return {"answer": "budget exhausted", "steps": max_steps, "degraded": True}
```

Twenty lines contain the whole paradigm: the model's two choices per step
(*answer* or *call tools*) *are* the control flow transfer.

## 3. What the transfer buys — and costs

| Property | Pipeline | Agent |
|---|---|---|
| Query routing | your router (W9 file 05) | model's choice, per step |
| Multi-hop (search → read → compute) | explicit DAG you wrote | emergent from tool descriptions |
| Predictability | high (traceable DAG) | trajectory distribution |
| Cost per query | fixed | variable (steps × tokens) |
| Failure surface | your branches | tool misuse, loops, injection (W9 battery) |

The trade is concrete: the agent deletes your router code and adds a
metrics harness (file 04) because you no longer know the path in advance.

## 4. Vocabulary fixed now (used in every later week)

- **Trajectory**: the full sequence (thought, tool call, observation)ᵏ.
- **Step**: one loop iteration (one model call + tool executions).
- **Tool contract**: schema + error semantics (Week 09's shape).
- **Episode budget**: max steps/tokens before forced stop.
- **HITL gate**: a step that pauses for human approval (file 04).

## Exercises

1. Convert your Week-09 router into a 4-tool agent definition (retrieve_p1,
   retrieve_p2, answer_p1, answer_vlm) — write the schemas, not the code.
2. Trace by hand: for "what does the revenue chart show", write the
   trajectory your agent *should* produce (2 steps), then the one it
   would produce with a vague tool description (4+ steps).
3. Find one capstone query where the fixed DAG beats the agent, and one
   where the agent wins — the pair that frames file 04's boundary.

## Pitfalls

- Calling every LLM app an agent — without control-flow transfer it is a
  pipeline with extra steps (costly, less predictable).
- Unbounded loops without a budget — `max_steps` and token caps are not
  optional; they are the degradation ladder's trigger.
- Tool descriptions written for you, not for the model — the model *is*
  the router now; descriptions are its routing table.

## Resources

- ReAct (Yao et al. 2022) §2; your Week-09 tool contract.
- Anthropic "Building effective agents" — the workflow-vs-agent boundary,
  stated the same way.
