# Deep-Dive: MCP Servers & FastMCP

Parent overview: [`../03-mcp-servers-fastmcp.md`](../03-mcp-servers-fastmcp.md)

This subfolder takes the in-process registry out-of-process: the MCP
architecture (hosts/clients/servers/transports), a FastMCP server exposing
your capstone tools, the two-tier test battery (deterministic + real-LLM),
and the read-only-first tool surface your capstone ships.

## File map

| File | What it covers |
|---|---|
| [`01-mcp-architecture.md`](01-mcp-architecture.md) | Hosts, clients, servers, transports |
| [`02-fastmcp-server.md`](02-fastmcp-server.md) | Tools/resources/prompts from decorators |
| [`03-client-batteries.md`](03-client-batteries.md) | Deterministic tests + real-LLM paths |
| [`04-capstone-tool-surface.md`](04-capstone-tool-surface.md) | Read-only-first design, versioned surface |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-mcp-architecture.md` — the moving parts, named once.
2. `02-fastmcp-server.md` — your registry, served over MCP.
3. `03-client-batteries.md` — two test tiers, one truth.
4. `04-capstone-tool-surface.md` — what you expose, and why that's all.

## Prerequisites

- [`../02-tools-and-memory/`](../02-tools-and-memory/) — the in-process
  registry whose contracts the server must preserve.
- [`../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/03-router-safety.md`](../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/03-router-safety.md)
  — the injection battery, now crossing process boundaries.
