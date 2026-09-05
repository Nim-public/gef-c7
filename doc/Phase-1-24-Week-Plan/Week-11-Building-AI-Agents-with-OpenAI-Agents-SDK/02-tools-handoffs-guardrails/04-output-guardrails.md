# Output Guardrails — Citation/Schema Validation as Tripwires

**What you'll learn:** your W10 audits (citation gate, schema checks)
rebuilt as output guardrails: they run on the agent's final output, can
tripwire to block it, and turn "the answer was bad" into an exception you
handle at the boundary.

## 1. The output guardrail shape

```python
from agents import OutputGuardrail, GuardrailFunctionOutput

async def citation_guardrail(ctx, agent, output: Answer) -> GuardrailFunctionOutput:
    retrieved = ctx.context.get("retrieved_ids", set())
    phantom = [c for c in output.citations if c not in retrieved]
    return GuardrailFunctionOutput(
        output_info={"phantom": phantom},
        tripwire_triggered=bool(phantom),
    )

answer_agent = Agent(
    name="Answerer",
    instructions=...,
    output_type=Answer,
    output_guardrails=[OutputGuardrail(guardrail_function=citation_guardrail)],
)
```

Output guardrails run when the agent produces its final output; a
tripwire raises `OutputGuardrailTripwireTriggered` with the payload —
your W10 citation audit, now blocking *at generation time* instead of
being detected after the fact.

## 2. Audit → guardrail: the porting table

| W10 audit (post-hoc) | SDK guardrail (in-run) | Behavior change |
|---|---|---|
| citation audit → flag `[unverified]` | tripwire → exception | retry/re-handling inside the run possible |
| schema check on `Answer` | Pydantic `output_type` (already strict) | moved to model-time |
| faithfulness spot-check (10%) | sampled guardrail (random or risky-only) | audit becomes gate for the sampled set |
| HITL flag for degradation | `degraded` field + guardrail passthrough | flag survives, delivery unchanged |

The porting rule: *post-hoc audits that only inform* stay post-hoc;
*audits that must block* become guardrails. Your citation gate was
already a blocker — it moves. The faithfulness spot-check was sampling —
it can gate the sample.

## 3. What a tripwire buys (and its one cost)

| Property | W10 post-hoc | SDK tripwire |
|---|---|---|
| bad answer reaches user? | yes, flagged | no — exception first |
| retry inside the run | your loop hack | re-run with error context, native |
| latency on failure | same | one guardrail pass |
| observability | audit log row | guardrail span + exception payload |

The cost: a tripwired run *has no final output* — the boundary must
decide (retry, refuse, degrade). The W10 pattern maps directly: one
retry with the failure as instructive context, then the flagged
degradation path. Budget one guardrail retry, never a loop.

```python
try:
    result = await Runner.run(agent, query)
except OutputGuardrailTripwireTriggered as e:
    retry = await Runner.run(agent, f"Your previous answer failed citation "
                             f"validation: {e.guardrail_result.output_info}. "
                             f"Fix and answer again.", session=session)
    if not retry_ok(retry):
        return degraded_answer(e)     # W10's flagged fallback
```

## 4. The guardrail suite (port of the audit catalog)

| Guardrail | Checks | Source |
|---|---|---|
| `citation_guardrail` | citations ⊆ retrieved | W9-04 file 03 |
| `schema_guardrail` | answer non-empty, confidence range | W9-04 answer contract |
| `scope_guardrail` | answer doesn't quote system prompt | W9 battery markers |
| `faithfulness_guardrail` (sampled) | claims ⊆ context | W5/W9-05 judge, on the sample |

Each is a small function; the suite runs in Tier 1 with canned outputs.
The `output_info` payloads join the trajectory store — audit rows, now
raised as exceptions.

## Exercises

1. Port the citation audit to `citation_guardrail`; verify a phantom
   citation *blocks* the run (exception), the retry fixes it, and the
   degraded path still flags after one retry.
2. Sampled-gate drill: implement `faithfulness_guardrail` firing on 10%
   of runs (seeded by run_id); confirm the sample is deterministic
   (same run_id → same decision) for reproducibility.
3. Observability drill: trigger each of the four guardrails; locate each
   in the trace (guardrail span) and in the trajectory store — the audit
   rows, now exception-borne.

## Pitfalls

- Guardrails that *edit* the output instead of tripping — validation
  that fixes hides failures; trip, then retry with context.
- Unbounded retry loops on tripwires — one retry, then degrade; a loop
  of tripwires is a prompt bug, not a validation strategy.
- Moving *sampled* audits fully into gates — sampling exists for cost;
  keep the sampling, gate only the sampled set.

## Resources

- SDK output guardrails reference + exceptions (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/02-observation-formatting.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/02-observation-formatting.md)
  — the failure phrasing for retry context.
