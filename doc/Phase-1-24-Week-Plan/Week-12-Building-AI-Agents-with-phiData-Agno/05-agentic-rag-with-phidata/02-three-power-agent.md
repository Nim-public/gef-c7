# Three-Power Agent — Knowledge + SQL + Web Toolkit Routing

**What you'll learn:** the three-toolkit agent: knowledge (your corpus),
SQL (your tables), web (the world) — the routing design, the priority
rules, and the guardrail that stops the web tool from hallucinating your
corpus.

## 1. The agent

```python
from agno.tools.duckdb import DuckDbTools
from agno.tools.websearch import WebSearchTools
from agno.tools.knowledge import KnowledgeTools

three_power = Agent(
    name="Three-Power Agent",
    model=...,
    tools=[
        KnowledgeTools(knowledge=knowledge, enable_search=True),
        DuckDbTools(db_path="data/warehouse.duckdb"),
        WebSearchTools(),
    ],
    instructions=[
        "PRIORITY 1 — corpus questions: use knowledge search. Cite "
        "unit_ids. The corpus is the source of record.",
        "PRIORITY 2 — numeric over our tables: use SQL. Show the query.",
        "PRIORITY 3 — external facts: web search ONLY when the corpus "
        "and tables cannot answer. State that the answer is external.",
        "Never mix sources silently: label which power answered.",
    ],
    output_schema=Answer,       # citations + source field
    markdown=True,
)
```

| Power | Tool | Cites |
|---|---|---|
| corpus | knowledge search | unit_ids |
| tables | SQL | query text |
| world | web search | URL + access date |

The priority rules are the routing table as instructions — and the
"never mix silently" rule is the audit-trail contract: every answer
names its power.

## 2. The routing battery (three powers)

| Query | Expected power | Wrong-power symptom |
|---|---|---|
| "What does the corpus say about X?" | knowledge | web answer, no unit_ids |
| "Total revenue Q3?" | SQL | number with no query shown |
| "What is NVDA's price today?" | web | stale corpus answer |
| "Why did our revenue rise?" | knowledge + SQL | pure speculation |
| "What will revenue be in 2030?" | refuse | any power |

The battery asserts *tool usage* (which tools fired) plus the source
label in the answer — the same shape as the W9 route battery, one column
wider.

## 3. The web tool's special danger (corpus dilution)

The web tool is the only one whose results can *contradict* your corpus
— and the model may prefer its confidence. Guards:

| Guard | Mechanism |
|---|---|
| priority instructions | corpus first, world labeled |
| answer labeling | `source: "corpus" | "external"` field |
| freshness gates | web only for queries the corpus cannot answer |
| conflict disclosure | if both used and disagree, show both |

```python
class Answer(BaseModel):
    answer: str
    source: str = Field(description="'corpus', 'tables', 'external', or combo")
    citations: list[str] = []
    external_sources: list[str] = []
```

The typed `source` field makes the labeling *structural* — the harness
asserts corpus questions never answer with `source="external"` alone.

## 4. The web tool's place in the capstone (decided, not default)

| If the capstone is... | Web tool |
|---|---|
| corpus-QA (GEF C7 default) | disabled or last-resort, labeled |
| market/current-events assistant | enabled with freshness discipline |
| internal-compliance assistant | disabled entirely (provenance) |

The decision goes in the boundary memo with the same trigger discipline:
enable web when a *measured* class of queries needs the world, not when
the demo wants it.

## Exercises

1. Build the three-power agent; run the routing battery (5 cases × 3
   runs); verify tool usage and `source` labels.
2. Priority drill: query the corpus about something *also* on the web;
   verify the answer prefers the corpus and says so.
3. Disable drill: run with the web tool removed; verify external-class
   queries degrade honestly ("not in corpus; web access disabled").

## Pitfalls

- Web results cited as corpus facts — the `source` field exists because
  silent mixing is the default model behavior, not the exception.
- Priority rules that are vibes — the battery asserts usage; instructions
  without cases are wishes.
- Web enabled "for completeness" — it adds a provenance boundary and a
  failure surface; enable on measured need.