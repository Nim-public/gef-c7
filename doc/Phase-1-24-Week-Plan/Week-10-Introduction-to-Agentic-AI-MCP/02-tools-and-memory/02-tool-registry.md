# ToolRegistry — jsonschema Validation, Error Contracts

**What you'll learn:** the registry as the agent's API gateway: schema
validation before execution, error contracts that teach instead of crash,
and the audit log that makes every call reviewable.

## 1. The registry, complete

```python
import jsonschema, time

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, dict] = {}      # name -> {fn, schema, meta}

    def register(self, fn, schema: dict, readonly: bool = True,
                 timeout_s: float = 5.0):
        self._tools[schema["function"]["name"]] = {
            "fn": fn, "schema": schema, "readonly": readonly,
            "timeout_s": timeout_s}

    def schemas(self) -> list[dict]:
        return [t["schema"] for t in self._tools.values()]

    def call(self, name: str, args: dict) -> str:
        tool = self._tools.get(name)
        if tool is None:
            raise UnknownTool(name, known=sorted(self._tools))
        params = tool["schema"]["function"]["parameters"]
        jsonschema.validate(args, params)       # gate 1: schema
        t0 = time.perf_counter()
        try:
            out = tool["fn"](**args)            # gate 2: execution
        except ToolError as e:
            raise ToolError(e.hint)             # gate 3: contract errors
        log_call(name, args, time.perf_counter() - t0)
        return out
```

Two gates before any user code runs: existence and schema. The audit log
(`log_call`) is the trajectory input for file 04's harness — free metrics
from the registry.

## 2. Error contracts — exceptions as instruction

```python
class ToolError(Exception):
    """Contract errors carry a hint the model can act on."""
    def __init__(self, hint: str):
        super().__init__(hint); self.hint = hint

def get_unit_text(unit_id: str) -> str:
    row = table_lookup(unit_id)
    if row is None:
        raise ToolError(
            f"unit_id '{unit_id}' not found. Valid ids look like 'u042' or "
            "'u042::r2' (region crops). Call search() first to list ids.")
```

The hint is the error contract: *what happened, what ids look like, what
to do next*. The loop converts it to an observation (file 05); the model
recovers in one step instead of three blind retries.

| Error class | Raised by | Model-visible hint |
|---|---|---|
| `UnknownTool` | registry | names the valid tools |
| `ValidationError` | jsonschema | the failing field + expected type |
| `ToolError` | tool body | situation + next action |
| `TimeoutError` | wrapper | "took >Ns; narrow the query" |

## 3. Read-only-first — the capstone's tool surface

Week 09's contract was read-only; keep it that way until measured need:

| Tool | Class | Rationale |
|---|---|---|
| `retrieve`, `get_unit_text`, `get_image` | read | the RAG surface |
| `compute_metric` | read | pure function over retrieved data |
| `write_note` | **deferred** | write access = injection blast radius |

The read-only rule from the W9 safety battery generalizes: an agent that
can only read cannot exfiltrate or destroy; add the first write tool with
a HITL gate (file 04), never casually.

## 4. The registry test suite (five tests, no more)

```python
def test_registry_contract():
    assert register_and_call_ok("retrieve", {"query": "x"})       # happy path
    assert raises(UnknownTool, call="retrive")                     # typo
    assert raises(ValidationError, args={"query": 42})             # type
    assert raises(ToolError, args={"unit_id": "nope"})             # contract
    assert schemas_are_unique_and_typed()                          # hygiene
```

Five tests cover every gate; the hygiene test (unique names, every
property typed) catches schema rot before the model feels it.

## Exercises

1. Wrap your Week-09 retrieval functions in the registry; wire the error
   contracts; verify all five registry tests.
2. Hint-quality drill: for 3 contract errors, run the agent and count
   steps-to-recovery with generic vs instructive hints — the A/B that
   justifies writing good errors.
3. Audit-log probe: from 10 agent runs, produce the per-tool call count
   and latency table — file 04's first metric, already collected.

## Pitfalls

- Validating with the *model's* argument JSON as truth — validate against
  the schema, always; models hallucinate field names.
- Broad `except Exception` at the tool body — contract errors get
  flattened into unhelpful strings; raise typed errors with hints.
- Registering write tools "just to try" — read-only-first is a security
  posture, not a phase.

## Resources

- `jsonschema` docs (Draft 2020-12); your Week-09 tool contract.
- [`../01-agents-foundations/01-agent-definition.md`](../01-agents-foundations/01-agent-definition.md)
  — the components this registry fills.
