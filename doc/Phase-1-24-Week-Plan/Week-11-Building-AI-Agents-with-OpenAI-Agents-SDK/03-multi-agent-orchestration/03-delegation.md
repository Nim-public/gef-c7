# Delegation — Manager with Agents-as-Tools

**What you'll learn:** the third topology: a manager agent that calls
specialists *as tools* — results return to the caller, control never
transfers, and the manager stays the single voice. When this beats
handoffs, and what it costs.

## 1. The mechanism

```python
from agents import Agent, function_tool

# a specialist wrapped as a tool — the SDK's agents-as-tools pattern
chart_tool = chart_agent.as_tool(
    tool_name="answer_chart_question",
    tool_description="Answer a question about a chart/table. Input: the "
                     "question plus the unit_id. Returns Answer JSON.",
)

manager = Agent(
    name="Manager",
    instructions="Answer corpus questions. Use answer_chart_question for "
                 "chart/table details; cite unit_ids from its result.",
    tools=[retrieve_tool, chart_tool],
    output_type=Answer,
)
```

`as_tool` wraps the specialist's full loop (its own tools, its own
turns) behind one schema. The manager sees: name, description, and a
JSON result — the specialist's *intermediate* turns stay inside the
tool's span.

## 2. Handoff vs delegation: the fork, formalized

| Property | Handoff | Agent-as-tool |
|---|---|---|
| Who talks to the user next | the specialist | the manager |
| Specialist's intermediate steps visible in main history | yes | no (nested in span) |
| Specialist output | becomes the run's output | a tool result the manager uses |
| Session continuity | specialist owns it | manager keeps it |
| Trace shape | flat, agent switches | nested spans |

The fork test, from W11 file 02: *should the user's next message go to
the specialist?* Dialogue ownership → handoff. Answer-factories →
delegation. Your capstone: the answerer is a factory (manager keeps
citing); a future "deep analysis" mode might be a handoff (it owns the
conversation).

## 3. The cost model — nesting is not free

| Run shape | Model calls | Where it shows |
|---|---|---|
| manager answers directly | 1 | flat |
| manager → tool-specialist (3 internal turns) | 4 | one tool span, nested turns |
| manager → two specialists sequentially | 7 | spans nest per call |

```python
def delegation_cost(p_delegate: float, inner_turns: float, outer_overhead: int) -> float:
    direct = outer_overhead
    delegated = outer_overhead + inner_turns * 900   # per-turn tokens
    return (p_delegate * (delegated - direct)) / direct
```

Delegation multiplies turns silently — the nested span hides them from
naive step counters. The harness (file 05) must read *nested* spans; the
ledger must count inner turns, or specialists look free.

## 4. Design rules for the manager

| Rule | Why |
|---|---|
| manager's instructions describe *when* to delegate | the tool description covers *what* |
| specialists share the typed `Answer` | the manager's citations stay verifiable |
| manager never duplicates a specialist's tools | two paths to one capability = drift |
| inner budgets per specialist tool | a specialist loop is a cost bomb without one |

The last rule ports your W10 episode budget into the delegation layer:
each agent-as-tool gets `max_turns` in its wrapper, and the manager's
budget is the *outer* bound.

## Exercises

1. Wrap the answerer as a manager tool; run 5 queries through manager vs
   direct answerer; compare tokens and success — the delegation tax,
   measured.
2. Nesting-visibility drill: run a delegated query; count model calls in
   the trace (nested spans) vs the naive step counter — the measurement
   gap, demonstrated.
3. Budget-inheritance drill: give the specialist wrapper `max_turns=3`;
   force an inner loop; verify the wrapper stops and returns a degraded
   result the manager can report honestly.

## Pitfalls

- Delegating to a specialist that hands off back — nested handoffs inside
  agent-as-tool create control-flow spaghetti; specialists inside tools
  must be terminal.
- Manager instructions that re-describe the tool's job — one description
  per surface; the manager says *when*, the tool says *what*.
- Counting nested turns as one step — the harness reads spans; naive
  counters undercount cost by the nesting factor.

## Resources

- SDK agents-as-tools (`Agent.as_tool`) reference (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/01-trajectory-instrumentation.md)
  — the store the nested spans feed.