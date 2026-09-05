# Architecture Freeze — The 1:1 Checklist

**What you'll learn:** the architecture freeze: every documented
component verified 1:1 against the code, every gate confirmed running,
and the freeze marked — after this, changes go through the revisit
process, not silent edits.

## 1. The freeze checklist (1:1 means every doc claim has code)

| # | Documentation claim | Code/artifact | Verified |
|---|---|---|---|
| 1 | text RAG pipeline | `scripts/rag_pipeline.py` | ☐ |
| 2 | multimodal ingestion | `scripts/ingest_multimodal.py` | ☐ |
| 3 | hybrid search + fusion | `scripts/retrieve.py` | ☐ |
| 4 | agent loop (SDK) | W11 port | ☐ |
| 5 | interactive flows (graph) | W13 graphs | ☐ |
| 6 | voice cascade | `scripts/voice_demo.py` | ☐ |
| 7 | eval harness + baselines | `scripts/eval_retrieval.py` + | ☐ |
| 8 | gates (all batteries) | CI workflow | ☐ |
| 9 | pin notes | `reports/sdk-versions.md` | ☐ |
| 10 | demo script | `scripts/four_pillars_demo.py` | ☐ |

The 1:1 rule: every row's doc claim is verified against the running
code *by executing it*, not by reading it. The freeze is the checklist
all-checked.

## 2. The freeze's side conditions

| Condition | Check |
|---|---|
| all batteries green | CI on the freeze commit |
| all pin notes current | the manifest review |
| all baselines committed | the gate inventory |
| no TODO/FIXME in the frozen paths | grep |
| the revisit process documented | the boundary memo's trigger list |

The side conditions are the freeze's preconditions — a freeze with red
gates or stale pins freezes the wrong thing.

## 3. After the freeze (the change process)

| Change type | Process |
|---|---|
| bug fix | allowed; tests must stay green |
| new capability | a revisit trigger fired; the memo updated first |
| dependency bump | the pin note + the affected batteries re-run |
| prompt/config change | version bump + battery re-run |

The freeze does not stop work — it makes changes *expensive enough to
be deliberate*. Every post-freeze change cites its trigger and re-runs
the affected gates.

## 4. The freeze report (the committed artifact)

```markdown
# Architecture freeze — [date] — commit [hash]

## Checklist: 10/10 rows verified by execution
[table from §1 with checkmarks and evidence commands]

## Side conditions: 5/5 green
[the §2 table with results]

## Change process: active (the §3 table governs from here)

Frozen by: [name]. Revisits require: a fired trigger, a memo update,
and gate re-runs.
```

The freeze report is the freeze's receipt — committed, dated, hash-
pinned. It is the document that says "this architecture is the release
candidate"; every later change cites it and its process.

## 5. The freeze's dependency inventory (the components, pinned)

| Component | Version source | Battery that re-verifies |
|---|---|---|
| model | `AGENT_CONFIG` | the 15-case eval |
| embedder | W8 memo | the parity loop |
| LanceDB | W9 pin | the golden-query parity |
| LangGraph | W13 pin | the span-shape fixture |
| SDK/LangChain/Agno | per-framework pins | their batteries |

The dependency inventory is the freeze's technical annex — every
component's version source and its re-verification battery. A dependency
bump after the freeze re-runs the battery before the freeze is amended;
the inventory is what makes that rule enforceable.

## 6. The freeze's components (the parts being frozen)

| Component | File/artifact | Gate |
|---|---|---|
| text RAG pipeline | `scripts/rag_pipeline.py` | the retrieval gate |
| multimodal ingestion | `scripts/ingest_multimodal.py` | V1–V8 |
| hybrid search + fusion | `scripts/retrieve.py` | the routing battery |
| agent loop (SDK) | the W11 port | the trajectory shapes |
| interactive flows | the W13 graphs | the invariant test |
| voice cascade | `scripts/voice_demo.py` | the latency table |
| eval harness + baselines | `scripts/eval_*.py` | the value gates |
| demo | `scripts/four_pillars_demo.py` | the acceptance run |

The components table is the freeze's body — one row per component, its
file, and its gate. It is the capstone's architecture, executable.

## Exercises

1. Run the freeze checklist end-to-end; every row verified by execution;
   the checked list committed as `reports/architecture-freeze.md`.
2. Side-condition drill: verify the five conditions; any red one blocks
   the freeze (fix first, freeze second).
3. Change-process rehearsal: make one post-freeze change through the
   process (trigger cited, gates re-run) — the freeze's maintenance,
   rehearsed.
4. Report drill: render §4 from the checklist results; the hash pinned;
   the freeze receipt is the capstone's milestone artifact.
5. Inventory drill: fill §5; every battery green at the recorded
   versions; the annex joined to the freeze report.
6. Components drill: verify the §6 table against the actual
   `scripts/` tree; every component's file exists and its gate is
   wired.