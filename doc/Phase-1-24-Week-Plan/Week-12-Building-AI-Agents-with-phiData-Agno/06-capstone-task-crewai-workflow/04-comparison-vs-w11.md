# Comparison vs W11 — Same Cases, All Three Frameworks

**What you'll learn:** the final framework table: the same eval set run
through hand-rolled (W10), OpenAI SDK (W11), Agno (W12-01), and CrewAI
(W12-06) — with the decision that ends the framework question for the
capstone.

## 1. The four-way table

| Task class | W10 | W11 SDK | W12 Agno | W12 CrewAI |
|---|---|---|---|---|
| simple lookup | success | success | success | success |
| multi-hop | success | success | success | success (seq.) |
| numeric exact | n/a (no SQL) | via tools | success (dual) | via tools |
| refusal honesty | strong | strong | strong | backstory-dependent |
| tokens p50 | 3.8k | 3.6k | 3.7k | 4.2k |
| lines of orchestration | ~50 | ~0 | ~0 | ~20 (crew setup) |

Fill from runs, not vibes — the W11 protocol (fixed corpus, config,
repeats) applies to all four columns.

## 2. Capability matrix (the honest summary)

| Capability | W10 | W11 | Agno | CrewAI |
|---|---|---|---|---|
| loop control ownership | yours | SDK | SDK | framework |
| structured outputs | manual | native strict | `output_schema` | `output_pydantic` |
| guardrails/tripwires | manual gates | native | flags+instructions | tasks+roles |
| knowledge integration | your stack | BYO | native `Knowledge` | RAG tools |
| UI | yours | yours | Playground/AgentOS | limited |
| tracing | your harness | native + merge | AgentOS | verbose logs |
| context budgeting | yours | yours | yours | yours |

The constant rows (budgeting, harness) are the program's thesis: the
*policies* are portable; the *mechanisms* are fashion.

## 3. The final framework decision

| If the capstone's center of gravity is... | Build on |
|---|---|
| grounded QA over your corpus, tight eval gates | W11 SDK (gates, strict outputs) |
| knowledge-first agents, fast UI | Agno (Knowledge + Playground) |
| multi-role content/analysis pipelines | CrewAI (roles are native) |
| teaching the mechanics | W10 patterns under everything |

The GEF C7 capstone's answer, from your own tables: the W11 SDK agent
with your harness — because the eval gates, typed outputs, and trace
merge are already built and battery-tested. The other frameworks'
*ideas* (Agno's Knowledge wrap, CrewAI's role splits) port as patterns,
not as migrations.

## 4. The capstone architecture paragraph (write it now)

```markdown
## Agent framework (decided W12)
- Core loop: OpenAI Agents SDK (W11 port; battery-green).
- Ported ideas: Agno's Knowledge-hybrid wrap (W12-02); CrewAI's
  role/goal/backstory discipline as instruction slots (W12-06).
- Rejected for now: CrewAI hierarchical (manager tax vs known order);
  Agno Team (same topology, already in SDK).
- Revisit: if role-play delegation dominates, re-evaluate CrewAI.
```

## Exercises

1. Run the eval set through the CrewAI crew; produce the fourth column
   of §1 with real numbers.
2. Capability-matrix drill: fill every cell from evidence (a run, a
   test, or "not built"); any gap becomes a scoping note for Week 13+.
3. Decision drill: write the §4 paragraph citing the framework table
   and your two best numbers — the standing decision for the capstone.

## 5. The ported-ideas ledger (the comparison's real yield)

| Idea | Origin | Where it lives in your build |
|---|---|---|
| Knowledge-hybrid wrap | Agno | `Knowledge` over your LanceDB (W12-02) |
| role/goal/backstory slots | CrewAI | instruction slots in the W11 agent |
| `Team` delegation | Agno | pattern note; SDK agents-as-tools covers it |
| Flow state objects | CrewAI | your chain's typed seams |

The ledger is the framework week's actual deliverable: three frameworks
audited, one mechanism chosen, and the *ideas* that earned their keep
ported as patterns into the chosen build. Ideas travel; migrations are
optional.

## Pitfalls

- Four frameworks, four half-ported agents — pick the mechanism; the
  comparison exists to inform *one* choice.
- CrewAI backstories trusted as safety — the tool layer enforces; roles
  are prompts (file 02's tests).
- Framework comparisons without the protocol header — same rules as
  every comparison since W9.