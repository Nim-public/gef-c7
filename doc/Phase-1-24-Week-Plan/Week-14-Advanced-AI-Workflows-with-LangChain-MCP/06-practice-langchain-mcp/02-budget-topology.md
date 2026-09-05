# Tool Budget & Topology — The Decisions, Finalized

**What you'll learn:** the capstone's architecture record: the tool
budget per component, the topology per flow, and the revisit triggers —
the W10 boundary memo, W11 verdict, W12 framework record, and W13 ADRs,
merged into one page.

## 1. The tool budget (per component)

| Component | Tools | Token budget/query | p95 latency |
|---|---|---|---|
| text RAG | retrieve, get_unit_text | 4k | 3 s |
| data agent | CorpusTools + Analytics | 5k | 4 s |
| interactive flows | gated tools | 3k | human-paced |
| voice | text-RAG subset | 3k | 2.5 s |

The budget table merges every week's ledgers (W9-04, W11 file 04, W12
file 04-04) — one page, per component. The Week-10 tool-surface policy
(read-only first) is the budget's foundation row.

## 2. The topology decisions (per flow)

| Flow | Topology | Justification |
|---|---|---|
| hot-path QA | chain (LCEL) | 80% of queries, fixed shape |
| long-tail QA | agent (create_agent) | dynamic composition |
| analytics | graph (verify nodes) | numeric grounding needs structure |
| interactive | interrupt graph | human gates |
| codegen | self-repair cycle | bounded repair |

The topology table is the W10 boundary memo, W11 verdict, and W13 ADRs
— merged. Every row cites its measured crossover or distribution
(number, not vibes).

## 3. The revisit triggers (the standing list)

| Trigger | Threshold | Action |
|---|---|---|
| a chain's class grows beyond its shape | R@10 drop >0.05 | promote to agent |
| supervisor overhead >30% on a class | cost table | collapse to chain |
| voice latency > budget twice | p95 table | revisit streaming stack |
| skip-rate on domain queries >5% | instrumentation | harden the floor |

Every trigger names its metric and threshold — the same discipline as
every memo since W10. The triggers are the architecture's maintenance
contract.

## Exercises

1. Merge the four prior memos into `doc/capstone/architecture.md` —
   budget, topology, triggers; every number cited.
2. Budget-drill: re-measure each component's p50/p95; update the table;
   any component exceeding budget gets a named optimization task.
3. Trigger drill: simulate one trigger firing; the action must be
   executable from the memo alone.