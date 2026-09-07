# When NOT to Use Agents — The Pipeline Boundary

**What you'll learn:** the decision test that keeps agents out of places
pipelines belong: predictable queries, fixed costs, auditable paths. The
capstone answer is usually *both* — pipeline for the hot path, agent for
the long tail — and this file draws that line with your own numbers.

## 1. The decision test, four questions

| Question | If yes → | If no → |
|---|---|---|
| Do queries need *runtime* composition of steps? | agent candidate | pipeline |
| Is per-query cost variance tolerable (2–10×)? | agent | pipeline |
| Must every path be auditable in advance? | pipeline | agent + traces |
| Is the query distribution stable? | pipeline cheaper | agent amortizes |

```python
def needs_agent(query_classes: dict[str, int], dag_depth: int) -> str:
    if dag_depth == 1:
        return "pipeline"                     # single retrieval + answer
    if max(query_classes.values()) / sum(query_classes.values()) > 0.8:
        return "pipeline"                     # one dominant class: hardcode it
    return "agent"                            # genuine long tail
```

Your Week-09 router data already answers this: if 80% of queries hit one
route, that route is a pipeline; the remaining 20% is the agent's
territory.

## 2. The capstone split (the usual answer)

| Path | Mechanism | Why |
|---|---|---|
| Hot path (~80%) | fixed pipeline: route → retrieve → generate | predictable cost/latency, tested DAG |
| Long tail (~20%) | agent with tools = pipeline stages | composition you did not pre-enumerate |
| Escape hatch | agent → suggest new pipeline route | the agent *learns your DAG for you* |

The elegant consequence: agent trajectories that repeat a new pattern 5+
times are *pipeline proposals* — mining your own traces is how the hot
path grows on evidence.

## 3. The costs agents always add (budget them now)

| Cost | Typical magnitude | Mitigation |
|---|---|---|
| Extra model calls | +1–5 per query | episode budget (file 02) |
| Token overhead | tool schemas ~500–2000 tok/step | trim schemas; tool result truncation |
| Latency variance | p95/p50 of 2–4× | budget stop, streaming |
| New failure class | loops, injection via tools (W9) | loop detector, firewall |
| Eval complexity | path distribution, not single DAG | file 04's harness |

## 4. The honest boundary statement

Write it into the capstone README:

```markdown
## Agentic boundary
- Pipeline: single-hop retrieval + generation (80% of measured queries).
- Agent: multi-hop composition over the same tools (20%).
- The agent's tools are the pipeline's stages; one registry, two callers.
```

One registry, two callers — that sentence is the whole architecture. The
agent adds no new tools; it adds *ordering freedom* over the ones you
already tested.

## 5. The migration path — pipeline to agent without a rewrite

The boundary is not a wall; it is a schedule:

```text
week 10: pipeline stays default; agent runs in shadow (log-only, no user)
week 11: agent serves the long tail behind a flag; hot path unchanged
week 12+: mined trajectories promote repeated patterns into pipeline
          routes; the agent's share shrinks as the pipeline grows
```

```python
def shadow_mode(query: str) -> dict:
    pipeline_answer = run_pipeline(query)
    agent_answer = run_agent(query)          # logged, not served
    log_comparison(query, pipeline_answer, agent_answer)
    return pipeline_answer                   # users still get the pipeline
```

Shadow mode gives you the comparison data of exercise 3 for free, on real
traffic, with zero user risk — the standard way to introduce an agent
into a working system.

## Exercises

1. Apply `needs_agent` to your Week-09 query distribution; write the
   boundary statement with your real percentages.
2. Trace mining: from your 25-query runs, find any repeated 3+ step
   pattern; write the pipeline route it proposes (the escape hatch,
   working).
3. Cost comparison: same 10 queries through (a) fixed pipeline, (b)
   agent; report tokens, latency p50/p95, and success — the table that
   justifies the split (or reverses it).
4. Shadow-mode sketch: write `shadow_mode` + the comparison log schema;
   define the metric on which the agent "wins" the flag (success AND
   steps ≤ pipeline steps + 1).

## Pitfalls

- "Agents are more advanced, so use one" — the advanced move is the
  boundary, not the paradigm.
- Agent tools that bypass the tested pipeline stages — one registry means
  the agent calls the *same* audited code, not a parallel path.
- Forgetting variance: an agent demo succeeds at p50 and dies at p95 —
  budget from file 04's tables, not the happy path.
- Cutover without shadow data — the flag flips on vibes; a week of
  shadow logs buys the decision.

## Resources

- Anthropic "Building effective agents" (workflows vs agents); your
  Week-09 routing table (the distribution data).
- [`../04-measuring-agents-patterns/`](../04-measuring-agents-patterns/)
  — the harness that grades the shadow runs.
