# FastMCP Server — Tools, Resources, Prompts from Decorators

**What you'll learn:** expose your Week-09 RAG tools as an MCP server in
under 60 lines: `@mcp.tool` for actions, `@mcp.resource` for read-only
data, `@mcp.prompt` for reusable prompts — with your error contracts
preserved verbatim.

## 1. The server, complete

```python
# scripts/mcp_rag_server.py
from fastmcp import FastMCP
import lancedb

mcp = FastMCP("gef-c7-rag", version="1.0.0")   # matches tool-contract v
db = lancedb.connect("data/lancedb")
table = db["units"]

@mcp.tool
def retrieve(query: str, modality: str | None = None, k: int = 5) -> list[dict]:
    """Search the corpus. Returns unit_id, text, score, path.
    Use for facts, quotes, chart lookups. Empty list = nothing found."""
    hits = hybrid_retrieve(query, modality, k)      # Week-09 function
    return hits if hits else []

@mcp.tool
def get_unit_text(unit_id: str) -> str:
    """Full text of one unit (page, crop, or clip transcript).
    Raises a hint if the id is unknown — call retrieve() first."""
    row = table_lookup(unit_id)
    if row is None:
        raise ValueError(f"unknown unit_id '{unit_id}'; ids look like "
                         "u042 or u042::r2 — call retrieve() first")
    return row["text"]

@mcp.resource("corpus://stats")
def corpus_stats() -> str:
    """Read-only corpus summary (counts, versions)."""
    return Path("reports/corpus-stats.json").read_text()

@mcp.prompt
def grounded_answer(question: str) -> str:
    """Reusable answer prompt: cite units, refuse without evidence."""
    return SYSTEM_TEMPLATE.format(question=question)

if __name__ == "__main__":
    mcp.run()                                       # stdio transport
```

Three decorator kinds, one mental model: **tools do things, resources
are things, prompts say things.** Your Week-09 handlers sit unchanged
under `@mcp.tool` — the registry's contracts became wire contracts.

## 2. Errors across the wire

Your `ToolError` hints must survive the boundary. FastMCP maps exceptions
to `isError: true` results with the message text — so write the hint into
the message, and keep the hint style from the registry file:

```python
# in-process:  raise ToolError("unit_id 'x' not found; call retrieve() first")
# over MCP:    {isError: true, content: [{text: "unit_id 'x' not found; ..."}]}
```

The agent's loop must treat `isError` exactly like the in-process
exception path — instructive observation, not a crash (file 05 formats
it).

## 3. Tool descriptions are now *the* interface

In-process, you had code review; over MCP, the model sees only the
docstring and signature. The bar rises:

| Element | In-process acceptable | Over MCP required |
|---|---|---|
| Description | terse | purpose + when-to-use + return shape |
| Defaults | in code | visible in schema |
| Failure mode | exception | stated in docstring |

Rule of thumb: a colleague must be able to call the tool from the
docstring alone — because the model *is* that colleague.

## 4. HTTP mode for the multi-client demo

```python
mcp.run(transport="http", host="127.0.0.1", port=8001)
# host connects:  client = MCPClient("http://127.0.0.1:8001")
```

Same handlers, same battery — the transport swap is one line (file 01's
table). The demo pattern: stdio for development, HTTP when the Week-11+
UI or a second agent connects.

## Exercises

1. Wrap your three RAG tools as a FastMCP server; connect from a test
   client; diff `tools/list` against your registry schemas — identical or
   explain.
2. Error-fidelity drill: call `get_unit_text("nope")` over MCP; verify the
   hint text arrives intact in the `isError` content.
3. Resource check: fetch `corpus://stats` and compare against the report
   file — resources are read-only views, and must never drift from the
   artifact.

## Pitfalls

- Business logic inside decorators — handlers stay thin; the Week-09
  functions are the logic, the server is a skin.
- Docstrings that say "see README" — the model cannot click links; the
  docstring is the whole manual.
- Returning numpy arrays or DataFrames — MCP results must be JSON-able;
  convert at the boundary, not in the handler's caller.

## Resources

- FastMCP docs (`@mcp.tool`, resources, prompts, transports).
- Your Week-09 tool contract — now served, version and all.
