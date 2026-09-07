# Toolkit Testing — The Battery, Toolkit Edition

**What you'll learn:** the W10 client battery re-targeted: canned-model
tests for toolkit behavior (schemas, scoping, flags, errors) — the
transport changed, the contracts did not.

## 1. The battery rows, toolkit edition

| Case | Assert |
|---|---|
| schema from hints | derived schema matches expected (param names, types) |
| docstring descriptions | description + arg docs present, non-empty |
| include/exclude scoping | disabled tool invisible to agent |
| stop_after_tool_call | episode ends after the flagged tool |
| error contract | hint text arrives verbatim in tool error |
| cache behavior | identical call hits cache (call count == 1) |

```python
def test_scoping():
    agent = Agent(tools=[CustomerDBTools(include_tools=["retrieve_customer_profile"])])
    exposed = {t.name for t in agent.tools[0].functions.values()}
    assert exposed == {"retrieve_customer_profile"}     # delete not exposed

def test_error_contract():
    res = call_tool(get_unit_text, {"unit_id": "nope"})
    assert "u042" in res and "retrieve()" in res        # hint intact
```

The fidelity assertion (hint intact) is the W10 test, ported verbatim —
it guards the recovery path that the whole hint-A/B program built.

## 2. Canned-model integration (the fast tier)

```python
CANNED_RUNS = [
    # (query, expected tool sequence, expected stop)
    ("List files then finalize", ["list_files", "finalize_report"], "stop_after_finalize"),
    ("Search margins", ["retrieve"], "continue"),
]

@pytest.mark.parametrize("query,tools,stop", CANNED_RUNS)
def test_toolkit_flow(canned_llm, query, tools, stop): ...
```

The canned tier verifies *your wiring* — toolkit construction, flag
plumbing, scoping — deterministically. The real-model tier (nightly)
verifies the model *uses* the toolkit as intended. Both tiers, same
discipline as W10/W11.

## 3. Cross-framework parity (the MCP surface still exists)

Your W10 MCP server and this toolkit wrap the *same* Week-09 functions.
The parity test:

```python
def test_tool_parity_across_surfaces():
    mcp_schemas = {t["name"]: t for t in mcp_tools_list()}
    agno_schemas = {t.name: t for t in corpus_toolkit.functions.values()}
    for name in mcp_schemas:
        assert name in agno_schemas                    # same surface
        assert same_semantics(mcp_schemas[name], agno_schemas[name])
```

Two surfaces, one source of truth (the plain Week-09 functions). If the
toolkits drift, one surface is lying to its model — the parity test is
the drift detector, exactly like the MCP schema diff.

## 4. The toolkit changelog

| Change | Gate |
|---|---|
| new tool added | battery rows + scoping review |
| tool removed | dead-reference sweep (agents referencing it) |
| flag changed | flow test (stop/cache behavior) |
| docstring edit | hint A/B if it is an error-bearing docstring |

The changelog is the toolkit's version discipline — same shape as the
tool-surface v1 policy (W10 file 03): additive-only per version,
breaking changes get a new version.

## Exercises

1. Build the 6-row battery over `CorpusTools`; wire into CI with the
   fast-tier marker.
2. Scoping drill: two agents, one toolkit; verify the demo agent's view
   excludes the write-ish tool and the full agent sees it.
3. Parity drill: run the cross-surface test (MCP vs Agno) on all tools;
   any drift becomes a named bug with an owner.

## Pitfalls

- Toolkit tests that construct tools but never run the agent loop — the
  wiring includes how the model *sees* the tools; test the loop.
- Scoping verified by inspection instead of assertion — the model's view
  (request payload) is the truth; grep the payload.
- Parity drift accepted as "framework differences" — semantics drift;
  document or fix, never absorb silently.

## Resources

- Agno Toolkit reference (context7: `/agno-agi/docs`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/03-client-batteries.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/03-mcp-servers-fastmcp/03-client-batteries.md)
  — the two-tier battery this ports.