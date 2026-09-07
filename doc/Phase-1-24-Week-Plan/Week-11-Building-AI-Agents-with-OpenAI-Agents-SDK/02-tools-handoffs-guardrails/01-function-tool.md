# function_tool — Schemas from Signatures, Gating with is_enabled

**What you'll learn:** the decorator that replaces your registry's
schema-building: signatures become JSON schemas, docstrings become
descriptions, and `failure_error_function`/`is_enabled` map to your error
contracts and gates.

## 1. The port, side by side

```python
from agents import function_tool, RunContextWrapper

@function_tool(
    name_override="retrieve",
    failure_error_function=hint_error,        # your ToolError hints, verbatim
    is_enabled=lambda ctx, agent: ctx.context.get("mode") != "read_only_demo",
)
def retrieve(ctx: RunContextWrapper[AgentContext], query: str,
             modality: str | None = None, k: int = 5) -> list[dict]:
    """Search the corpus. Returns unit_id, text, score, path.
    Use for facts, quotes, chart lookups. Empty list = nothing found."""
    return hybrid_retrieve(query, modality, k)
```

| Registry concept (W10) | SDK mechanism |
|---|---|
| JSON schema generation | signature parsing (type hints → schema) |
| description + hints | docstring (auto-detected style) |
| `ToolError` hints | `failure_error_function` |
| validation gate | `strict_mode=True` (default) + server-side revalidation kept |
| gate policy | `is_enabled` callable (per-context) |
| HITL gate | `needs_approval` callable |
| timeouts | `timeout` + `timeout_behavior` |

Note the context convention: a first parameter of `RunContextWrapper`
receives your run context — this is where the retrieved-ids set and
session metadata flow (the typed-output validator's plumbing).

## 2. failure_error_function — the hint contract at the SDK layer

```python
def hint_error(ctx, error: Exception) -> str:
    return f"{type(error).__name__}: {error} — do not repeat this call " \
           f"unchanged; adjust arguments or use a different tool."

@function_tool(failure_error_function=hint_error)
def get_unit_text(ctx, unit_id: str) -> str: ...
```

Default behavior already notifies the LLM of failures; your W10 hint
*content* (valid id shapes, next action) comes from raising inside the
handler — the decorator wraps the message. Pass `failure_error_function=None`
to re-raise instead (for tools whose failures must abort).

## 3. is_enabled — context-conditional tool surfaces

```python
is_enabled=lambda ctx, agent: ctx.context["p3_quota_left"] > 0
# the VLM-answering tool vanishes from the schema when quota is out
```

`is_enabled` receives the run context and the agent, so tool availability
becomes *state-driven*: quota, mode flags, corpus readiness. This is the
W9 router's degradation ladder, mechanized — disabled tools vanish from
the schema rather than erroring at call time.

## 4. The porting checklist (registry → decorator)

| W10 contract item | Port action |
|---|---|
| schema + types | from signature; delete hand-written schema |
| docstring quality bar (W10: "colleague-callable") | same bar, now load-bearing |
| `ToolError` hints | raise in handler; `failure_error_function` formats |
| revalidation posture | keep server-side checks *inside* the handler |
| timeouts | `timeout=5.0`, `timeout_behavior="error_as_result"` |
| battery cases | port to file 05's pytest battery |

The last row is the porting rule from W10's MCP file, restated: the
decorator is a skin; the Week-09 functions remain the tested logic.

## Exercises

1. Port your three RAG tools to `@function_tool`; diff the generated
   schema against your hand-written one — the docstring must carry the
   hints the schema used to.
2. `is_enabled` drill: gate `get_image` behind a context flag; verify the
   disabled tool disappears from the model's view (check the request
   payload or `tools/list` equivalent) and the agent reroutes.
3. Error-fidelity drill: force each error class through the decorator;
   confirm the hint text reaches the model intact (your W10 fidelity
   test, re-run at the SDK layer).

## Pitfalls

- Docstrings that say "see README" — the decorator builds the tool
  description from them; the model sees exactly the docstring.
- `strict_mode` failing on exotic signatures (e.g., `dict[str, Any]`
  params) — tighten the signature; strict is the point.
- Moving validation *out* of handlers because the SDK parses schemas —
  the model is untrusted; keep server-side revalidation.

## Resources

- SDK reference: `function_tool` decorator (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/04-capstone-tool-surface.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/04-capstone-tool-surface.md)
  — the surface being ported.
