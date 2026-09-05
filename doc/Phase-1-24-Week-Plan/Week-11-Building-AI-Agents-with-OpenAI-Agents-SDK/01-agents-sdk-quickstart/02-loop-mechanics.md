# Loop Mechanics — The Four Documented Steps, max_turns, Handlers

**What you'll learn:** the SDK's loop in precise terms — what a *turn*
is, where the two exception paths fire, and how `error_handlers` gives
your degradation ladder a native slot.

## 1. A turn, defined

One turn = one model invocation **including its tool calls**. Your W10
"step" was the same unit; the SDK just names it. The loop:

```text
1. invoke model with current items
2. final output? → terminate
3. handoff?      → swap agent, loop
4. tool calls?   → execute all, loop
```

Consequences worth internalizing: a model call that emits 3 tool calls is
*one* turn; a handoff does not consume extra turns by itself but the new
agent's invocations do; `max_turns=6` therefore bounds *model invocations*,
not user-visible steps.

## 2. The two exception paths, handled natively

```python
from agents import Agent, Runner, RunErrorHandlerInput, RunErrorHandlerResult

def on_max_turns(_data: RunErrorHandlerInput) -> RunErrorHandlerResult:
    return RunErrorHandlerResult(
        final_output="I couldn't finish within the turn limit. "
                     "Please narrow the request.",
        include_in_history=False,        # don't poison the session
    )

result = Runner.run_sync(agent, query, max_turns=6,
                         error_handlers={"max_turns": on_max_turns})
```

| Exception | Raised when | Native handling |
|---|---|---|
| `MaxTurnsExceeded` | turns > max_turns | `error_handlers["max_turns"]` fallback |
| `InputGuardrailTripwireTriggered` | input guardrail fires | your except clause |
| `OutputGuardrailTripwireTriggered` | output guardrail fires | your except clause |

The W10 degradation ladder maps 1:1: budget stop → `MaxTurnsExceeded`
handler; gate/audit failures → guardrail tripwires. The `final_output`
fallback even replaces your `"budget exhausted"` string — with
`include_in_history=False` solving the history-poisoning bug you handled
by hand.

## 3. Only the first agent's input guardrails run

The SDK documents that input guardrails run on the *starting* agent only
— handoff targets' input guardrails do not re-run. The capstone rule:
put corpus-scoped input validation on the router (the first agent), and
per-specialist checks on *tool* input guardrails (file 02), which fire at
every tool call regardless of which agent holds control.

```text
router (input guardrail ✓ runs once)
  └─ handoff → specialist (input guardrail ✗ skipped)
       └─ tools (tool_input_guardrails ✓ run every call)
```

## 4. Streaming, hooks, and the run config you will actually set

```python
result = Runner.run(agent, query, run_config=RunConfig(
    workflow_name="gef-c7-rag",          # trace grouping
    trace_metadata={"tool_surface": "v1", "constitution": "cv1"},
))
```

`RunConfig` carries what your `AGENT_CONFIG` did: workflow naming for
traces, metadata for attribution. `RunHooks` gives lifecycle callbacks
(run start/end, agent switches) — the seam for shadow-mode logging
(W10 file 04) without touching the loop.

## Exercises

1. Turn-accounting drill: with a canned model emitting (a) 1 tool call,
   (b) 3 parallel calls, (c) 2 calls + handoff — predict the turn counts,
   then verify against `RunResult`.
2. Handler drill: set `max_turns=2` on a task that needs 3; verify the
   fallback fires, `include_in_history=False` keeps the session clean,
   and your trajectory row says `degraded`.
3. Guardrail-placement drill: put an input guardrail on a handoff target
   and send a violating input through the router — document that it does
   not fire, then move the check to a tool guardrail and confirm it does.

## Pitfalls

- Counting tool calls as turns — a turn is the model invocation; the
  budget you tuned in W10 translates 1:1 but the naming differs.
- Catching tripwires with a bare `except Exception` — the exception types
  carry the guardrail + results; catching broadly loses the payload.
- Setting `max_turns=None` "to be safe" — an unbounded agent is an
  unbounded bill; the handler + budget is the pair.

## Resources

- SDK reference: `Runner.run`, `RunResult`, `RunConfig` (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/02-hand-rolled-react.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/02-hand-rolled-react.md)
  — the loop this formalizes.
