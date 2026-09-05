# The MCP Adapter — Multi-Server Client Configuration

**What you'll learn:** one client, many servers: the adapter that
federates your RAG server, a filesystem server, and a utility server
into one tool surface — with per-server namespaces and version checks.

## 1. The adapter

```python
from fastmcp import Client

SERVERS = {
    "rag":   {"url": "stdio:mcp_rag_server.py",      "version": "1.0.0"},
    "files": {"url": "stdio:mcp_files_server.py",    "version": "1.0.0"},
    "util":  {"url": "http://127.0.0.1:8002/mcp",    "version": "1.0.0"},
}

class MultiServerAdapter:
    def __init__(self, servers: dict):
        self.clients = {name: Client(cfg["url"]) for name, cfg in servers.items()}
        self._schemas = {}
        for name, client in self.clients.items():
            tools = client.list_tools()
            assert_server_version(client, servers[name]["version"])
            self._schemas[name] = [namespace(name, t) for t in tools]

    def call(self, server: str, tool: str, args: dict) -> str:
        return self.clients[server].call(tool, args)
```

| Design element | Purpose |
|---|---|
| per-server namespace (`rag__retrieve`) | no cross-server name collisions |
| version assert at connect | the W10 handshake rule, federated |
| server prefix in every call | provenance: which server answered |

The W10 single-server client becomes an adapter over several — the
namespacing is the load-bearing addition, because two servers exposing
`search` silently collide without it.

## 2. Namespace conventions

| Server | Tool | Federated name |
|---|---|---|
| rag | retrieve | `rag__retrieve` |
| rag | get_unit_text | `rag__get_unit_text` |
| files | list_files | `files__list_files` |
| util | time_now | `util__time_now` |

The double-underscore convention is machine-parseable (split once) and
human-readable. The trajectory store records the *federated* name, so
the audit trail shows which server served each call — the W10 audit
log, federated.

## 3. The client contract (the tool-contract page, federated)

```markdown
## Federated surface v1
| server | version | tools | transport |
|---|---|---|---|
| rag | 1.0.0 | retrieve, get_unit_text | stdio |
| files | 1.0.0 | list_files, read_file (sandboxed) | stdio |
| util | 1.0.0 | time_now | HTTP |

Client minimum: version assert per server, tools/list diff per server,
namespaced calls only.
```

The W10 surface page, one row per server. The client asserts every
server's version and diff-checks every server's tool list — a server
that changes unannounced fails the connection, not the demo.

## 5. The adapter test suite (the federation's contract tests)

```python
def test_namespacing():
    names = [t.name for t in adapter.exposed_tools()]
    assert all("__" in n for n in names)              # every tool namespaced
    assert len(names) == len(set(names))              # no collisions

def test_version_asserts():
    with pytest.raises(VersionMismatch):
        adapter_with_bad_config()                     # bumped server, old config

def test_server_isolation():
    rag_tools = {t.name for t in adapter.exposed_tools() if t.name.startswith("rag__")}
    files_tools = {t.name for t in adapter.exposed_tools() if t.name.startswith("files__")}
    assert rag_tools and files_tools and not (rag_tools & files_tools)
```

Three tests are the adapter's contract: namespacing completeness,
version enforcement, and per-server isolation. They run in CI on every
server change — the federation's wiring is tested like everything else.

## Exercises

1. Build the adapter over three servers; print the federated surface;
   verify namespacing and version asserts.
2. Collision drill: add a second server exposing `search`; verify the
   namespacing prevents the collision (both surface, both callable).
3. Contract drill: bump one server's version without updating the
   config; the connect assert must fail loudly.
4. Suite drill: implement §5's three tests; wire into CI; any server
   change re-runs them.

## Pitfalls

- Unnamespaced federated tools — collisions surface as "the wrong tool
  answered"; the prefix prevents the class.
- Version asserts skipped "for the demo" — a server bump silently
  changes behavior; the assert is the demo's seatbelt.
- One adapter class per server pair — the adapter is generic; server
  count is configuration.