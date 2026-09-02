# Week 12 — Building AI Agents with phiData (Agno)

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 28 Nov, 7–10 PM IST (Session 1) · Sun 29 Nov, 7–10 PM IST (Session 2) · Office Hours Thu 3 Dec, 7–8 PM IST

**Weekly task:** [06-capstone-task-crewai-workflow.md](06-capstone-task-crewai-workflow.md)

---

## Why this week matters

W10 built the agent loop by hand; W11 used a lean SDK. This week adds **batteries**: phiData/Agno ships knowledge bases, vector-DB integration, memory, playground UI, and prebuilt toolkits — the fastest path from "my capstone data" to "working agent with a UI". The formal task also introduces **CrewAI** (role-based multi-agent crews), giving you the third and fourth points on the framework comparison you've been building since W10.

## What you will be able to do after this week

- [ ] Build Agno agents (model, instructions, tools, knowledge) and run them locally and in the playground
- [ ] Wire data ingestion from RDBMS/CSV/JSON into agent knowledge (reusing W6's stores)
- [ ] Write custom toolkits wrapping your capstone systems (W9 `search_knowledge`, W6 SQL)
- [ ] Build an analytics agent over financial/stock data with charts and guarded SQL
- [ ] Implement agentic RAG: the agent decides retrieve vs SQL vs clarify
- [ ] Build a CrewAI multi-agent workflow (the formal task) and evaluate it against your W11 single agent

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-agno-introduction.md](01-agno-introduction.md) | Agno/phiData, first agent, playground, W11 mapping | 3 h |
| 2 | [02-knowledge-and-databases.md](02-knowledge-and-databases.md) | Knowledge bases, LanceDB, RDBMS/CSV/JSON ingestion | 3 h |
| 3 | [03-custom-tools-toolkits.md](03-custom-tools-toolkits.md) | Custom toolkits over your capstone systems | 2–3 h |
| 4 | [04-analytics-agent-financial.md](04-analytics-agent-financial.md) | The financial/stock analytics agent (session-2 build) | 3–4 h |
| 5 | [05-agentic-rag-with-phidata.md](05-agentic-rag-with-phidata.md) | Agent-decided retrieval vs SQL vs clarify | 2–3 h |
| 6 | [06-capstone-task-crewai-workflow.md](06-capstone-task-crewai-workflow.md) | CrewAI multi-agent workflow (formal task) | 4 h |

## Environment setup

```powershell
pip install agno lancedb sqlalchemy pandas
pip install yfinance            # session-2 financial data
# optional playground:
pip install "agno[playground]"
```

> **Naming note:** the framework was `phidata`, renamed to **Agno** (same authors; `from agno...` imports in current versions). Course materials may say phiData — the concepts map 1:1. Verify the current API against the Agno docs before writing production code (this file's examples follow the current `agno` package).

## Self-check before Week 13

1. Agno `Knowledge` + `search_knowledge=True` vs your W9 hybrid retriever: what does the framework add, what does it hide?
2. Your analytics agent answered a question with a number that's not in the DB. Which two guards should have caught it (W6-03 layers, W10-02 rules)?
3. What does the playground give you that `print_response` doesn't — and what does the playground *hide*?
4. CrewAI `role/goal/backstory` maps to which W11 SDK primitive — and what does the crew's `process` parameter control?
5. For your capstone: which one workflow would you hand to a crew rather than a single agent — and why (name the roles)?
