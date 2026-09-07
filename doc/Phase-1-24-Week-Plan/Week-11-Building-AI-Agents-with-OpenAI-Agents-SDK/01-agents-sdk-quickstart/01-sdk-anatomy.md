# SDK Anatomy — Agent, Runner, RunResult

**What you'll learn:** the three core objects, field by field, with the
Week-10 mapping that makes every SDK feature legible: you built each of
these by hand already.

## 1. The Agent object

```python
from agents import Agent

agent = Agent(
    name="RAG agent",                       # identity in traces
    instructions="...",                     # the constitution (W10 file 05)
    tools=[retrieve_tool, get_unit_text_tool],
    output_type=Answer | None,              # Pydantic final type (§3 here)
    handoffs=[specialist_agent],            # control transfer (W11 file 02)
    model="pinned-model-id",
    model_settings={"temperature": 0.0},
)
```

| Agent field | Your W10 equivalent |
|---|---|
| `instructions` | `SYSTEM` constitution string |
| `tools` | `ToolRegistry.schemas()` |
| `output_type` | your final-answer validation (citation audit) |
| `handoffs` | the router's route table |
| `model` / `model_settings` | `AGENT_CONFIG["model"]` |

## 2. The Runner and its documented loop

```python
from agents import Runner

result = await Runner.run(agent, query, max_turns=6, session=session)
# or sync:
result = Runner.run_sync(agent, query, max_turns=6)
```

The loop, as the SDK documents it (this *is* your `run_react`):

1. The agent is invoked with the input.
2. If there is a final output (type of `agent.output_type`), terminate.
3. If there is a handoff, re-run with the new agent.
4. Else, run tool calls and loop.

Exceptions: `MaxTurnsExceeded` when the turn limit trips; guardrail
tripwires raise their own typed exceptions — both are your W10 failure
paths, formalized.

## 3. The RunResult

```python
result.final_output            # final answer (typed if output_type set)
result.final_output_as(Answer) # typed accessor
result.last_agent              # who answered (handoffs change it)
result.new_items               # every item generated this run
result.input_guard_results / result.output_guard_results
result.raw_responses           # raw model responses (token accounting)
```

| RunResult field | Your W10 equivalent |
|---|---|
| `final_output` | `run_react` return `answer` |
| `last_agent` | nothing — your W10 agent had one agent; handoffs are new |
| `new_items` | your `trace` list |
| guard results | your gate/audit layer |

## 4. The field-by-field W10 mapping table

| W10 component | SDK primitive | Notes |
|---|---|---|
| `run_react` loop | `Runner.run` | 4 documented steps vs your while |
| `ToolRegistry` | `@function_tool` tools | schemas from signatures (file 02) |
| constitution string | `instructions` | same rules, same battery |
| citation audit | output guardrail | tripwire semantics (file 02) |
| trajectory store | tracing + your parquet | spans replace hand traces |
| fitter budget | manual (context mgmt) | sessions store history; trimming is yours |

The last row is the week's honest caveat: the SDK gives loop, tools,
persistence, tracing — *context fitting remains yours* (file 04 of W10
still applies).

## Exercises

1. Build the mapping table for *your* agent: every W10 component → SDK
   primitive or "manual, still mine". Any row you cannot map is a design
   decision to write down.
2. Run one query through `Runner.run_sync` with your tools; diff the
   `new_items` sequence against your W10 trace — the shapes differ, the
   semantics should match.
3. Anatomy quiz: from `RunResult` alone, reconstruct the trajectory's
   tool set and step count — what field did you need that wasn't there?

## Pitfalls

- Mapping `instructions` to a *system prompt template with placeholders*
  — instructions are static; dynamic context goes through input/context,
  not template tricks.
- Reading `final_output` as a string when `output_type` is set — it is
  your Pydantic object; parsing it as a string is a type bug.
- Assuming `last_agent` is always the starting agent — handoffs change
  it; downstream code must use the field.

## Resources

- OpenAI Agents SDK docs: agents, running_agents, result references
  (context7: `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/01-agent-definition.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/01-agent-definition.md)
  — the components being mapped.
