# Chaining — Sequential Refinement with Typed Outputs

**What you'll learn:** the pipeline-as-agents pattern: typed hand-offs of
*values* (not dialogue control), where each agent's output type is the
next agent's contract — your W9 pipeline, re-expressed.

## 1. The chain

```python
from pydantic import BaseModel
from agents import Agent, Runner

class Extract(BaseModel):
    question_type: str
    needed_modality: str
    key_terms: list[str]

class Answer(BaseModel):
    answer: str
    citations: list[str]

extractor = Agent(name="Extractor", instructions="Classify the query",
                  output_type=Extract, model="pinned-fast-model")
answerer = Agent(name="Answerer", instructions="Answer using retrieved context; cite.",
                 tools=[retrieve_tool, get_unit_text_tool], output_type=Answer)

e = await Runner.run(extractor, query)
a = await Runner.run(answerer, f"{query}\n\nPlan: {e.final_output.model_dump_json()}")
```

Two properties distinguish chaining from handoffs: **control never
transfers** (your code holds the loop), and **values cross the boundary
typed** — `Extract` is the contract between the agents, in code.

## 2. Chain vs handoff: the decision

| Question | Chain | Handoff |
|---|---|---|
| Does the next agent need the *dialogue*? | no | yes |
| Is the sequence fixed? | yes | runtime-chosen |
| Who owns failure? | your code (between calls) | the agents |
| Cost control | explicit per stage | budgeted per run |

The W10 boundary statement applies recursively: chains are pipelines
built from agent stages — the hot path from your boundary memo, now with
typed seams. Handoffs are for the long tail where the *order* is
unknown.

## 3. Refinement loops (the controlled cycle)

```python
answer = None
for round_no in range(2):                     # hard budget: 2 rounds
    r = await Runner.run(answerer, prompt_for(round_no, answer, critique))
    answer = r.final_output
    if answer.confidence >= 0.8:
        break
    critique = await Runner.run(critic_agent, answer.model_dump_json())
```

Refinement = chain + critique agent + a *numeric* exit condition
(`confidence ≥ 0.8`, not "looks good"). The critique agent is the
self-check the SDK enables; the hard budget is what keeps it a refinement
instead of a spiral (file 05's detector watches this exact shape).

## 4. Cost and latency accounting per stage

| Stage | Model | Typical tokens | Latency |
|---|---|---|---|
| extract | fast | ~400 | ~0.5 s |
| retrieve+answer | main | ~2.5k | ~2 s |
| critique (round 2 only) | fast | ~600 | ~0.8 s |

The chain's ledger is explicit per stage — the property that makes
chaining the *auditable* topology. Your W9-04 cost ledger maps stage to
stage; the fitter applies per call, so budgets are per-stage, not global.

## Exercises

1. Re-express your W9 hot path (router→retrieve→generate) as a chain with
   two typed stages; run the eval set; compare success/steps/tokens with
   the handoff router on the same tasks.
2. Refinement drill: add the critique loop with a 2-round budget; measure
   how often round 2 fires and its success delta — the number that
   decides if the critique agent pays rent.
3. Typed-seam drill: change `Extract.needed_modality` to an enum; verify
   the answerer's behavior shifts measurably (schema-in-prompt effect) —
   typed seams are prompts too.

## Pitfalls

- Chains that re-implement handoffs (agent A "asks" agent B via a tool) —
  pick one mechanism; hybrid topologies hide control flow.
- Refinement without a numeric exit — "one more round" is the spiral's
  first step.
- Fast-model extraction that drops domain terms — the extractor's output
  is the answerer's *entire* view of the query; test the seam with the
  exact-term class.

## Resources

- SDK chaining patterns (agents as stages) (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/04-when-not-agents.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/04-when-not-agents.md)
  — the boundary this pattern implements.