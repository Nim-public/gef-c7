# Shared-Interface Comparison — Both Engines, One Harness

**What you'll learn:** the comparison: both retrieval engines (your W9
stack and LlamaIndex) behind one interface, evaluated by one harness on
one eval set — the W12-04 comparison protocol, engine edition.

## 1. The shared interface

```python
class RetrievalEngine(Protocol):
    def retrieve(self, query: str, k: int = 5) -> list[dict]: ...
    # returns [{"unit_id": ..., "text": ..., "score": ...}]
```

| Engine | Implements |
|---|---|
| W9 stack | `hybrid_retrieve` wrapped |
| LlamaIndex | the query engine's retriever wrapped |

The shared interface is the Encoder Protocol pattern (W8 file 01-01)
applied to retrieval engines: one signature, two implementations, one
harness.

## 2. The comparison protocol

| Element | Spec |
|---|---|
| eval set | the 15-case set, v-frozen |
| queries | both engines, same k |
| metrics | R@5, MRR, faithfulness (given the nodes) |
| runs | 1 (retrieval is deterministic) + repeats for stochastic parts |
| verdict | per metric, with the delta |

```python
def compare_engines(engines: dict[str, RetrievalEngine],
                    queries: list[str], k: int = 5) -> pd.DataFrame:
    rows = []
    for name, eng in engines.items():
        for q in queries:
            hits = eng.retrieve(q, k)
            rows.append({"engine": name, "query": q,
                         "r5": recall_at_k(hits, gold(q), 5)})
    return pd.DataFrame(rows)
```

The protocol is the W11 comparison table's structure — one variable
(the engine), shared everything else. The verdict is per metric with
the delta.

## 3. The comparison table

| Metric | W9 stack | LlamaIndex | Δ | Cause |
|---|---|---|---|---|
| R@5 (charts) | 0.78 | 0.71 | −0.07 | chunking differs |
| R@5 (text) | 0.85 | 0.84 | −0.01 | parity |
| MRR | 0.71 | 0.66 | −0.05 | ranking differs |
| faithfulness (same nodes) | equal | equal | — | same synthesizer |

The expected shape: LlamaIndex slightly behind *unless* its chunking is
matched to yours — the chunker is the difference (file 02's pin). With
matched chunking and embedder, the engines converge.

## 4. The comparison report (the protocol's output)

```markdown
# Engine comparison — eval-set v3 — [date]

| metric | W9 stack | LlamaIndex | Δ | cause |
|---|---|---|---|---|
| R@5 charts | 0.78 | 0.74 | −0.04 | chunking |
| R@5 text | 0.85 | 0.84 | −0.01 | parity |
| MRR | 0.71 | 0.68 | −0.03 | ranking |
| faith (same nodes) | 0.91 | 0.91 | 0 | same synthesizer |

protocol: 15 cases, k=5, chunk-matched, embedder pinned
verdict: parity within noise after chunk-matching; the retriever's
ranking is the remaining delta
```

The report is the protocol's output — the table, the header, and the
verdict. It is the ship/adopt/reject decision's (file 04) input, and
its every number is regenerable by the comparison script. The W10-05
rubric discipline applies per slice: every weakness gets an owner, an
action, and a re-measurement.

## 5. The comparison protocol checklist (the run's preconditions)

```text
[ ] both engines consume the same corpus version (manifest hash)
[ ] both use the same embedder (pinned, from Settings)
[ ] both use the same chunking (matched, from file 02)
[ ] same k, same metric implementations, same gold labels
[ ] the eval-set version is frozen (file 01-04 of this week)
```

The preconditions checklist is the comparison's validity — each row is
a variable that must be held constant. Any unchecked row is a
confound; the delta is then unattributable.

## Exercises

1. Implement the shared interface for both engines; run the comparison;
   produce the table with the Δ column and causes.
2. Chunk-matching drill: configure LlamaIndex's chunker to your W4
   settings; re-run; the gap should narrow — the chunker's effect,
   isolated.
3. Synthesis-drill: with identical retrieved nodes, compare both
   synthesizers' faithfulness — separating retrieval from generation
   quality.
4. Report drill: render §4; the header carries the protocol; the verdict
   cites the table.
5. Delta-drill: attribute the largest Δ — chunking, embedder, or
   ranking — with an isolated experiment per hypothesis.
5. Delta-drill: attribute the largest Δ — chunking, embedder, or
   ranking — with an isolated experiment per hypothesis.

## Pitfalls

- Comparing engines with different chunking/embedders — the variables
  must be isolated or the delta is unattributable.
- One engine with access to metadata the other lacks — shared interface,
  shared data.
- Verdicts from small samples — the eval set's size is the protocol's
  power; state the n.