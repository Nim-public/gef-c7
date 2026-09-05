# Exercises — Agentic RAG with LangChain

Expanded set with worked approaches. The deliverable: the three-source
agent, decomposition working, the self-improving eval loop running, and
graph parity proven.

## 1. Three-source routing (from 01-three-source-routing)

**Task:** build the three-tool agent; run the W12 routing battery (5
cases × 3); verify tool usage and source labels; the priority drill
(corpus-vs-web overlap).

**Worked approach:** the battery is unchanged from W12 — same cases,
same assertions, new framework. The `source` field check is the
structural proof of the labeling contract.

**Pass criterion:** 5/5 routes + labels; the priority drill passes.

## 2. Decomposition (from 02-decomposition)

**Task:** build the decomposer; run the multi-hop cases; verify
sub-questions are self-contained; the synthesis cites per part.

**Worked approach:** the self-contained test is the schema description
plus a probe battery (pronoun cases). The fan-out uses `Send` (W13
file 01-02) or sequential parts — measure both.

**Pass criterion:** sub-questions self-contained; synthesis cites per
part; the pairing audit covers the parts.

## 3. Self-improving loop (from 03-self-improving-loops)

**Task:** mine your trajectory store; construct 3 cases from the top
failure cluster; add as eval-set v+1 with the changelog; wire into the
regression gate.

**Worked approach:** the mining table (n ≥3 classes) is the loop's
input; the cases are gold-labeled from data; the changelog names the
scars. The loop is *working* when the regression gate catches a
reintroduced failure class.

**Pass criterion:** 3 new cases gold-labeled; the changelog rows
committed; the gate updated.

## 4. Graph parity (from 04-graph-parity)

**Task:** run the 15-case set through both implementations; produce the
parity table; investigate any divergence.

**Worked approach:** the parity protocol (same corpus, config, 3 runs)
is the W11 comparison, fifth application. Divergence on corpus QA means
the shared artifacts (instructions, knowledge) drifted — fix the drift,
not the test.

**Pass criterion:** outcome parity 15/15; token delta within tolerance;
the memo updated.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Routing battery + labels | route table | 3 |
| Decomposition: self-contained parts | probe battery | 3 |
| Self-improving loop: cases mined + gated | changelog | 4 |
| Graph parity 15/15 | parity table | 4 |
| Pin note updated | pin note | 2 |

**Pass bar:** 13/16 to proceed to file 05 (MCP workflows). The
self-improving loop (4-pointer) is the week's compounding deliverable —
the eval set that maintains itself.

## Pitfalls recap

- Tool descriptions duplicating the priority instructions — one priority
  list; descriptions describe, instructions route.
- Decomposition on single-hop questions — the overhead without benefit;
  the routing rule decides.
- Mined cases without gate wiring — a case that never runs again is a
  vanity case.