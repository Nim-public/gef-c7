# Anti-Patterns — Ping-Pong, Spirals, Bloat

**What you'll learn:** the three multi-agent failure shapes, their trace
signatures, detectors you can write in ten lines, and the design rule
each one violates.

## 1. The catalog

| Anti-pattern | Trace signature | Violated rule |
|---|---|---|
| Ping-pong | handoff A→B→A→B, ≥2 cycles | one speaker per decision |
| Spiral | same tool called with near-identical args, 3+ times | budget + loop detector |
| Bloat | agents whose instructions restate other agents' jobs | one job per agent |
| (hidden) Nested-cost blindness | step counters ignore nested spans | harness reads spans |

Each has a detector — cheap, deterministic, running in the harness
(file 05) on every trajectory.

## 2. Ping-pong — the handoff trampoline

```python
def is_ping_pong(trace: list[dict], min_cycles: int = 2) -> bool:
    handoffs = [t for t in trace if t.get("type") == "handoff"]
    agents = [h["to"] for h in handoffs]
    pairs = list(zip(agents, agents[1:]))
    return pairs.count((agents[0], agents[1])) >= min_cycles or \
           len(set(agents)) < len(agents) - 1
```

Root cause is almost always a handoff description that says *when to
leave* but not *when to stay*: the specialist hands back on a case the
router re-routes. Fix: the one-line hand-back policy (file 01) plus
explicit stay-zones in the description ("if the query mentions charts or
tables, do not hand back").

## 3. Spirals — refinement without an exit

Signature: the same tool, same args ±epsilon, across turns; or
refinement rounds that never raise confidence. Detectors:

```python
def near_dup_calls(trace: list[dict], thresh: float = 0.95) -> int:
    calls = [(t["tool"], t["args"]) for t in trace if t.get("type") == "tool"]
    dups = 0
    for a, b in zip(calls, calls[1:]):
        if a[0] == b[0] and jaccard(a[1], b[1]) > thresh:
            dups += 1
    return dups
```

Fixes, in order: the loop-breaker observation (W10 file 05: name the
repetition), a numeric exit on refinement (chaining file), and the
episode budget as the backstop. A spiral that survives all three is a
task the agent cannot do — refuse, don't spin.

## 4. Bloat — agents accreting jobs

Signature: an agent's instructions exceed ~15 lines, its tool list spans
two domains, and its traces show it doing another agent's job. Bloat is
the slow failure — no single trace shows it; the *trend* does:

```python
def bloat_signal(agent_name: str, store) -> float:
    recent = store.recent(agent_name, runs=50)
    return mean(len(r.tools) for r in recent) - store.baseline_tool_count[agent_name]
```

Fix: the W10 boundary statement, per agent — each agent's README line
("owns X, not Y"). A tool that two agents share is a router decision
(file 01's hygiene audit); a job that three agents share is a missing
agent or a missing pipeline stage.

## 5. Nested-cost blindness — the meta anti-pattern

Every pattern above is *visible* only if the harness reads nested spans
(file 03's warning). The meta-fix: the trajectory schema counts model
calls, not steps, and the dictionary (W10 file 04) says so.

## Exercises

1. Write the three detectors; run them over your stored trajectories;
   report the counts — your topology's current health, in three numbers.
2. Ping-pong rehearsal: create the failing description, watch the trace
   ping-pong, fix the stay-zone, verify the detector goes quiet.
3. Spiral drill: give the agent an impossible task without the
   loop-breaker; watch the spiral; add the breaker; compare trajectories
   — the fix's value, measured in tokens.
4. Bloat trend: plot mean tools-per-agent over your runs; if it rises,
   name the accretion source (usually "one more tool just for this
   demo").

## Pitfalls

- Detectors that only watch *final* outputs — ping-pong and spirals live
  in the trace; the answer looks fine.
- Fixing ping-pong by banning hand-backs — the escape hatch is policy,
  not prohibition; write the stay-zone.
- Treating bloat as style — it is a cost curve; measure tools-per-agent
  like any other budget.

## Resources

- Your trajectory store + W10 harness (the detector substrate).
- [`../02-tools-handoffs-guardrails/02-handoffs.md`](../02-tools-handoffs-guardrails/02-handoffs.md)
  — the description discipline that prevents all three.