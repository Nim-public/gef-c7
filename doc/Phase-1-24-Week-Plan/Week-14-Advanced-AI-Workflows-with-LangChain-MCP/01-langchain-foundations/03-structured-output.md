# Structured Output — Pydantic-Validated Chains

**What you'll learn:** `with_structured_output` at the chain boundary:
Pydantic models as the validation layer, `include_raw` for forensics,
and the W9/W11 citation-audit pattern surviving intact.

## 1. The pattern

```python
from pydantic import BaseModel, Field

class Answer(BaseModel):
    answer: str
    citations: list[str] = Field(description="unit_ids like 'u042'")
    confidence: float = Field(ge=0, le=1)

typed = model.with_structured_output(Answer)
result = typed.invoke(prompt_value)          # → Answer instance
```

Identical contract to W11's `output_type` and W12's `output_schema` —
the third framework, the same Pydantic validator port. Your citation
audit (W9-04) plugs in as a field validator, exactly as before.

## 2. include_raw — forensics without losing typing

```python
typed_raw = model.with_structured_output(Answer, include_raw=True)
res = typed_raw.invoke(prompt_value)
res["parsed"]        # Answer instance
res["raw"]           # the AIMessage — for the trajectory store
res["parsing_error"] # None, or the validation failure
```

The trajectory store wants the raw response (token counts, finish
reason); the application wants the typed object. `include_raw=True`
gives both — the merge (W11 file 05-03) continues to work unchanged.

## 3. Validation failures as control flow

| Failure | `with_structured_output` behavior | Your handling |
|---|---|---|
| schema-valid but phantom citations | *passes* (schema-level) | your guardrail/validator layer |
| malformed JSON | retry per model config; error after | catch, log, degrade |
| wrong types | OutputParserException | catch, log, degrade |

The layering lesson from W11 file 02-04: schema validation catches
*shape*; your validators catch *semantics* (phantom citations); the
degradation ladder catches what both miss. Three layers, one answer
contract.

## 4. Structured output in the tool surface (create_agent)

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:pinned-model-id",
    tools=[retrieve_tool, get_unit_text_tool],
    response_format=Answer,          # structured final answer
)
result = agent.invoke({"messages": [{"role": "user", "content": q}]})
result["structured_response"]        # Answer instance
```

`response_format` on `create_agent` is the W11 `output_type`/W12
`output_schema` equivalent — the validator and the audit port unchanged.
The three-framework mapping table (W12 file 01-03) gains its final
column with this row.

## Exercises

1. Port the `Answer` model + citation validator to the LCEL chain;
   run the impossible-query case; the phantom must fail validation.
2. `include_raw` drill: store both `raw` and `parsed` in the trajectory
   row; verify token counts read from `raw.usage_metadata`.
3. Failure-taxonomy drill: force a malformed-JSON response (bad model);
   classify the failure per §3's table; wire the degradation.

## Pitfalls

- Validators that mutate instead of raise — the schema layer is not the
  place to silently fix citations; trip and degrade (W11's rule).
- Losing `raw` in the store — token accounting dies without it; always
  `include_raw=True` in eval paths.
- Confusing schema validation with grounding validation — a perfectly
  shaped answer can still be wrong; your audit layer is still required.