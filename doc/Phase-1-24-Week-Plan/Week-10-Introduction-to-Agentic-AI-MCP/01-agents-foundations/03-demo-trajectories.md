# Demo Trajectories — Single-Tool, Multi-Tool, Impossible

**What you'll learn:** three canonical trajectories to *predict before
running*: the trivial one, the multi-hop one, and the impossible one.
Prediction-then-verification is how you learn to read trajectories as
engineering artifacts.

## 1. Trajectory A — single tool, the boring success

Query: *"Summarize page 3 of the architecture doc."*

```text
step 1: thought "the doc is in the text index"
        call retrieve_page(page=3, doc="architecture")
        obs: "The system uses a three-stage pipeline..."
step 2: (no tool call) answer: "Page 3 describes ... [u011]"
```

**Prediction checklist:** exactly 1 tool step; no repeats; citation
present. If this trajectory ever takes 2+ tool steps, your tool does too
little or the description hides its scope.

## 2. Trajectory B — multi-tool, where control flow shows

Query: *"Which image in the corpus mentions the EBITDA margin, and what
is the exact number?"*

```text
step 1: search images by text         → retrieve(modality="image", query="EBITDA margin")
        obs: 3 hits (u042, u047, u051)
step 2: read the top hit's OCR        → get_unit_text("u042")
        obs: "gross margin 12.4%, EBITDA margin 8.1%"
step 3: verify against other hits     → get_unit_text("u047")
        obs: "EBITDA margin 8.1% (Q3)"
step 4: (no tool call) answer: "8.1% [u042][u047]"
```

**Prediction drill:** before running, write the expected step count and
tools. The verification value is in the *delta*: an extra `retrieve`
usually means the first retrieval's description undersold its filter
parameters; an extra `get_unit_text` means the observation format hid the
number (file 05's observation formatting).

## 3. Trajectory C — impossible, the one that proves the budget

Query: *"What was the CEO's bonus in 2019?"* (not in corpus)

```text
step 1: retrieve(query="CEO bonus 2019")   → 0 hits above threshold
step 2: retrieve(query="CEO compensation") → 2 weak hits, no bonus data
step 3: (no tool call) answer: "The corpus does not contain ... [no citation]"
```

**The success criterion here is the honest failure**: no invented number,
no phantom citation, ≤ budget. Agents that "succeed" on impossible
queries are your worst demo risk — the battery (W9) makes them explicit:

| Impossible-query class | Required behavior |
|---|---|
| absent fact | "not found" + no citation |
| unanswerable from images | say which modality lacks it |
| requires external data | name the missing source, refuse |

## 4. Trajectories as eval fixtures

Each trajectory above becomes a test: expected tools (as a set), expected
max steps, expected citation validity. Ten tasks × expected-route table
is the eval set file 06 builds — trajectories you have *seen* make the
table honest; trajectories you imagined make it fiction.

## Exercises

1. Write all three trajectories for *your* corpus (predict), run them,
   and produce a predict-vs-actual table with one-line causes per delta.
2. Construct a query that *should* take exactly 2 tools; if your agent
   takes 1 or 3, name the description fix for each direction.
3. Impossible-battery: 5 absent-fact queries; score the agent on the
   honest-failure rubric (no invention ≤ budget). Anything below 4/5 is a
   system-prompt fix (file 05), not a model problem.

## Pitfalls

- Treating a successful answer as a passing trajectory — success without
  the expected route means the control flow transfer worked *against* you.
- Impossible queries tested once, informally — they belong in the battery,
  run on every eval.
- Reading traces as prose — parse them; the trace *is* your metrics input
  (file 04).

## Resources

- ReAct paper §3 (trajectory examples); your Week-09 battery (the
  impossible-query classes).
- Your tool registry (file 02) — the trace source.
