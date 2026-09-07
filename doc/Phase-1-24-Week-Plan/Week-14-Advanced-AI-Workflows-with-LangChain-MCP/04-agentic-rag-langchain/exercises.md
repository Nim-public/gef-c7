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

## 7. The decomposition pin note

**Task:** extend `reports/sdk-versions.md` with the decomposition stack:
SubQuestions schema, the fan-out mechanism, the synthesis contract, and
the probe-battery command.

**Worked approach:** decomposition is the multi-hop multiplier — the
pin note records the part bound and the self-containment probe coverage.

**Pass criterion:** note committed; the probe battery green as
recorded.

## 8. The agentic-RAG manifest (consolidated)

**Task:** consolidate the agentic-RAG stack in `reports/sdk-versions.md`:
the three-source tools, decomposition, self-improving loop cadence, and
the parity record — one block.

**Worked approach:** the agentic-RAG build spans four files; the pin
note is its manifest — every moving part's version and verification
date.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## 9. The parity mutation record

**Task:** run the parity mutation (loosen one grounding instruction in
the W14 agent); confirm the parity test fails on cases 1–5; restore;
record the before/after in the parity table's footer.

**Worked approach:** the mutation is the parity test's characterization
— the same discipline as every gate in the program: a gate that has
never failed a planted bug is not trusted.

**Pass criterion:** the mutation caught; the record committed beside
the parity pin note.

## Pitfalls recap

- Tool descriptions duplicating the priority instructions — one priority
  list; descriptions describe, instructions route.
- Decomposition on single-hop questions — the overhead without benefit;
  the routing rule decides.
- Mined cases without gate wiring — a case that never runs again is a
  vanity case.