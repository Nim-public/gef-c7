# Handoff Pattern — Router → Specialist Topology

**What you'll learn:** the multi-agent topology your W9 router implied:
one triage agent, narrow specialists, dialogue ownership transferring at
handoff — with the token math that decides how many specialists you can
afford.

## 1. The topology

```python
from agents import Agent, handoff

chart_agent = Agent(
    name="ChartAgent",
    instructions="Answer chart/table questions using get_unit_text. "
                 "Always cite the unit_id.",
    tools=[get_unit_text_tool, get_image_tool],
    output_type=Answer,
)
fts_agent = Agent(
    name="FtsAgent",
    instructions="Answer exact-term queries (codes, names) using retrieve.",
    tools=[retrieve_tool],
    output_type=Answer,
)
router = Agent(
    name="Router",
    instructions="Triage: charts → ChartAgent; exact codes/names → FtsAgent; "
                 "simple lookups → answer yourself.",
    tools=[retrieve_tool],
    handoffs=[handoff(chart_agent), handoff(fts_agent)],
    output_type=Answer,
)
```

The W10 boundary rule applies per agent: each specialist is a *pipeline
with a narrow job*; the router is the only agent whose job is choosing.

## 2. The cost model: router tax + specialist cost

| Run shape | Model calls | Token overhead |
|---|---|---|
| router answers directly | 1 | none |
| router → handoff → specialist | 2+ | router's triage turn (full schemas) |
| handoff chains (A→B→C) | 3+ | each hop pays history again |

```python
def handoff_tax(p_specialist: float, triage_tokens: int, answer_tokens: int) -> float:
    direct = answer_tokens
    via_handoff = triage_tokens + answer_tokens
    return (p_specialist * (via_handoff - direct)) / direct
```

The router tax is the price of *not writing the if-statement*: with
p_specialist = 0.6 and triage ≈ 40% of an answer's tokens, the routed
path costs ~1.24× direct. Acceptable for quality; the point is that you
measure it (file 05's harness) instead of discovering it on the bill.

## 3. Specialist design rules

| Rule | Rationale |
|---|---|
| narrow tools per specialist | least privilege + smaller schemas = cheaper turns |
| typed output shared across specialists | downstream code is agent-agnostic |
| one-line "when to hand back" policy | escape hatch without ping-pong (file 05) |
| specialist names are routing-visible | the model reads them; name by domain |

```python
instructions="... If the query is not about charts or tables, hand back to Router."
```

The hand-back line is the loop-breaker: without it, specialists guess;
with it, misrouted queries return in one hop. Pair it with the anti-
ping-pong detector (file 05) so the rule never becomes a trampoline.

## 4. When the topology fits (and its ceiling)

Fits: query classes with genuinely different tool needs and vocabularies
(your W9 classes). Ceiling: ~3–5 specialists — beyond that, triage
accuracy drops (the model reads more descriptions) and the router tax
compounds. The W9 measurement (class distribution) caps the topology
before you build it: 4 classes → 4 specialists is a mapping, not a guess.

## Exercises

1. Build the router + two specialists from your W9 classes; run the eval
   set; report the handoff tax (measured, not the formula's example).
2. Specialist-hygiene audit: list each specialist's tools; any tool used
   by >2 specialists is a candidate for the router (shared tool, fewer
   transfers).
3. Hand-back drill: misroute a query on purpose; verify the specialist
   returns in one hop via its hand-back policy; count the wasted tokens.

## Pitfalls

- Specialists with identical tool sets — that is not specialization, it
  is prompt fragmentation; merge them.
- Untyped specialist outputs — the downstream (metrics, UI) breaks on the
  first handoff; share the `Answer` model.
- Routers that also answer — triage and answering are different jobs;
  the W10 boundary statement said so per-system, now per-agent.

## Resources

- SDK handoffs guide (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md`](../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md)
  — the class distribution that sizes this topology.
