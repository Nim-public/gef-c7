# Deep-Dive: Workflow Assistant with MCP

Parent overview: [`../05-workflow-assistant-mcp.md`](../05-workflow-assistant-mcp.md)

The multi-server MCP assistant: one client configured across servers,
scope containment (paths, tokens, allow-lists), gated cross-server
chains, and cross-server injection testing — the W10 tool surface,
federated.

## File map

| File | What it covers |
|---|---|
| [`01-mcp-adapter.md`](01-mcp-adapter.md) | Multi-server client configuration |
| [`02-scope-containment.md`](02-scope-containment.md) | Paths, tokens, allow-lists |
| [`03-gated-chains.md`](03-gated-chains.md) | Gated cross-server chains |
| [`04-cross-server-injection.md`](04-cross-server-injection.md) | Injection testing across servers |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-mcp-adapter.md` — many servers, one client.
2. `02-scope-containment.md` — the walls, per server.
3. `03-gated-chains.md` — cross-server automation, gated.
4. `04-cross-server-injection.md` — the battery, federated.

## Prerequisites

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/`](../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/)
  — the server and client this adapter federates.
- [`../01-langchain-foundations/04-create-agent.md`](../01-langchain-foundations/04-create-agent.md)
  — the agent consuming the federated tools.