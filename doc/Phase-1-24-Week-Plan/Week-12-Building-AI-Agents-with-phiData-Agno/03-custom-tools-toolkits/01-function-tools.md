# Function Tools — Schemas from Hints and Docstrings

**What you'll learn:** Agno derives tool schemas from Python type hints
and docstrings — the same "docstring is the contract" rule as the MCP
decorators (W10/W11), with Agno's own conventions.

## 1. The decorator and plain-function paths

```python
from agno.agent import Agent
from agno.tools import tool

@tool
def retrieve(query: str, modality: str | None = None, k: int = 5) -> str:
    """Search the corpus. Returns unit_id, text, score, path.

    Args:
        query (str): search terms.
        modality (str): 'text', 'image', 'video' or None for all.
        k (int): max hits, 1-20.

    Returns:
        str: JSON list of hits; empty list = nothing found.
    """
    return json.dumps(hybrid_retrieve(query, modality, k))

agent = Agent(model=..., tools=[retrieve], markdown=True)
```

| Source | Feeds |
|---|---|
| type hints | parameter JSON schema |
| docstring body | tool description |
| `Args:` section | per-parameter descriptions |
| `Returns:` section | result description |

Identical discipline to W10 file 02 — the docstring *is* the model's
documentation. Agno also accepts plain functions and `Toolkit` methods;
the schema derivation is the same in all three.

## 2. Strict functions for full schema control

```python
from agno.tools import Function

weather_tool = Function(
    name="get_weather",
    description="Get current weather for a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "city and state"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["location", "unit"],
        "additionalProperties": False,
    },
    strict=True,
    entrypoint=get_weather,
)
```

`Function` with `strict=True` is the escape hatch when hints cannot
express the schema (enums, additionalProperties=False). Your W10 registry
 schemas port verbatim — the JSON schema *is* the same artifact.

## 3. Docstring quality bar (the W10 rule, restated)

| Element | Required | Model-visible effect |
|---|---|---|
| one-line purpose | yes | when to choose this tool |
| Args section with types | yes | correct call construction |
| Returns description | yes | what to expect, stop-rule |
| failure behavior | yes | recovery without spirals |

The A/B discipline from W10 (hint quality → recovery steps) applies
verbatim: rewrite the docstring, measure the steps. Agno changes the
decorator, not the economics.

## 4. Error contracts at the Agno layer

Agno surfaces tool exceptions to the model as error results — your
`ToolError` hint pattern ports directly:

```python
@tool
def get_unit_text(unit_id: str) -> str:
    """Full text of one unit.

    Args:
        unit_id (str): unit id like 'u042' or region 'u042::r2'.

    Returns:
        str: the unit's text.
    """
    row = table_lookup(unit_id)
    if row is None:
        # the hint teaches; Agno relays it as the tool error
        raise ValueError(f"unknown unit_id '{unit_id}'; ids look like "
                         "u042 or u042::r2 — call retrieve() first")
    return row["text"]
```

Your W10 fidelity test ports unchanged: force the error, assert the hint
text arrives intact in the tool-result message.

## Exercises

1. Port the three RAG tools as `@tool` functions; inspect the derived
   schemas (print `agent.tools` internals or the request payload); diff
   against your W10 hand-written schemas.
2. Docstring A/B: rewrite one weak docstring; measure steps-to-correct-
   call on 5 queries — the hint discipline, same metric.
3. Error-fidelity drill: force the unknown-id error; assert the hint
   reaches the model verbatim; count recovery steps vs W10 baseline.

## Pitfalls

- Docstrings without the Args/Returns structure — Agno parses
  docstring-style sections; prose-only docstrings lose parameter
  descriptions.
- Hints swallowed by generic exception wrapping — raise with the hint in
  the message; test the fidelity (W10 file 02's test, re-run).
- Schemas drifting between the MCP surface (W10) and the Agno surface —
  one source of truth per tool; the diff test runs on both.

## Resources

- Agno tools docs: `@tool`, `Function`, docstring styles (context7:
  `/agno-agi/docs`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/02-tools-and-memory/02-tool-registry.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/02-tools-and-memory/02-tool-registry.md)
  — the contracts being re-skinned.