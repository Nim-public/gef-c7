# Toolkit Classes — Grouping, Scoping, Per-Task Flags

**What you'll learn:** `Toolkit` as the unit of tool *organization*:
grouping related functions, include/exclude scoping per agent, and
per-tool behavior flags (`stop_after_tool_call`, `show_result`) — the
least-privilege surface, toolkit edition.

## 1. The class shape

```python
from agno.tools import Toolkit

class CorpusTools(Toolkit):
    def __init__(self, mode: str = "demo", **kwargs):
        self.mode = mode
        tools = [self.retrieve, self.get_unit_text, self.get_image]
        super().__init__(name="corpus_tools", tools=tools, **kwargs)

    def retrieve(self, query: str, modality: str | None = None,
                 k: int = 5) -> str:
        """Search the corpus..."""
        ...

    def get_unit_text(self, unit_id: str) -> str: ...
    def get_image(self, unit_id: str) -> str: ...
```

The constructor carries configuration (mode, paths, quotas); the
methods are the tools; the docstrings are the schemas. One class per
domain — the W10 tool-surface table, as code.

## 2. Scoping: include/exclude per agent

```python
# least privilege: the demo agent cannot delete
demo_agent = Agent(
    tools=[CustomerDBTools(include_tools=["retrieve_customer_profile"])],
)
# full access for the maintenance agent
admin_agent = Agent(
    tools=[CustomerDBTools()],     # both tools
)
```

| Mechanism | Use |
|---|---|
| `include_tools=[...]` | allow-list per agent |
| `exclude_tools=[...]` | deny-list for shared toolkits |
| constructor config | environment (paths, quotas, dry-run) |

This is W10's read-only-first posture, mechanized: the *same toolkit*
serves a read-only demo agent and a full admin agent — the surface is a
construction parameter, not a fork.

## 3. Per-tool behavior flags

| Flag | Effect | Use |
|---|---|---|
| `stop_after_tool_call_tools` | agent stops after that tool | terminal actions (submit, finalize) |
| `show_result_tools` | result shown to user directly | formatting tools |
| `cache_results` / TTL | dedupe identical calls | expensive retrievals |

```python
Toolkit(name="t", tools=[...],
        stop_after_tool_call_tools=["finalize_report"],
        cache_results=True, cache_ttl=3600)
```

`stop_after_tool_call` is the declarative version of your W10
`looks_looped` problem's opposite: some tools *end* the episode by
design. The flag removes the model's option to continue past them.

## 4. The toolkit ↔ W10 surface mapping

| W10 surface element | Agno toolkit mechanism |
|---|---|
| registry schemas | derived from hints/docstrings |
| per-tool timeout | toolkit/tool config |
| error contracts | raises in methods |
| gate (`needs_gate`) | Agno hooks / pre-tool flags |
| read-only-first | `include_tools` allow-list |

The port is mechanical *if* your W10 contracts were written as data
(policies JSON) — which they were. This is the payoff of policies-as-
artifacts: they re-skin, they do not re-implement.

## Exercises

1. Wrap your RAG tools in `CorpusTools`; instantiate a demo agent with
   `include_tools` minus one tool; verify the missing tool is invisible
   to the model and the agent reroutes.
2. Flag drill: add a `finalize_report` tool with
   `stop_after_tool_call`; verify the episode ends there — and that a
   task *needing* two calls after it now fails (the flag's cost).
3. Config drill: same toolkit, two constructors (demo/eval); verify the
   demo instance cannot reach write-ish behavior.

## Pitfalls

- One god-toolkit for every agent — grouping is least privilege's
  substrate; split by domain.
- Flags set per-agent inconsistently — the toolkit constructor is the
  config surface; agent-level overrides get documented.
- Docstrings inside toolkits skipped — same bar as free functions; the
  model reads them identically.

## Resources

- Agno Toolkit docs: include/exclude, flags (context7: `/agno-agi/docs`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/04-capstone-tool-surface.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/04-capstone-tool-surface.md)
  — the surface policy this mechanizes.