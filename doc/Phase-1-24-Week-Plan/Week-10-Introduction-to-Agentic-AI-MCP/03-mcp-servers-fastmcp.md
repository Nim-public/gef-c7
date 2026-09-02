# 03 — MCP Servers with FastMCP

> Week 10 index: [README.md](README.md)

**Session 2 topics:** *Understand the Architecture Parallel. Implement Basic MCP Server: Use FastMCP (Python framework) to create an MCP server. Practical Implementation. Test with Real LLM.*

---

## What you'll learn

- What MCP (Model Context Protocol) is and the architecture parallel toWeek 9's tool contract
- Building a server with FastMCP: tools, resources, transports
- Testing with the FastMCP client and with a real LLM
- Wrapping your capstone's retrieval + SQL systems as MCP tools

## 1. The problem MCP solves

Weeks 10-02 gave your *one* agent a tool registry. Now multiply: Claude Desktop, your IDE assistant, your W11 SDK agents, your W13 LangGraph app — each wants your search/SQL tools, each with its own glue. Before MCP: N apps × M tools = N×M integrations.

**Model Context Protocol** (Anthropic, 2024 — now an industry standard) is the USB-C between LLM apps and capabilities:

```
┌──────────────┐   MCP    ┌─────────────────────┐      ┌──────────────────┐
│ MCP client   │◄────────►│ your FastMCP server │─────►│ W9 RAG / W6 SQL  │
│ (any app)    │  stdio/  │ tools, resources    │      │ (your capstone)  │
└──────────────┘  http    └─────────────────────┘      └──────────────────┘
```

Write the server **once**; every MCP-capable client can call it. That's the "architecture parallel": MCP tool schema ≈ your Week 10-02 registry schema ≈ OpenAI function schema — one idea, standardized on the wire.

Server capabilities: **tools** (model-invoked functions — the 90% case), **resources** (client-read data: files, configs), **prompts** (reusable prompt templates).

## 2. FastMCP server

```powershell
pip install fastmcp
```

```python
# capstone_mcp.py
from fastmcp import FastMCP

mcp = FastMCP(
    name="Capstone Tools",
    instructions="Capstone knowledge tools: document/table search and read-only SQL.",
)

@mcp.tool
def search_knowledge(query: str, k: int = 5) -> dict:
    """Search the capstone knowledge base (documents + tables).
    Returns hits with id, text, source and a relevance score."""
    from retrieve import search_knowledge as _impl     # W9-05 contract
    return _impl(query, k=k)

@mcp.tool
def sql_query(question: str) -> dict:
    """Answer an aggregational question over capstone tables with a read-only
    SELECT. Returns {sql, cols, rows}. Refuses write statements."""
    from text2sql import run_query                     # W6-03
    return run_query(question)

if __name__ == "__main__":
    mcp.run()                                          # stdio transport (default)
```

