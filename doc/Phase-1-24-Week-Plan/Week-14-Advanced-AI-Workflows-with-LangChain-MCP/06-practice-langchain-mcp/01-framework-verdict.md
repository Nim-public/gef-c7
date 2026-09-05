# The Framework Verdict — Five Frameworks, One Decision

**What you'll learn:** the final table: hand-rolled (W10), OpenAI SDK
(W11), Agno (W12), CrewAI (W12), LangChain/LangGraph (W13–14) —
outcome parity where applicable, and the one-mechanism decision with
ported ideas.

## 1. The five-framework table

| Capability | W10 | W11 | Agno | CrewAI | LangChain/Graph |
|---|---|---|---|---|---|
| loop | 50 lines, yours | `Runner` | `Agent.run` | crew runtime | graph runtime |
| tools | registry | decorators | Toolkit | tool assignment | `@tool` |
| typed output | manual | strict | `output_schema` | `output_pydantic` | `response_format` |
| guardrails | gates | tripwires | flags | tasks | middleware |
| knowledge | your stack | BYO | native | RAG tools | BYO (your stack) |
| multi-agent | — | handoffs | `Team` | crews | subgraphs/supervisor |
| HITL | gates | interrupts | flags | human tasks | interrupts |
| observability | harness | traces | AgentOS | verbose | streams+LangSmith |

Fill the parity columns from your runs (W11 file 06-02, W12 file 06-04,
W14 file 04-04) — cells without runs are marked "not compared", never
guessed.

## 2. The decision (unchanged, now final)

```markdown
## Final framework decision (W14)
- Core loop: OpenAI Agents SDK (W11 port; battery-green since W11).
- Linear chains: LCEL (W14) — prompt/model/parse pipelines.
- Interactive/HITL flows: LangGraph (W13) — interrupts + checkpoints.
- Data agent path: Agno (W12) — Knowledge wrap + toolkits.
- CrewAI: evaluated; role discipline ported as instruction slots.
- ALL frameworks share: trajectory store, eval sets, batteries,
  budget rules, gate policies.
```

The decision survives five weeks of evidence: the *mechanisms* split by
job; the *policies* never fragment. Every framework week ended with the
same sentence, and it still holds.

## 3. The ported-ideas ledger, final

| Idea | Origin | Lives in |
|---|---|---|
| knowledge-hybrid wrap | Agno | the data agent |
| role/goal/backstory slots | CrewAI | instruction slots |
| middleware layers | LangChain | retry/fitter/gates |
| interrupts + checkpoints | LangGraph | HITL flows |
| strict typed outputs | OpenAI SDK | every final answer |

The ledger is the framework arc's yield: five weeks, five mechanisms
audited, five ideas kept. The ideas travel; the migrations didn't
happen.

## 4. The per-framework "when to reach for it" page (the verdict's user guide)

| Reach for | When | Cite |
|---|---|---|
| W10 patterns | debugging any framework's magic | the loop is the substrate |
| W11 SDK | production QA agent with gates | W11 battery, W13 parity |
| Agno | fast data agents with Knowledge | W12-02 parity loop |
| CrewAI | role-play content pipelines | W12-06 bake-off |
| LangChain/LCEL | linear chains in any system | W14-02 parity |
| LangGraph | interactive, stateful, HITL | W13 interrupts |

The user guide is the verdict's practical form: not "which framework
won" but "which framework for which job, with the evidence link". Every
row's cite is a battery or a parity run from the program.

## Exercises

1. Fill the table's parity columns from your runs; mark the not-compared
   cells honestly.
2. Decision drill: re-affirm or revise the §2 decision citing the final
   table — the same two cited numbers rule.
3. Ledger drill: verify every ported idea has a living test (a run or a
   battery row); dead ideas get pruned from the ledger.
4. User-guide drill: for each "reach for" row, name the artifact a
   teammate would read to start — the guide's links must resolve.
5. Appendix drill: build §5's evidence appendix; link every row to its
   artifact; a reviewer clicks three at random — all must resolve.

## 5. The verdict's evidence appendix (where each number lives)

| Table row | Evidence artifact |
|---|---|
| W11 column | `reports/comparison.md` (W11-06) |
| Agno column | `reports/framework-parity.md` + W12 eval runs |
| CrewAI column | W12-06 bake-off report |
| LangChain column | W14-04 parity table |
| tokens p50 | the merged trajectory store |

The evidence appendix is the table's audit trail — every cell names the
artifact that produced it. The five-framework verdict is the program's
most-cited page; its every number is checkable in one hop.

## Pitfalls

- Cells filled from documentation instead of runs — the table's value is
  its evidence.
- Five frameworks shipping in the capstone — one mechanism per job; the
  decision paragraph lists which and why.
- The ledger keeping ideas whose tests died — prune or re-test; the
  ledger is a living record.