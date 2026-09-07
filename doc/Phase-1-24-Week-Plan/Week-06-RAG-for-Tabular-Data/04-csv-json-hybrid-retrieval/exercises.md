# Exercises — CSV/JSON Hybrid Retrieval

Expanded set with worked approaches. The deliverable: the shape-based
router, the serialization pipeline with round-trips, the three-rung
ladder measured, and the cross-store join with staleness detection.

## 1. The decision tree (from 01-decision-tree)

**Task:** implement `route_data`; run it on 6 files of varying shapes;
the boundary drill (49 vs 51 rows) and the misroute drill.

**Worked approach:** the router is measurable at ingest — no model
call. The boundary drill proves the threshold flips; the misroute drill
documents each wrong route's failure mode.

**Pass criterion:** 6/6 routes correct; the boundary flip verified; the
misroute failure modes recorded.

## 2. Serialization (from 02-row-serialization)

**Task:** serialize 100 rows row-major; embed and retrieve "which
product appears most"; the summary chunk drill; the round-trip drill.

**Worked approach:** the serialization quality shows in the hit list —
field names in the text give numbers semantics. The round-trip proves
the metadata (row_key) links back to the warehouse.

**Pass criterion:** the top hits are plausible; the summary chunk is the
top hit for schema questions; the round-trip matches.

## 3. The three-rung ladder (from 03-router-design)

**Task:** implement the ladder; run the battery per rung; the zero-shot
threshold calibrated from the score distribution.

**Worked approach:** the ladder's rungs are measured separately — rules
precision, zero-shot accuracy, agent fall-through rate. The threshold
is set from the score distribution, not assumed.

**Pass criterion:** per-rung accuracy table committed; the threshold
calibrated; fall-throughs logged.

## 4. Cross-store joins (from 04-cross-store-joins)

**Task:** implement `hydrate_row`; the freshness drill (post-ingest
update → stale flag); the deletion drill (honest "no longer exists").

**Worked approach:** the staleness flag is the cross-store join's
honesty — the vector hit is a *pointer*, and the live row is the
truth. The drills prove both paths.

**Pass criterion:** 10/10 hydrated rows fresh; the stale flag fires
after an update; the deletion drill honest.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Router: shapes routed correctly | route table | 3 |
| Serialization: retrieval quality + round-trip | drill results | 4 |
| Ladder: per-rung accuracy, calibrated | ladder table | 4 |
| Cross-store: fresh/stale/deleted handled | join drills | 4 |
| Pin note (hybrid stack) | pin note | 2 |

**Pass bar:** 15/18 to proceed to file 05 (the capstone task). The
cross-store join (4-pointer) is the hybrid bridge's point — the vector
hit and the warehouse fact are the same fact.

## 6. The hybrid pin note (the bridge's manifest)

**Task:** consolidate the hybrid stack in `reports/sdk-versions.md`:
the decision-tree thresholds, the serialization contract, the router
ladder, and the cross-store join — one block.

**Worked approach:** the hybrid bridge's manifest lists the router's
thresholds, the serialization contract, and the staleness policy — each
citing its drill.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## Pitfalls recap

- Rows serialized without field names — "16.9" embeds like any float;
  the field names give semantics.
- Stale chunks trusted as current — the hydration join fetches live
  rows; the staleness flag is the honesty.
- Router rungs skipped to "just use the agent" — the ladder's cheap
  rungs handle the obvious cases; the agent is for the rest.