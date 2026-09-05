# Structured Output — output_type, Pydantic, Strict JSON Schema

**What you'll learn:** typed final answers: `output_type` turns your
string-parsing + citation-audit layer into a Pydantic model with
strict-schema enforcement — and changes where your validation lives.

## 1. The pattern

```python
from pydantic import BaseModel, Field
from agents import Agent

class Answer(BaseModel):
    answer: str
    citations: list[str] = Field(description="unit_ids like 'u042'")
    confidence: float = Field(ge=0, le=1)
    degraded: bool = False

agent = Agent(
    name="RAG agent",
    instructions="Answer only from tool results; cite every claim.",
    tools=[retrieve_tool, get_unit_text_tool],
    output_type=Answer,
)
```

`Runner.run` now returns `result.final_output` as an `Answer` instance —
no regex citation extraction, no `json.loads` at the boundary. Your W10
citation audit becomes a Pydantic validator:

```python
@field_validator("citations")
@classmethod
def citations_exist(cls, v, info):
    retrieved = info.context.get("retrieved_ids", set()) if info.context else set()
    unknown = [c for c in v if c not in retrieved]
    if unknown:
        raise ValueError(f"phantom citations: {unknown}")
    return v
```

(Context plumbing varies — the audit logic is unchanged from W9-04; only
its trigger moved from post-run to model-time.)

## 2. Strict JSON schema — what the SDK enforces for you

Under the hood, `AgentOutputSchema` wraps your model, generates a JSON
schema, and (by default) calls `ensure_strict_json_schema` — OpenAI's
strict mode, which guarantees the model's JSON *conforms* (all fields,
no extras) rather than merely resembling it.

| Mode | Behavior | When |
|---|---|---|
| `strict_json_schema=True` (default) | schema strictly enforced; unsupported constructs raise `UserError` at build | always, unless a type can't comply |
| `AgentOutputSchema(T, strict_json_schema=False)` | lenient validation | exotic types that can't be strict |

The design consequence: **strict mode forbids arbitrary `dict[str, Any]`**
fields and optional-by-default behaviors — your `Answer` model must be
fully typed. That constraint is a feature: it is the citation-audit
guarantee, mechanized.

## 3. Typed outputs through the pipeline

The typed final composes with everything you already built:

| Consumer | What it gets |
|---|---|
| trajectory store | `answer.degraded`, `answer.citations` as typed columns |
| metrics harness | outcome classification reads `degraded` — no parsing |
| Gradio UI | `result.final_output.answer` — no display munging |
| eval harness | gold comparison on typed fields |

The W10 outcome classifier (`outcome_of`) simplifies accordingly:
`refused` is now `answer == "not found"`-shaped or an empty citations
list — model intent made structural.

## 4. When *not* to set output_type

| Case | Recommendation |
|---|---|
| free-form chat demo | plain text; typing adds friction |
| agent mid-chain (its output feeds another) | type it — the chain depends on it |
| guardrail-validated prose | type it; `citations` is your audit handle |
| streaming to UI token-by-token | text or partial-object strategy; typed finals arrive at completion |

Your capstone: type the *final answer agent*, keep intermediate agents
chained via their own typed outputs (file 03), and leave utility agents
plain where typing buys nothing.

## Exercises

1. Define `Answer` with the citation validator; run the impossible-query
   task — the validator (not the prompt) must now catch phantom citations.
2. Strictness drill: add an `extras: dict[str, Any]` field; observe the
   `UserError`; remove it and document why strict mode rejected it.
3. Pipeline drill: chain two agents (extractor → answerer) with typed
   outputs; verify `result.final_output` on the *outer* run is the last
   agent's type, and `last_agent` names it.

## Pitfalls

- Validators that *silently fix* bad citations — validation that mutates
  hides model failures; raise, and let the tripwire/excision path handle.
- Forgetting the context plumbing for validation — `info.context` is not
  populated automatically; wire the retrieved-ids set through the run
  context.
- Typing everything by default — output_type is a contract; contracts on
  free-form agents produce parse failures, not safety.

## Resources

- SDK refs: `Agent.output_type`, `AgentOutputSchema`, strict JSON schema
  (context7: `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-09-RAG-with-Image-Video-Audio/04-end-to-end-multimodal-rag/03-grounded-generation.md`](../../Week-09-RAG-with-Image-Video-Audio/04-end-to-end-multimodal-rag/03-grounded-generation.md)
  — the citation audit this mechanizes.
