# Exercises — LangGraph Foundations

Expanded set with worked approaches. The deliverable: your W10 agent
rebuilt as a graph, with state reducers tested and the execution path
readable.

## 1. State design (from 01-state-design)

**Task:** build the graph state (query, retrieved, errors, attempts,
answer) with three reducers; run one multi-hop query; verify accumulation
and overwrite semantics field by field.

**Worked approach:** the reducer table (§3) is the state's algebra —
write it as the state's docstring, then let the multi-hop run prove it.
The `errors` accumulator is the loop detector's substrate — feed it
from the tools node's except path.

**Pass criterion:** field-by-field semantics verified; the reducer table
in the state docstring.

## 2. Wiring the hot path (from 02-nodes-and-edges)

**Task:** wire the W9 hot path as a graph; run 5 queries; diff outcomes
and node sequences against the W9 function chain.

**Worked approach:** the graph is the *same* pipeline with inspectable
wiring — outcomes must match exactly; the node sequence is new
information (the W9 function chain hid it).

**Pass criterion:** 5/5 outcome parity; node sequences logged.

## 3. The bounded cycle (from 03-cycles-and-bounds)

**Task:** build the ReAct cycle with the three-way exit; run the eval
set; verify the attempts distribution matches W10's and the
force-answer edge flags `degraded`.

**Worked approach:** the bound is the W10 budget with a graph address —
`max_steps=6` in the config becomes `attempts >= 6` in
`should_continue`. The force-answer node completes the degradation
ladder's top rung.

**Pass criterion:** attempts distribution parity; forced runs flagged;
battery green.

## 4. Path reading (from 04-invoke-stream-inspect)

**Task:** run one task three ways (invoke/stream/history); extract the
trajectory row from each; verify all three agree with the W11 trace
(±5% tokens).

**Worked approach:** the three-views drill is the capture-parity test,
graph edition — invoke for results, stream for the live trace, history
for the record. The merge goes into your trajectory store unchanged.

**Pass criterion:** three views consistent; trajectory row committed;
parity within tolerance.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Reducers table + multi-hop proof | state tests | 3 |
| Hot-path graph parity 5/5 | wiring tests | 3 |
| Bounded cycle + force-answer edge | cycle tests | 4 |
| Three-view trajectory agreement | parity check | 3 |
| Graph diagram matches builder | README/code review | 2 |

**Pass bar:** 12/15 to proceed to file 02 (the story generator). The
bounded cycle (4-pointer) is the foundations' capstone — the W10 loop,
now a picture.

## Pitfalls recap

- Missing reducers silently overwriting accumulations — the multi-hop
  run exposes it; test accumulation first.
- Conditional edges without exhaustive mappings — runtime errors that a
  table-test would have caught.
- Force-answer without the `degraded` flag — the harness grades it as a
  success; the flag is the contract.