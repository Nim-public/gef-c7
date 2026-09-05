# Handoffs — Control Transfer, Descriptions, last_agent

**What you'll learn:** the SDK's native control-flow transfer: a handoff
is a tool call that swaps the active agent — the W10 "who writes the
if-statement" question, answered by the framework.

## 1. The mechanics

```python
from agents import handoff, Agent

router = Agent(
    name="Router",
    instructions="Route: charts → ChartAgent, exact terms → FtsAgent, else answer.",
    tools=[retrieve_tool],
    handoffs=[
        handoff(chart_agent, tool_description_override="Handle chart/table questions"),
        handoff(fts_agent,   tool_description_override="Handle exact codes and names"),
    ],
)

result = await Runner.run(router, "Which chart shows Q3 margin?")
print(result.last_agent.name)      # "ChartAgent" — control transferred
```

Under the hood, each handoff becomes a tool (`transfer_to_chart_agent`).
When the model calls it, the loop swaps to the target agent (documented
loop step 3) and `result.last_agent` names the agent that produced the
final answer.

## 2. The handoff description *is* the routing table

Your W9 regex router becomes a tool description — the model reads it the
way it reads any tool:

| W9 router element | Handoff equivalent |
|---|---|
| class detector (regex) | the model's reading of the description |
| route → pattern mapping | `tool_description_override` per handoff |
| default route | the router's own instructions + tools |
| miss logging | traces + `new_items` (the handoff call is visible) |

The porting discipline from W10 file 05 applies verbatim: write the
description, A/B it on misroutes, version it. The regex has become a
prompt — same maintenance loop, new medium.

## 3. input_filter and history nesting at transfer

```python
from agents.extensions.handoff_filters import remove_all_tools

handoff(chart_agent, input_filter=remove_all_tools)   # custom filters possible
```

At transfer, the conversation history moves with it — including
irrelevant tool noise from the router. `input_filter` cleans it (the
bundled filters remove tool calls/outputs; `nest_handoff_history` can
restructure the transcript instead). The W10 memory rule — *the model
sees the fit, not the raw store* — now applies at the agent boundary too.

## 4. Handoffs vs agents-as-tools (the design fork)

| Mechanism | Control | Best for |
|---|---|---|
| handoff | full transfer; one speaker at a time | specialist ownership (router→expert) |
| agent-as-tool (file 03) | delegation; results return to caller | subtasks inside one answer |

The test: *should the user's next message go to the specialist?* Yes →
handoff (dialogue ownership). No → agent-as-tool (delegation, answer
returns). Your capstone: router→specialists is a handoff; "compute
margin" as a helper is agent-as-tool.

## Exercises

1. Build the router with two specialist handoffs; run the three routing
   tasks from your W9 eval; verify `last_agent` per task matches the
   routing table.
2. Description A/B: misroute one query deliberately; rewrite the
   `tool_description_override`; re-run; log the fix (the W10 hint-AB
   loop, now on handoff descriptions).
3. Filter drill: inspect the history the specialist *sees* with and
   without `remove_all_tools`; measure the token delta — the transfer's
   context cost, now visible.

## Pitfalls

- Handoff descriptions that name *when* but not *what* — "handles
  follow-ups" is unreadable; "handles chart/margin questions with
  get_unit_text" routes.
- Forgetting that handoff targets' input guardrails don't run (W11 file
  01) — put corpus-scoped checks on tool guardrails instead.
- Handoff loops (A→B→A) — traces expose them; budget catches them; fix
  the descriptions that invite them.

## Resources

- SDK reference: `handoff()`, handoff filters, `last_agent` (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/04-failure-phrasing.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/04-failure-phrasing.md)
  — the A/B loop this reuses.