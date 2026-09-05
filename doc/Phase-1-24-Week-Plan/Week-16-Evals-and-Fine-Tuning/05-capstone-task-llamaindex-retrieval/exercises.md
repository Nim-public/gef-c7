# Exercises — LlamaIndex Retrieval Comparison

Expanded set with worked approaches. The deliverable: the four LlamaIndex
objects wired, settings pinned, the shared-interface comparison run, and
the evidence-based verdict.

## 1. Essentials wiring (from 01-llamaindex-essentials)

**Task:** build the four objects over a corpus subset; query it; verify
the metadata round-trip (unit_ids in nodes).

**Worked approach:** the metadata round-trip is the citation life-line —
nodes without `unit_id` cannot be cited, and the audit (file 04 of W13)
would reject every answer. The wiring's acceptance test is the
round-trip.

**Pass criterion:** queries answered with node metadata intact; the
unit_ids resolvable to manifest rows.

## 2. Settings pinning (from 02-settings-pinning)

**Task:** write the pinning block; run the settings audit; the unpin
drill (one setting deliberately default) and the parity loop
(W12-02-01) against your W9 stack.

**Worked approach:** the audit is the pin's enforcement — the unpin
drill proves the audit catches the drift. The parity loop proves the
pinned settings reproduce your stack's retrieval.

**Pass criterion:** audit green; the unpin drill red; the parity loop
5/5.

## 3. The engine comparison (from 03-shared-interface-comparison)

**Task:** implement the shared interface for both engines; run the
comparison protocol; produce the table with Δ and causes; the
chunk-matching drill.

**Worked approach:** the chunk-matching drill isolates the chunker's
effect — with matched chunking and embedder, the engines converge; the
remaining delta is the retriever's ranking, honestly attributed.

**Pass criterion:** the table committed with Δ and causes; the
chunk-matching effect measured.

## 4. The verdict (from 04-ship-adopt-reject)

**Task:** write the ship/adopt/reject memo citing the comparison; the
reversibility drill (disable the adopted component; the eval re-runs
green on the W9 path).

**Worked approach:** the reversibility drill is the adopt decision's
safety net — an adopted component that cannot be disabled is a
dependency trap.

**Pass criterion:** the memo committed; the reversibility drill green.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Essentials wired + metadata round-trip | drill | 3 |
| Settings pinned + audit + parity | pin tests | 4 |
| Comparison table with Δ and causes | comparison report | 4 |
| Verdict memo with reversibility | decision memo | 4 |
| Pin note updated | pin note | 2 |

**Pass bar:** 14/17 to proceed to file 06 (demo-day prep). The
comparison (4-pointer) is the week's measurement — evidence-based
adoption or a principled rejection.

## Pitfalls recap

- Default embedders silently used — the space mismatch is the silent
  killer; the pin's audit is the guard.
- Metadata not round-tripping — citations die; the round-trip test is
  the life-line.
- Verdicts without reversibility — adoption without an exit is a trap;
  the drill is the exit.