Decorator mechanics (why this is nearly free): FastMCP reads the function's **name, type hints, and docstring** to generate the tool's schema — your docstring *is* the LLM-facing description (Week 10-02's design rules apply verbatim). Type hints become the JSON schema.

Transports:

| Transport | Use | How |
|---|---|---|
| **stdio** | local apps (Claude Desktop, IDE) | `mcp.run()` — the client spawns your script |
| **HTTP/SSE** | shared/network servers | `mcp.run(transport="http", port=8000)` |

Resources and prompts, for completeness:

```python
@mcp.resource("doc://schema")
def db_schema() -> str:
    """The live database schema for SQL tools."""
    return read_schema_block()                # W6-03 — generated from the DB, not hand-copied

@mcp.prompt
def triage(ticket: str) -> str:
    """Support-ticket triage prompt."""
    return f"Classify and route this ticket:\n{ticket}"
```

## 3. Testing: client first, then a real LLM

### FastMCP client (deterministic, no tokens — run in CI)

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("capstone_mcp.py") as client:       # in-proc from the script
        tools = await client.list_tools()
        print([t.name for t in tools])                    # ['search_knowledge', 'sql_query']

        res = await client.call_tool("search_knowledge",
                                     {"query": "refund timeline", "k": 3})
        print(res.data)

        try:
            await client.call_tool("sql_query", {"question": "delete all orders"})
        except Exception as e:
            print("blocked as designed:", e)              # W6 validator surfaces here

asyncio.run(main())
```

Test battery (pytest, mirroring W3-02/W5-04 habits): list_tools returns expected names *with* descriptions; each tool's happy path; the injection probe through `sql_query`; and the no-match case returning `caveat` rather than empty.

### With a real LLM (the session's "test with real LLM")

Two integration paths:

**A. Via an SDK agent (preview of Week 11)** — the OpenAI Agents SDK can attach MCP servers directly:

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async with MCPServerStdio(params={"command": "py", "args": ["capstone_mcp.py"]}) as server:
    agent = Agent(
        name="Capstone assistant",
        instructions="Use search_knowledge for prose questions, sql_query for numbers.",
        mcp_servers=[server],
    )
    result = await Runner.run(agent, "How many GPU orders, and what's the refund timeline?")
    print(result.final_output)
```

**B. Claude Desktop / any MCP client** — add to the client's config:

```json
```json
{"mcpServers": {"capstone": {"command": "py", "args": ["<repo>/capstone_mcp.py"]}}}
```

*(Claude Desktop requires an absolute path here — point it at your local clone, e.g. `C:/Users/you/GEF C7/capstone_mcp.py`.)*
```

Restart the client; your tools appear in the chat. Watching a *foreign* application call *your* capstone tools is the moment MCP clicks.

## 4. Wrapping the capstone — the full tool surface

| MCP tool | Wraps | Safety rails |
|---|---|---|
| `search_knowledge` | W9-05 hybrid retriever | k cap, caveat on low confidence |
| `sql_query` | W6-03 Text2SQL | read-only user + validator (defense in depth) |
| `get_schema` (resource) | live DB schema | read-only by nature |
| `catalog_product` (later) | W9-01 app 2 | idempotent upsert by id |

Design rules carried over: minimal verbs (no `run_shell`), structured returns, explicit caveats, descriptions written for the model. The MCP server is your capstone's *public API* — same discipline as any API you'd ship.

## Exercises

1. Build `capstone_mcp.py` with the two tools; verify `list_tools` shows generated schemas (inspect the parameter types — where did they come from?).
2. Client battery: 6 tests — 2 happy paths, wrong-tool name, injection via `sql_query`, empty-result caveat, oversized k (validator).
3. Connect Claude Desktop (or any MCP client) to your server; ask one question that *requires* both tools and watch both fire. Screenshot the trace for your README.
4. Add a third tool `list_recent_orders(limit)` wrapping raw SQL with a hardcoded, allow-listed query — compare its reliability vs `sql_query` for the same question. What does fixed-surface vs free-form SQL teach you?
5. Serve over HTTP (`transport="http"`) and point the client at the URL. What changes in your test code? (Answer: only the constructor.)

## Pitfalls

- **Docstrings as afterthoughts** — the generated description is the *only* selection signal a client LLM gets
- **Slow first call** — imports/models load on server start; heavy init belongs at module level, and clients time out
- **State in the server** — stdio servers are one-per-client; HTTP servers are shared — scope per-request or use a DB (W10-02's mutable-global warning, at protocol scale)
- **Exposing write tools before gates exist** — a write tool is a remote code execution primitive for any connected client; read-only first, always
- **Assuming the client validates** — MCP transports carry whatever args arrive; your W6/W10-02 validators still do the real work

## Resources

- [FastMCP docs](https://gofastmcp.com) — servers, tools, resources, clients (the framework this program uses)
- [Model Context Protocol spec](https://modelcontextprotocol.io) — the protocol's official docs
- OpenAI Agents SDK, [MCP guide](https://openai.github.io/openai-agents-python/mcp/) — path A integration (W11)
- Anthropic, *Model Context Protocol* announcement + Claude Desktop MCP config guide
