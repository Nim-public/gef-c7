# State Passing — Context, Outputs, Summaries Across Boundaries

**What you'll learn:** the three state channels in multi-agent systems —
run context, typed outputs, and conversation summaries — what each is
for, and the boundary rules that keep state from leaking.

## 1. The three channels

| Channel | Carries | Lifetime | SDK home |
|---|---|---|---|
| Run context | dependencies (ids, clients, flags) | one run | `RunContextWrapper[T]` |
| Typed outputs | results between agents | per call | `output_type` |
| Conversation/summaries | dialogue state | episode | session + handoff filters |

```python
from agents import RunContextWrapper

@dataclass
class RunCtx:
    retrieved_ids: set[str]
    p3_quota: int
    mode: str                    # demo | eval | shadow

def retrieve(ctx: RunContextWrapper[RunCtx], query: str, k: int = 5):
    ctx.context.retrieved_ids.update(...)   # state the validators trust
```

The context object is *infrastructure*, not content: ids for validators,
quotas for gates, mode flags for batteries. Question content travels as
inputs and outputs — never smuggled through context.

## 2. What crosses each boundary (the rules)

| Boundary | Crosses via | Never crosses |
|---|---|---|
| tool call | args (schema-typed) | run context internals |
| chain stage | typed output model | raw history |
| handoff | conversation (filtered) | context (rebuilt per agent if needed) |
| agent-as-tool | tool args → tool result | intermediate turns (stay nested) |

The W10 state-boundary rule generalizes: **context objects do not
cross agent boundaries** — each agent rebuilds what it needs from
inputs/outputs. A context field a specialist mysteriously needs is
either an input it should receive or a design smell.

## 3. Summaries: the compression channel

Long episodes hand off badly — the receiving agent pays for every prior
turn. The summary pattern:

```python
def summarize_for_handoff(items: list, max_chars: int = 800) -> str:
    facts = [f"[{i}] {it.summary}" for i, it in enumerate(items)
             if it.kind in ("answer", "key_fact")]
    return "Prior context:\n" + "\n".join(facts[-6:])
```

| Content | Carried raw? | Why |
|---|---|---|
| final answers, key facts | yes | the decision surface |
| tool call details | no — summarized | verbosity, not signal |
| failed attempts | one line each | lessons without cost |
| system/constitution | never duplicated | the new agent has its own |

The fitter's rules (W10 file 05) apply per boundary: summaries are
compression with receipts — ids and numbers survive, prose shrinks.

## 4. The state-passing checklist

```text
[ ] every typed output has a schema version
[ ] run context carries only infrastructure (ids, quotas, flags)
[ ] handoff input filter strips tool noise (or nests deliberately)
[ ] summaries preserve ids and numbers (fitter property P3/P4)
[ ] no context field is read by two agents with different meanings
```

## Exercises

1. Wire `RunCtx` through your tools; add the retrieved-ids validator
   dependency; verify the typed-output guardrail sees it at the answer
   agent.
2. Boundary audit: for your router + specialists, list what crosses each
   boundary; flag any context field consumed by two agents with
   different expectations.
3. Summary drill: hand off from a 10-turn episode with the summary
   pattern; verify the specialist's answer quality matches a fresh-run
   baseline (±1 rubric point) — summary fidelity, measured.

## Pitfalls

- Context as a global grab-bag — typed, minimal, infrastructure-only;
  the audit exists because grab-bags grow.
- Handoffs that carry the full raw transcript — the input filter is the
  tool; raw history is the specialist's bill, not its asset.
- Summaries that drop ids — the citation gate fails downstream; the
  fitter's P3 property is the guard.

## Resources

- SDK run context docs + handoff filters (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/03-context-fitter.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/03-context-fitter.md)
  — the compression properties this extends.