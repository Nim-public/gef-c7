# Three-Source Routing — Vector, SQL, Web

**What you'll learn:** the W12 three-power routing re-expressed as
LangChain tools: one `create_agent` with three retrieval tools, priority
instructions, and the source-label contract.

## 1. The agent

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_corpus(query: str) -> str:
    """Search the corpus (LanceDB hybrid). Use for facts, quotes,
    explanations. Returns unit_ids + text. The corpus is the source of
    record."""
    return json.dumps(hybrid_retrieve(query, k=5))

@tool
def query_warehouse(sql: str) -> str:
    """Run a SELECT over the warehouse. Use for exact numbers.
    Returns rows + row count. SELECT only."""
    return guarded_sql(sql)

@tool
def search_web(query: str) -> str:
    """Search the web for facts NOT in the corpus. Label answers as
    external. Last resort."""
    return web_search(query)

agent = create_agent(
    model="openai:pinned-model-id",
    tools=[search_corpus, query_warehouse, search_web],
    response_format=Answer,     # with source: corpus|tables|external
)
```

| Power | Tool | Cites |
|---|---|---|
| corpus | `search_corpus` | unit_ids |
| tables | `query_warehouse` | the SQL |
| world | `search_web` | URL + date |

The W12-05 three-power agent, LangChain edition — the priority rules
live in the tool descriptions and the typed `Answer.source` field. The
routing battery (W12 file 05-02) re-runs unchanged: same cases, same
assertions.

## 2. The priority instructions

```python
ROUTING_INSTRUCTIONS = [
    "PRIORITY 1: corpus facts → search_corpus. Cite unit_ids.",
    "PRIORITY 2: numbers over our tables → query_warehouse. Show the SQL.",
    "PRIORITY 3: external facts → search_web. Label as external.",
    "Never mix sources silently — the source field states what answered.",
]
```

The instructions are the W12-02 constitution, ported — and the battery
asserts usage, not just answers. The W9/W12 measurement discipline:
route accuracy per class, the same eval set, one more column.

## 3. The routing battery (three sources)

| Query | Expected tool | Assert |
|---|---|---|
| "What does the corpus say about X?" | `search_corpus` | unit_ids cited |
| "Total revenue Q3?" | `query_warehouse` | SQL shown |
| "NVDA price today?" | `search_web` | `source=external` |
| "Why did revenue rise?" | both 1+2 | both sources labeled |
| "Revenue in 2030?" | refuse | no power fires |

The battery is the W12-05 table, one column wider (LangChain). The
typed `source` field makes the labels structural — the harness asserts
corpus questions never answer `external`-only.

## 5. The routing pin note

**Task:** extend `reports/sdk-versions.md` with the three-source stack:
tool list, priority-instruction version (W12 cvN ported), the `source`
field schema, and the routing-battery command.

**Worked approach:** the three-power routing is now in its second
framework — the pin note records the battery's port status (same cases,
same assertions) and the instruction wording's version.

**Pass criterion:** note committed; the battery command green as
recorded.

## Exercises

1. Build the three-source agent; run the routing battery (5 cases × 3);
   verify tool usage and source labels.
2. Priority drill: query the corpus about something *also* on the web;
   the corpus must win and be labeled.
3. Disable drill: remove the web tool; external queries degrade
   honestly ("not in corpus; web disabled").
4. Pin drill: extend the note; confirm the battery cases match the W12
   set verbatim (the port's parity, router edition).

## Pitfalls

- Tool descriptions that duplicate the instructions — one priority list;
  descriptions describe *what*, instructions describe *when*.
- Web results silently mixed into corpus answers — the `source` field
  and its battery case are the guard.
- Routing measured on answers instead of tool usage — the trace (LangSmith
  or your store) shows what fired; assert that.