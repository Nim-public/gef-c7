# 03 — Multi-Agent Orchestration Patterns

> Week 11 index: [README.md](README.md)

**Session 2 topics:** *Orchestrating multi-agent workflows: agent handoffs, chaining, and delegation patterns.*

---

## What you'll learn

- The three orchestration patterns (handoff, chaining, delegation) with SDK code
- A decision table for choosing patterns — and how they preview LangGraph (W13)
- State passing between agents; context scoping rules
- Anti-patterns: the loops, spirals, and ping-pongs multi-agent systems die of

## 1. The three patterns

| Pattern | Control flow | SDK mechanism | Analogy from your stack |
|---|---|---|---|
| **Handoff** (router→specialist) | model *transfers* control; one active agent at a time | `handoffs=[...]` | W6-04's router, but the LLM decides |
| **Chaining** (pipeline) | fixed sequence A→B→C; each refines | sequential `Runner.run`s | W4's ingestion pipeline; W3-01's prompt chaining |
| **Delegation** (manager) | orchestrator agent *calls* worker agents as tools; keeps control | agents wrapped as `function_tool`s | W14's CrewAI-style crews, miniaturized |

### Handoff (from file 02, revisited as a pattern)

```python
triage = Agent(name="Triage", instructions="Route only.", handoffs=[rag_agent, sql_agent])
# one active agent; result.last_agent tells you who finished
```

Use when: distinct expertise/domains, mutually exclusive question types, least-privilege scoping. Costs: context handoff is *all-or-nothing* (the whole history moves), routing errors are user-visible.

### Chaining

```python
async def chained(question: str) -> dict:
    plan    = await Runner.run(planner_agent, question)
    research = await Runner.run(rag_agent, plan.final_output)
    compose  = await Runner.run(writer_agent, f"Q: {question}\nFindings: {research.final_output}")
    return compose.final_output
```

Use when: stages are known and ordered (like your RAG pipeline — but with LLM-quality transforms between). Costs: latency stacks; errors propagate (validate at the seams — W3-01's chaining rules, unchanged). Deterministic control flow = testable = the *workflows* side of Anthropic's taxonomy.

### Delegation (agents as tools)

```python
@function_tool
async def ask_data_analyst(question: str) -> str:
    """Ask the data analyst agent a numeric question about capstone tables."""
    result = await Runner.run(sql_agent, question)
    return str(result.final_output)

orchestrator = Agent(
    name="Manager",
    instructions="Use ask_data_analyst for numbers, kb_search for prose. Synthesize both.",
    tools=[ask_data_analyst, search_knowledge],
)
```

Use when: the manager must *interleave* specialist calls with its own reasoning (compare two sources, iterate). Costs: manager context grows with each delegation (W10-05 budgeting); specialists can't see each other's outputs unless the manager relays them. You built this shape in W10-01 — the SDK version just adds typed tool plumbing.

## 2. Choosing — the decision table

| Need | Pattern |
|---|---|
| Mutually exclusive domains, least privilege | handoff |
| Known ordered stages | chaining |
| Interleaved reasoning over specialists | delegation |
| Dynamic branching/loops with explicit control | LangGraph (W13) — the SDK's handoffs are implicit graphs; graphs make them explicit |
| Simple fixed pipeline | *no agents* — W3-05 again |

The W3-05 lever table now extends to architecture: handoff/chaining/delegation are *arrangements* of the agent lever, and each arrangement trades flexibility against predictability exactly as that table predicted.

## 3. State passing between agents

What moves, and what doesn't:

- **Handoff**: full conversation history moves; the receiving agent's `instructions` replace the sender's. Anything else (user profile, flags) must be re-injected or carried via `context` (the typed per-run object from file 02).
- **Chaining**: nothing moves implicitly — you explicitly pass `final_output` (shape it with `output_type` per stage).
- **Delegation**: only the *tool args* reach the worker; the manager owns all context and must summarize results back.

```python
# explicit, typed state for chaining
class Research(BaseModel):
    findings: list[str]
    citations: list[str]

research = (await Runner.run(rag_agent, plan.final_output)).final_output_as(Research)
```

Rule (from W10-05): the *scratchpad* is the state that survives — with chaining, that's the typed intermediate objects; with handoffs, that's the history; with delegation, that's the manager's own notes.

## 4. Anti-patterns (the failures to design against)

| Anti-pattern | Symptom | Fix |
|---|---|---|
| **Handoff ping-pong** | A hands to B, B back to A, loop | handoff descriptions disallow back-transfers; max_turns |
| **Manager spiral** | delegation tool called 8× for one question | budget in instructions ("call each specialist at most twice"), max_turns |
| **Context bloat at the manager** | every delegation result fully appended | managers summarize results into notes (W10-05) |
| **Shadow prompts** | specialists each re-explain the whole system | constitutions stay scoped per agent (W10-05 §2) |
| **Silent scope creep** | specialist uses a tool its domain never needed | per-agent tool lists = least privilege (W10-04) |

The `max_turns` parameter is your circuit breaker in every pattern — set it, test it (W10-01 exercise 3's SDK edition).

## Exercises

1. Implement all three patterns over the same 5 questions (triage, plan→research→write, manager+2 tools). Compare: answer quality, steps, tokens, wall time. One table.
2. Induce handoff ping-pong deliberately (two agents instructed to defer to each other); observe `max_turns` protection firing. Then fix via descriptions.
3. Delegation budget: add "call each specialist at most twice" to the manager; run 10 tasks; count violations before/after.
4. Typed chaining: give each stage a `output_type` (Plan, Research, Draft); break stage 2's schema — where does the error surface, and how do you recover?
5. Draw your capstone's orchestration as a diagram (agents, edges, tools, gates). Which pattern(s) survive your W6-04 router's question distribution — and what stays a plain pipeline?

## Pitfalls

- **Multi-agent by fashion** — three agents where one with three tools suffices is 3× failure surface (Anthropic's *effective agents* thesis)
- **Delegation without result summarization** — manager context explodes (W10-05's budget rules apply per delegation)
- **Untyped intermediate state** — stringly-typed stage handoffs break silently; `output_type` everywhere
- **Guardrail gaps between handoffs** — intermediate agents bypass intake guards; validate at tool level (file 02's note, now a pattern-level rule)
- **No circuit breakers** — max_turns unset in any pattern; test every path with a pathological task

## Resources

- Anthropic, *Building effective agents* — orchestrating workflows vs agents (§ "Orchestrating")
- OpenAI Agents SDK, [agents guide](https://openai.github.io/openai-agents-python/agents/) + [running agents](https://openai.github.io/openai-agents-python/running_agents/)
- W3-05 (levers), W6-04 (router), W10-01 (loop) — the three ancestors of every pattern here
- LangGraph concepts docs (skim) — for the vocabulary of the explicit-graph alternative arriving in Week 13
