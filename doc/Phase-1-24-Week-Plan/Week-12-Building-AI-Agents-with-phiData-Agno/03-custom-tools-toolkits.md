# 03 — Custom Tools & Toolkits

> Week 12 index: [README.md](README.md)

**Session 2 topic:** *Building a custom toolkit for advanced data handling and retrieval-augmented generation (RAG).*

---

## What you'll learn

- Agno tools vs toolkits: packaging your capstone capabilities the framework way
- Writing a custom `Toolkit` over your W9 retriever, W6 SQL pipeline, and W9-05 agent contract
- Toolkit design rules carried over from W10-02 (unchanged, now with framework syntax)
- Tool result formatting and the observation contract (W10-05)

## 1. Plain functions as tools (the floor)

Agno wraps plain functions — name, type hints, docstring become the schema (W10-02's registry, framework edition):

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def count_orders(product: str) -> str:
    """Count capstone orders for a product name. Returns a sentence with the number."""
    from text2sql import run_query
    r = run_query(f"How many orders are there for product {product}?")
    return f"{r['rows']}"

agent = Agent(name="Counter", model=OpenAIChat(id="gpt-4o-mini"),
              tools=[count_orders])
```

Rules identical to W10-02: docstring = LLM manual; validate inside; structured returns; errors that teach.

## 2. Custom Toolkits (the framework's packaging)

A **Toolkit** groups related tools with shared config — the right shape once you have >2 tools over the same subsystem:

```python
from agno.tools import Toolkit

class CapstoneToolkit(Toolkit):
    def __init__(self, k_default: int = 5, row_limit: int = 100):
        super().__init__(name="capstone_tools")
        self.k_default = k_default
        self.row_limit = row_limit
        self.register(self.search_knowledge)
        self.register(self.sql_query)
        self.register(self.save_note)

    def search_knowledge(self, query: str, k: int | None = None) -> str:
        """Search capstone documents and tables.
        Returns ranked hits as 'id | source | text' lines. Use for prose questions."""
        from retrieve import search_knowledge as _impl        # W9-05 contract
        hits = _impl(query, k=k or self.k_default)
        if not hits or hits.get("caveat"):
            return "NO MATCHES — the knowledge base lacks this. Recommend telling the user."
        return "\n".join(f"[{h['id']}] {h['source']}: {h['text'][:300]}" for h in hits["hits"])

    def sql_query(self, question: str) -> str:
        """Answer numeric/aggregational questions over capstone tables (read-only)."""
        from text2sql import run_query                        # W6-03 (validator + repair)
        r = run_query(question)
        rows = "\n".join(", ".join(map(str, r["rows"][:self.row_limit])) for r in [r])
        return f"SQL: {r['sql']}\nColumns: {r['cols']}\nRows:\n{rows}"

    def save_note(self, note: str) -> str:
        """Persist an intermediate finding across steps."""
        self._notes.append(note)
        return f"saved ({len(self._notes)} notes)"
```

Everything from W10-02's design-rules table carries over verbatim — the toolkit is a *packaging*, not a redesign:

| W10-02 rule | In toolkit form |
|---|---|
| docstring = LLM manual | method docstrings, enforced |
| validate args | inside each method (W6 validator untouched) |
| idempotency | read-only tools by default; writes gated (W10-04) |
| structured returns | `ok/result/caveat` shape, or text-with-ids |
| least privilege | instantiate with flags (`allow_sql=False` for the prose-only agent) |

## 3. Advanced data handling: the tools the session names

| Toolkit tool | Wraps | Design notes |
|---|---|---|
| `search_knowledge` | W9 hybrid retriever | caveat on low confidence (W4-03 threshold) |
| `sql_query` | W6 Text2SQL | read-only; result row cap; SQL in output for audit |
| `get_schema` | W6-03 schema block | lets the agent self-check columns before querying |
| `chart_data` | matplotlib → file path (W1-03/05) | "visual insight" tools: save file, return *path + summary stats*, never the bytes |
| `save_note`/`read_notes` | W10-02 scratchpad | per-run scoping |

The chart tool is the analytics agent's superpower (file 04): numbers → PNG path → the agent references the file in its answer. Guard it like SQL: fixed output dir, no shell-outs, path-only returns.

## 4. RAG as a toolkit (advanced handling)

The session's phrase "custom toolkit for … retrieval-augmented generation" = your W9 retriever *and its evaluation knobs* exposed as tools:

```python
def search_knowledge(self, query: str, k: int | None = None,
                     doc_type: str | None = None) -> str:
    """Hybrid search over capstone docs+tables. Optional doc_type filter."""
    hits = hybrid_search(query, k=k or self.k_default, doc_type=doc_type)  # W4-05/W5-03
    ...
```

Exposing `doc_type` teaches the agent to *filter* (W5-03's prefilter pattern) — the description must say when to use it. Exposing too many knobs teaches nothing: one query param with clear semantics beats five.

## 5. Testing toolkits (the W10-03 battery, toolkit edition)

```python
def test_search_happy_path():
    out = toolkit.search_knowledge("refund timeline")
    assert out.startswith("[")            # cited format

def test_search_no_match():
    out = toolkit.search_knowledge("zzz nonexistent policy qqq")
    assert "NO MATCHES" in out

def test_sql_rejects_writes():
    out = toolkit.sql_query("delete all orders")
    assert "read-only" in out.lower() or "error" in out.lower()
```

Then wire the toolkit into an agent and re-run the W10 10-task trajectory suite — the toolkit changes the *packaging*, the eval proves the *behavior* didn't regress.

## Exercises

1. Package `search_knowledge` + `sql_query` + `save_note` as `CapstoneToolkit`; instantiate twice with different flags (full vs prose-only) and show the tool lists differ.
2. Add `get_schema` (W6-03's generated schema) and a question that previously failed on a typo'd column — does the agent self-correct now?
3. Add the chart tool; ask "orders by region as a bar chart" — verify a PNG path + a text summary come back, and the agent cites both.
4. Port the W3-02 injection battery through the toolkit path; confirm the W6/W10 walls hold under the framework's execution.
5. Docstring A/B: weaken one tool's docstring to one vague line; measure tool-selection accuracy across your 10 tasks (W10-04 suite). Quantify the docstring's worth.

## Pitfalls

- **Toolkit methods returning raw dicts with huge lists** — context explosion (W10-05); truncate and summarize in the tool
- **Shared mutable state on the toolkit** (`self._notes`) across concurrent runs — scope per run or use storage (W10-02's warning)
- **Naming collisions with framework tools** — `search` is a common name; namespace your toolkit (`capstone_search`)
- **Reimplementing validators inside tools loosely** — reuse the exact W6 validator functions; two validators drift
- **Toolkit god-object** — one class with 15 tools; per-task instantiation with flags (file 01's least-privilege note)

## Resources

- Agno [Tools docs](https://docs.agno.com) — custom tools, toolkits, function calling
- Agno toolkit examples (finance, SQL, web) — packaging patterns to mimic
- W10-02 (registry), W6-03 (SQL pipeline), W9-05 (retriever contract) — what you're wrapping
- CrewAI tools docs (next file's framework, same packaging idea)
