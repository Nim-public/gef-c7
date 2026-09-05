# Memory Taxonomy — History, Scratchpad, Episodic, Semantic

**What you'll learn:** the four memory tiers agents actually use, what
each costs in tokens, what belongs in each, and the budget line that
decides when to compress.

## 1. The taxonomy, with owners

| Tier | Content | Lifetime | Cost driver | Capstone form |
|---|---|---|---|---|
| History | the message list | one episode | grows every step | the loop's `messages` |
| Scratchpad | working notes the agent writes | one episode | agent-controlled | `scratchpad_add(note)` tool |
| Episodic | past *trajectories* (summarized) | across queries | grows per session | trajectory store (file 04) |
| Semantic | corpus facts, profiles | permanent | retrieval, not growth | your LanceDB index |

The crucial boundary: **history is transcript, scratchpad is conclusion.**
History is append-only and unfiltered; scratchpad is what the agent
decided matters. Confusing them is why agents drown by step 8.

## 2. What actually goes in each (capstone rules)

| Tier | Include | Exclude |
|---|---|---|
| History | tool calls/observations, user turns | full tool *outputs* >600 tok (summarize) |
| Scratchpad | "top hit u042, margin 12.4%", dead ends | raw retrievals, JSON dumps |
| Episodic | one-line trajectory summaries + outcome | full traces (they live in file 04's store) |
| Semantic | tool descriptions, user prefs | anything query-specific |

```python
def scratchpad_add(note: str) -> str:
    if len(note) > 200:
        raise ToolError("notes are conclusions, not transcripts; keep <200 chars")
    SPAD.append(note)
    return f"noted ({len(SPAD)} notes)"
```

A tool for the scratchpad (read via context injection, write via this)
makes memory *auditable* — you can diff what the agent chose to remember.

## 3. Episodic memory without a vector store (yet)

```python
def summarize_trajectory(trace: list[dict], outcome: str) -> str:
    tools = [t["tool"] for t in trace]
    return f"{outcome}: {len(tools)} steps via {tools}"

# retrieved into context only when a new query matches its intent
```

Full episodic retrieval (embeddings over summaries) arrives with the
memory week; for now, the summary *line* in the system context is the
80% version: "last similar query: EBITDA chart → 2 steps, found u042".

## 4. The budget line that forces compression

| Context section | Budget (8k ctx) | Exceeded → |
|---|---|---|
| System + constitution (file 05) | 400 tok | rewrite, never truncate |
| Tool schemas | 600 tok | drop tools, never mangle |
| Scratchpad | 300 tok | compress oldest |
| History observations | 2500 tok | summarize closed steps |
| Retrieved context (RAG) | 3500 tok | top-K trim (W9 budget) |
| Answer reserve | 700 tok | untouchable |

File 04 implements this table as the fitter; the taxonomy file's job is
to decide *what* lives where so the fitter has clean layers to cut.

## Exercises

1. Instrument your loop: log tokens per tier after every step; produce the
   per-tier growth chart for one 8-step trajectory.
2. Scratchpad drill: give the agent the `scratchpad_add` tool on a
   multi-hop query; verify the final answer cites notes, not raw
   observations (the tier doing its job).
3. Compression drill: at 70% history budget, summarize all closed steps
   into one line each; re-run the query and confirm the answer is
   unchanged — compression that changes answers is a bug, not a feature.

## Pitfalls

- "Memory = bigger history" — unbounded history is the #1 cost failure in
  student agents; tiers exist to bound it.
- Scratchpad entries that are copies of observations — the tier is for
  conclusions; the observation is already in history.
- Episodic memory storing full traces in-context — traces are for file
  04's harness, not the model's window.

## Resources

- Your Week-09 context budget (the RAG layer of this table).
- [`03-mcp-servers-fastmcp/`](../03-mcp-servers-fastmcp/) — next: the tool
  surface, out-of-process.
