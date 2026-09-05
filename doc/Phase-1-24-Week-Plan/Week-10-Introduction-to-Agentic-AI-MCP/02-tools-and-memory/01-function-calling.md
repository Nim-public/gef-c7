# Function Calling — Schema → Decision → Execute → Observe

**What you'll learn:** the four-movement protocol under every agentic
framework, what the model actually sees at each step, and the three places
schemas quietly fail.

## 1. The protocol, annotated per movement

```python
TOOLS = [{
    "type": "function",
    "function": {
        "name": "retrieve",
        "description": ("Search the corpus. Use for facts, quotes, charts. "
                        "Returns unit_id + text + score."),
        "parameters": {
            "type": "object",
            "properties": {
                "query":   {"type": "string", "description": "search terms"},
                "modality": {"type": "string", "enum": ["text", "image", "video", "audio"],
                             "description": "scope; omit for all"},
                "k":       {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "required": ["query"],
        },
    },
}]
```

| Movement | Who acts | What is on the wire |
|---|---|---|
| Schema | you | tool definitions in the request |
| Decision | model | `tool_calls: [{name, arguments(json str)}]` |
| Execute | you | your code; **never** the model's |
| Observe | you → model | `role:"tool"` message with the result |

The decisive detail: the model returns *JSON strings*, not objects —
`json.loads` failures are a protocol stage, not an exception, and belong
in the observation as instructive errors (file 05).

## 2. Where schemas quietly fail

| Failure | Example | Effect |
|---|---|---|
| Enum drift | schema says `["text","image"]`, tool handles `"video"` too | model never picks the valid option |
| Required overload | `required: ["query","modality","k"]` | model invents values to satisfy the schema |
| Description written for devs | "BM25+vector hybrid search" | model can't map queries to it |
| Untyped bags | `"parameters": {"type": "object"}` | model guesses argument names |

The capstone rule from Week 09's contract carries over: **schema = API**.
The `enum` is documentation the model reads; required fields are promises
you force it to make.

## 3. The observe step — formatting is context engineering

```python
def tool_message(call, entry: dict) -> dict:
    return {"role": "tool", "tool_call_id": call.id,
            "content": json.dumps(entry, ensure_ascii=False)[:600]}
```

The observation is a *prompt* (file 05 develops this): errors phrased as
guidance, results truncated at field boundaries, ids preserved verbatim
for citations. A 600-char cap keeps 5 tool steps inside ~3k tokens of
observations.

## 4. Parallel calls and their ordering hazard

Models may emit several `tool_calls` per decision. Two rules:

1. **Execute all before feeding back** — partial feedback teaches the
   model its other calls vanished.
2. **Order-independent tools only** — if `get_unit_text(u042)` informs
   whether to call `retrieve(...)`, it must wait for the next step.

```python
results = [registry.call(c.name, c.args) for c in resp.tool_calls]  # all first
messages += [tool_message(c, r) for c, r in zip(resp.tool_calls, results)]
```

## Exercises

1. Write schemas for your three Week-09 tools; run the four movements
   against a canned LLM; verify the wire format at each step.
2. Schema-failure hunt: take your real traces, find one enum drift and one
   required-overload; fix both; re-run the 10 predicted trajectories
   (foundations file 03) and report the step delta.
3. Parallel-call drill: craft a query where the model should emit 2
   independent calls; verify your loop executes both before feedback.

## Pitfalls

- Executing the model's *suggested* code (some models emit code strings)
  — tools are allow-listed callables; never eval.
- Schema fields named for your internals (`unit_id_v3`) — the model mangles
  them; name for the query writer.
- Observations that leak system prompts or paths — the observation is
  model-visible; sanitize like the W9 firewall does.

## Resources

- OpenAI function-calling reference; your Week-09 tool contract (the
  schema source).
- [`../01-agents-foundations/02-hand-rolled-react.md`](../01-agents-foundations/02-hand-rolled-react.md)
  — the loop this protocol plugs into.
