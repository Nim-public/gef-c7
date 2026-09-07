# phiData → Agno Migration — Imports and API Notes

**What you'll learn:** the rename (phiData → Agno) as an API migration:
what moved, what was renamed, what the old tutorials get wrong, and how
to read legacy phiData code without porting it blindly.

## 1. The rename, in imports

```python
# OLD (phiData):
from phi.agent import Agent
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.lancedb import LanceDb
from phi.playground import Playground

# NEW (Agno):
from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb
from agno.playground import Playground
```

| phiData concept | Agno concept |
|---|---|
| `phi.agent.Agent` | `agno.agent.Agent` |
| `KnowledgeBase` (per-source classes) | `Knowledge` (unified, sources via insert) |
| `phi.vectordb.lancedb.LanceDb` | `agno.vectordb.lance_db.LanceDb` |
| `phi.playground.Playground` | `agno.playground.Playground` / `AgentOS` |
| `phi.model.openai.OpenAIChat` | `agno.models.openai.OpenAIChat` |

The mechanical rule: `phi.` → `agno.`, then check the *knowledge*
classes — that is where the API restructured (KnowledgeBase → Knowledge
with unified `insert`).

## 2. The knowledge restructure, concretely

```python
# phiData-style (legacy):
kb = PDFUrlKnowledgeBase(
    urls=["https://example.com/doc.pdf"],
    vector_db=LanceDb(table_name="docs", uri="tmp/lancedb"),
)
agent = Agent(knowledge=kb, search_knowledge=True)

# Agno-style (current):
from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType

knowledge = Knowledge(
    vector_db=LanceDb(
        uri="tmp/lancedb", table_name="docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)
knowledge.insert(url="https://example.com/doc.pdf")
agent = Agent(knowledge=knowledge, search_knowledge=True)
```

Two visible changes: sources are added by `insert` (any type) instead of
per-source KnowledgeBase classes, and `SearchType.hybrid` +
`reranker` are first-class vector-db options — matching your Week-09
hybrid work exactly.

## 3. Reading legacy tutorials without porting blindly

| Legacy pattern | Modern reading |
|---|---|
| `add_tools=True`-style knowledge helpers | `KnowledgeTools` (think/search/analyze flags) |
| `assistant = Agent(...)` naming | cosmetic; `Agent` is the same object |
| Cookbook notebooks with `phi.` imports | translate imports, verify against current docs |
| `Assistant.run(..., references=True)` | `search_knowledge=True` semantics |

The reading rule for old code: **verify every construct against the
current docs before porting** — the framework moved fast, and 2024-era
phiData snippets are the tutorial-world equivalent of deprecated APIs.

## 4. The migration checklist

```text
[ ] imports: phi. → agno. (grep the whole file)
[ ] KnowledgeBase classes → Knowledge + insert
[ ] search flags: search_knowledge / KnowledgeTools flags
[ ] structured output: use_response_schema → output_schema
[ ] run the W10/W11 battery against the migrated agent
[ ] record version pins in reports/sdk-versions.md
```

The last row is the standing rule from W11: every framework touch gets a
version pin + a context7 id in the same file.

## Exercises

1. Migrate one legacy phiData snippet (any from the old cookbook) to
   current Agno; diff behavior on one query — identical output or
   document the API semantic that changed.
2. `grep` drill: `rg "from phi\."` across your repo; count stragglers;
   fix and re-run the battery.
3. Knowledge port drill: migrate your LanceDB corpus into Agno's
   `Knowledge` with `SearchType.hybrid`; run 5 retrieval queries through
   both stacks; compare hits (they should match — same engine, same
   table).

## Pitfalls

- Blind import renaming (`phi.` → `agno.`) — the knowledge API
  *restructured*; the rename alone compiles and misbehaves.
- Mixing legacy and current knowledge APIs in one agent — one
  `Knowledge` object per corpus; no dual-write.
- Tutorial code trusted over docs — context7 for the current signature,
  every time (the repo's standing rule).

## Resources

- Agno docs (context7: `/agno-agi/docs`); migration notes in the repo
  changelog.
- [`../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/01-multi-vector-tables.md`](../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/01-multi-vector-tables.md)
  — the LanceDB layer `Knowledge` wraps.