# 01 — OpenAI Agents SDK Quickstart

> Week 11 index: [README.md](README.md)

**Session 1 topics:** *Introduction to OpenAI Agents SDK: What it is, use cases, real-world agentic workflows. Core agent components: Agents, tools, handoffs, guardrails, runners, sessions. Environment setup for agent development (Python SDK, authentication, and quickstart). Anatomy of a basic agent: models, prompts, state/memory, minimal tool use. Agent communication and workflow: conversation history, multi-turn dialogues. Tracing and debugging with built-in SDK tools.*

---

## What you'll learn

- What the SDK is — and what each of its six primitives maps to from Week 10
- The `Agent` → `Runner.run` anatomy, including the loop you hand-wrote
- Sessions for multi-turn memory; tracing for debugging
- Where models/prompts/state live in SDK objects

## 1. What the SDK is

The OpenAI Agents SDK is a small Python framework around the loop you built in W10-01, with five primitives: **Agents** (LLM + instructions + tools), **handoffs** (agent-to-agent transfer), **guardrails** (input/output checks with tripwires), **sessions** (memory), and **tracing** (observability). It is model-agnostic (works over the Chat Completions protocol you know from W1) and provider-flexible (LiteLLM integration for 100+ providers).

The mapping from your hand-rolled loop — keep this table beside you all week:

| Your W10 code | SDK primitive |
|---|---|
| `run_agent()` loop (invoke → final? → tools → repeat) | `Runner.run()` — same 4 steps, verbatim |
| `max_steps` | `max_turns` (raises `MaxTurnsExceeded`) |
| `ToolRegistry` + schemas | `@function_tool` / `mcp_servers=[]` |
| forced "FINAL:" convention | `output_type` (structured final output) |
| history list | `Session` (e.g., `SQLiteSession`) |
| W3-02 injection battery | `input_guardrails` tripwires |
| W10-04 JSONL trace | built-in tracing (dashboard/local file) |

## 2. Quickstart: agent → run → result

```powershell
pip install openai-agents
```

```python
from agents import Agent, Runner

agent = Agent(
    name="Capstone assistant",
    instructions="Answer capstone questions concisely; cite sources when you have them.",
    model="gpt-4o-mini",
)

result = Runner.run_sync(agent, "What is RAG in two sentences?")
print(result.final_output)
```

`Runner.run_sync` wraps the async loop; the async form is `await Runner.run(...)` (production services should use async — W11-04's voice stack requires it). The loop per the SDK's own docs: **(1)** invoke the agent **(2)** if the output matches `agent.output_type`, done **(3)** if the agent *hands off*, continue with the new agent **(4)** else run tool calls and repeat — raising `MaxTurnsExceeded` or a tripwire exception when limits hit.

## 3. Anatomy of an Agent object

```python
from agents import Agent, ModelSettings

agent = Agent(
    name="Capstone assistant",             # identity in traces/handoffs
    instructions="...",                    # the W3-02 constitution → system prompt
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.2, max_tokens=800),
    tools=[],                              # @function_tool list (W11-02)
    mcp_servers=[],                        # your W10-03 FastMCP server
    handoffs=[],                           # other Agents (W11-02/03)
    output_type=None,                      # a Pydantic model → structured final output
    input_guardrails=[], output_guardrails=[],   # W11-02
)
```

Everything from the program so far has a slot: `instructions` is your constitution (W10-05), `tools`/`mcp_servers` are the registry (W10-02/03), `model_settings` is W1-07's sampling, `output_type` replaces the `FINAL:` convention with a *typed* contract:

```python
from pydantic import BaseModel

class Answer(BaseModel):
    answer: str
    citations: list[str]
    confidence: str      # low|medium|high — the W5-04 hook, now enforced by schema

agent = Agent(name="Capstone assistant", instructions="...",
              output_type=Answer)
result = Runner.run_sync(agent, "refund timeline?")
print(result.final_output.citations)     # parsed, validated — no regex scraping
```

## 4. Sessions: multi-turn memory (W1-07/W10-02, built-in)

```python
from agents import SQLiteSession

session = SQLiteSession("user_42", "agent_memory.db")

result1 = Runner.run_sync(agent, "What is the refund timeline?", session=session)
result2 = Runner.run_sync(agent, "And for cancelled plans?", session=session)
# result2 sees turn 1 — the session persists history automatically
```

`SQLiteSession` stores per-conversation history in a local DB; the same session id resumes context. This is W10-02's *history* row of the memory taxonomy — scratchpad/episodic memory remain yours to build (tools + stores, exactly as Week 10 taught).

## 5. Tracing: see the loop

Every run emits a **trace** with **spans** (LLM generation, tool execution, handoffs, guardrails):

```python
from agents import set_tracing_disabled
# tracing is ON by default (requires OPENAI_API_KEY);
# inspect at https://platform.openai.com/traces, or export locally:
```

```python
with agents.trace("eval-run-17"):
    result = Runner.run_sync(agent, task_input)
# W11-05 reads spans programmatically for the eval harness
```

Your W10-04 JSONL habit and the SDK's traces are the same information at different fidelity — W11-05 shows how to join them.

## 6. Real-world workflow shapes (the "use cases" mapped)

| Workflow | Primitives | Program hook |
|---|---|---|
| Single agent + tools | Agent, tools | W10-01's loop, SDK edition |
| Router → specialists | handoffs | W11-02/03; your capstone triage |
| Guarded intake | input guardrails | W3-02 battery, tripwires |
| Structured extraction | output_type | W5-05/W6-03 formatted outputs |
| Long-running conversations | sessions | support bot (W3's task) |
| Tool-heavy enterprise actions | function tools + HITL gates | W10-04's approval pattern |

## Exercises

1. Quickstart end-to-end: agent + structured `output_type` on 5 capstone questions; print `final_output` fields and the trace URL. What does the trace show for a *no-tool* run?
2. Session continuity: 5-turn conversation in one `SQLiteSession`; between turns, open the DB file — where does history live? Then `session.clear_session()` and verify amnesia.
3. Loop mechanics: give the agent a tool and a task that needs 2 calls; set `max_turns=2` — catch `MaxTurnsExceeded` and print the partial trace. Match each span to a W10-01 loop line.
4. Instructions as constitution: port your W10-05 constitution into `instructions`; re-run the W10 injection battery (the SDK has no guardrails yet — does the constitution alone hold? Record for file 02).
5. Model swap: run the same task with `gpt-4o-mini` and a local model via LiteLLM/Ollama (W2-05) — same trace structure? What differs in spans?

## Pitfalls

- **Sync calls in async contexts** — mixing `run_sync` inside an async app deadlocks; pick one mode per service
- **`instructions` treated as a system prompt footnote** — it's the constitution; W10-05's rules apply verbatim
- **Sessions without eviction** — unbounded history per session id (W1-07 trimming still applies conceptually; check the session's growth)
- **Tracing off in prod without a plan** — you lose the debugging surface that W11-05 depends on; disable deliberately, not silently
- **Expecting the SDK to validate tool *behavior*** — it routes calls; your W10-02 validators remain the walls

## Resources

- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) — quickstart, agents, running agents, sessions
- [Tracing guide](https://openai.github.io/openai-agents-python/tracing/) — spans, processors, external exporters
- W10 files 01/02/05 — your implementation of what the SDK wraps
- OpenAI Cookbook, agentic patterns examples
