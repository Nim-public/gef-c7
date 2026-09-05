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

## 4. The budget's guardrails (how the table stays true)

| Guardrail | Mechanism | Cadence |
|---|---|---|
| p95 re-measurement | the ledger per component | weekly |
| budget breach alarm | gate threshold on p95 | per run |
| new-tool budget check | the surface review (W10) | per tool added |
| token inflation watch | blended cost vs baseline | nightly |

The guardrails are the budget's enforcement — a table without
re-measurement is a snapshot, not a budget. Each guardrail cites its
mechanism (most are gates you built in W11–W13) and its cadence.

## 5. The budget-topology one-page (the architecture's face)

```text
CAPSTONE ARCHITECTURE (W14)
flows:   hot-path chain | long-tail agent | analytics graph
         | interactive graph | voice cascade | codegen loop
budgets: text 4k | data 5k | interactive 3k | voice 3k (p95)
gates:   see gate inventory (W14-04)
triggers: 4, executable (§3)
```

The one-pager is the merged memo's summary — the architecture on a
postcard. It is what the demo, the README, and the reviewers cite; the
detail lives in the four merged memos it links.

## 6. The topology decision tests (each row's evidence test)

| Flow | Decision test |
|---|---|
| hot-path chain | 5 queries through the chain, R@10 ≥ baseline |
| long-tail agent | the ambiguous-class cases route and succeed |
| analytics graph | numeric gate green (exact-match) |
| interactive graph | invariant test (no advance without choice) |
| voice cascade | latency table within budget |
| codegen loop | attempts histogram median ≤2 |

Each topology row carries its evidence test — the decision is verified
by running the test, not by re-reading the memo. The tests are the
architecture's executable form; the memo cites them.

## Exercises

1. Merge the four prior memos into `doc/capstone/architecture.md` —
   budget, topology, triggers; every number cited.
2. Budget-drill: re-measure each component's p50/p95; update the table;
   any component exceeding budget gets a named optimization task.
3. Trigger drill: simulate one trigger firing; the action must be
   executable from the memo alone.
4. Guardrail drill: breach one budget on purpose; the alarm fires; the
   memo's optimization task is created by the drill, not by memory.
5. One-pager drill: render §5 from the merged memo; the postcard and the
   memo must agree on every number.
6. Decision-test drill: run all six decision tests in one command; six
   green lines is the architecture's health check.