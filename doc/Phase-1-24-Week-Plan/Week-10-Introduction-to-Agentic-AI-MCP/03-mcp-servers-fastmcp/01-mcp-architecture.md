# MCP Architecture — Hosts, Clients, Servers, Transports

**What you'll learn:** the four MCP roles and two transports, what each
role owns, and where your capstone's components map onto them.

## 1. The roles, once each

| Role | Owns | Your capstone |
|---|---|---|
| Host | the LLM app, user consent, security policy | your agent loop (file 01) |
| Client | one-to-one connection to a server | the loop's tool bridge |
| Server | tools/resources/prompts, its own state | your RAG tools as a service |
| Transport | message carriage: stdio or HTTP(SSE) | stdio for local dev; HTTP when served |

```text
┌─ Host (your agent) ─┐   stdio/HTTP   ┌─ Server (RAG tools) ─┐
│ client ─────────────┼───────────────▶│ tools: retrieve, ... │
│ LLM, memory, gates  │◀───────────────│ resources, prompts   │
└─────────────────────┘    JSON-RPC    └──────────────────────┘
```

MCP is JSON-RPC over the transport; the client discovers the server's
capabilities (`tools/list`), then calls (`tools/call`). Everything your
registry did in-process — schemas, validation, errors — now crosses a
process boundary with the same semantics.

## 2. What moves across the boundary (and what never does)

| Crosses | Never crosses |
|---|---|
| tool schemas (JSON Schema) | your model API keys |
| tool results (text/images) | your LanceDB table files |
| resources (read-only data refs) | in-process state (scratchpad, history) |
| prompts (reusable templates) | the host's memory tiers |

The state boundary is the design lesson: the server is *stateless over
requests* (your LanceDB is its only state); the host owns memory, gates,
and the LLM. An MCP server that holds session state splits your agent's
mind across processes — keep memory in the host.

## 3. Transports: stdio vs HTTP, decided by deployment

| Transport | Use | Capstone stage |
|---|---|---|
| stdio | server as child process of the host | dev, tests, demo on one machine |
| HTTP + SSE | server as a service, many clients | multi-user demo, Spaces |

Same tools, same handlers — the transport is configuration, which is why
the battery (file 03) runs identically against both.

## 4. Capability discovery and versioning

```text
client → initialize(capabilities) → server responds with its tool list
client → tools/list                → schemas (the registry's, unchanged)
client → tools/call(name, args)    → result | isError + message
```

Your Week-09 tool-contract version string rides along in the server's
metadata — the client asserts compatibility before first call, the same
manifest-version discipline across a process boundary.

## 5. Failure modes at the boundary — what breaks across processes

| Failure | In-process behavior | Cross-process behavior | Defense |
|---|---|---|---|
| tool crash | exception, caught | process may die | server per-call isolation, restart policy |
| slow tool | latency spike | timeout + dead client | server timeouts, client deadline |
| big result | memory pressure | transport limits | pagination, size caps |
| partial write | transaction rolls back | state visible mid-flight | staging tables (W9-04) |

```python
# client-side deadline — the loop never waits forever:
result = client.call(name, args, timeout_s=tool["timeout_s"])
```

The table is why the registry's per-tool `timeout_s` mattered in file 02:
in-process it was hygiene; across a boundary it is the difference between
a slow step and a hung agent. Every boundary failure has an in-process
twin — the battery (file 03) runs the cases against both to prove parity.

## Exercises

1. Draw your capstone's role diagram (host/client/server/transport) with
   the exact tools that cross; mark what stays in-process.
2. Statefulness audit: list every piece of state in your loop; assign
   host/server ownership — anything assigned "server" that is not LanceDB
   is a design smell; note it.
3. Transport drill: run the same server over stdio and HTTP; diff the
   tool listings — they must be identical.
4. Boundary-failure drill: kill the server mid-trajectory; verify the
   client's error observation is instructive and the agent degrades (not
   hangs).

## Pitfalls

- Servers that import the host's memory or scratchpad — state boundary
  violation; the server sees requests, not sessions.
- Tool schemas diverging between registry and server — single source: the
  server derives schemas from the same definitions.
- Skipping the initialize handshake's version assert — silent protocol
  drift; assert, don't hope.

## Resources

- MCP specification (modelcontextprotocol.io) — roles, lifecycle, JSON-RPC
  methods.
- FastMCP docs — the implementation of everything in this diagram.
