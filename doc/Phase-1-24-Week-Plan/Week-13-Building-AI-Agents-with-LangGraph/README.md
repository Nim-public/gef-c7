# Week 13 — Building AI Agents with LangGraph

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 5 Dec, 7–10 PM IST (Session 1) · Sun 6 Dec, 7–10 PM IST (Session 2) · Office Hours Thu 10 Dec, 7–8 PM IST

**Weekly task:** [05-capstone-task-phidata-agent.md](05-capstone-task-phidata-agent.md) · **Optional deepening:** [06-checkpointing-human-in-loop.md](06-checkpointing-human-in-loop.md)

---

## Why this week matters

Every framework so far hid the control flow inside a loop (W10) or a convention (W11/W12). **LangGraph makes the control flow itself the artifact**: an explicit, inspectable, checkpointable graph of states, nodes, and edges. The schedule's two session-1 projects (Story Generator, Support Ticket Router) are perfect teaching shapes, and the session-2 loop (code-gen → self-repair) is the pattern your capstone's hardest flows need. This is also the week your W10-04 HITL design becomes a first-class graph feature.

## What you will be able to do after this week

- [ ] Define `StateGraph` state with TypedDict/Pydantic, nodes as functions, edges and conditional edges
- [ ] Compile, invoke, and stream a graph; read its execution trace
- [ ] Build the Story Generator project (state-driven branching)
- [ ] Build the Customer Support Ticket Router mapped to *your* capstone (intent → urgency → KB → escalation)
- [ ] Build a code-generation & self-repair loop (plan → write → test → debug)
- [ ] Add checkpointing, human-in-the-loop interrupts, and time-travel debugging
- [ ] Integrate your phiData/Agno agent for data-intensive tasks (the formal task)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-langgraph-foundations.md](01-langgraph-foundations.md) | State, nodes, edges, conditional edges, invoke/stream | 3–4 h |
| 2 | [02-project-story-generator.md](02-project-story-generator.md) | Session Project 1 — state-driven narrative | 2–3 h |
| 3 | [03-project-support-ticket-router.md](03-project-support-ticket-router.md) | Session Project 2 — mapped to your capstone | 3–4 h |
| 4 | [04-team-agents-codegen-loop.md](04-team-agents-codegen-loop.md) | Self-repair loop + supervisor/team patterns | 3 h |
| 5 | [05-capstone-task-phidata-agent.md](05-capstone-task-phidata-agent.md) | phiData agent for data-intensive tasks (formal task) | 3 h |
| 6 | [06-checkpointing-human-in-loop.md](06-checkpointing-human-in-loop.md) | Checkpoints, interrupts, HITL, time travel | 2 h |

## Environment setup

```powershell
pip install langgraph langchain langchain-openai
```

## Self-check before Week 14

1. In your ticket-router graph, which edge is *conditional* — and what state field does its condition read?
2. Your code-repair loop ran 9 iterations without passing tests. Which two graph mechanisms bound it (edge condition, checkpointer/limits)?
3. A human approval interrupts the graph. What exactly is persisted when the graph pauses — and how does the run resume?
4. LangGraph state vs W11 sessions vs W10 scratchpad — which problem does each solve in one sentence each?
5. Where does your capstone *need* an explicit graph vs the W11 SDK's implicit flow? Name one node where a human should interrupt.
