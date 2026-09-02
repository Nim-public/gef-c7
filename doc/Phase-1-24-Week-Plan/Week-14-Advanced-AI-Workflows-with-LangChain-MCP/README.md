# Week 14 — Advanced AI Workflows with LangChain & MCP

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 12 Dec, 7–10 PM IST (Session 1) · Sun 13 Dec, 7–10 PM IST (Session 2) · Office Hours Thu 17 Dec, 7–8 PM IST

**Practice build:** [06-practice-langchain-mcp.md](06-practice-langchain-mcp.md)

---

## Why this week matters

LangChain is the integration layer your capstone has been missing: prompt templates, chains, agents, document loaders, and — via its **MCP adapter** — a standardized way to reuse the tool server you built in Week 10 across every framework you've tried. The two session projects (CSV Analyzer, Code Review Agent, Agentic RAG, Personal Workflow Assistant) are four templates you will re-implement against your own capstone data.

## What you will be able to do after this week

- [ ] Compose LangChain primitives: prompt templates, LCEL chains, structured output, agents
- [ ] Build a CSV Analyzer (chat-with-data, profiling, AI analysis, visual insights)
- [ ] Build a Code Review Agent (bugs, performance, refactoring, reports)
- [ ] Build agentic RAG with routing and multi-step reasoning in LangChain/LangGraph
- [ ] Connect your Week 10 MCP server through LangChain's MCP adapter and build a workflow assistant across file/GitHub/Slack/database MCP servers
- [ ] Position LangChain vs the four frameworks you've already used (W10–12)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-langchain-foundations.md](01-langchain-foundations.md) | Prompt templates, LCEL, structured output, `create_agent` | 3 h |
| 2 | [02-project-csv-analyzer.md](02-project-csv-analyzer.md) | Session Project 1 — chat with your data | 3 h |
| 3 | [03-project-code-review-agent.md](03-project-code-review-agent.md) | Session Project 2 — review/refactor/report | 3 h |
| 4 | [04-agentic-rag-langchain.md](04-agentic-rag-langchain.md) | Agentic RAG: routing, multi-step, self-improving | 3 h |
| 5 | [05-workflow-assistant-mcp.md](05-workflow-assistant-mcp.md) | LangChain + MCP: files, GitHub, Slack, SQL | 3–4 h |
| 6 | [06-practice-langchain-mcp.md](06-practice-langchain-mcp.md) | Capstone MCP integration (practice) | 3 h |

## Environment setup

```powershell
pip install langchain langchain-openai langchain-community langgraph
pip install langchain-mcp-adapters          # file 05
pip install pandas matplotlib mcp
```

## Self-check before Week 15

1. An LCEL chain `prompt | model | parser` fails mid-run — where do you add retries and fallbacks, and why *there*?
2. Your CSV Analyzer's SQL/pandas tool misread a date column. Which layer catches it — template, tool, or output model?
3. What does LangChain's MCP adapter replace from your W10/W11 code — and what does it *not* cover?
4. "Self-improving pipeline" in agentic RAG: which component actually *learns*, and what's the honest version of that claim?
5. Which of your four frameworks (SDK, Agno, CrewAI, LangChain) fits the capstone's *final* architecture best — and which one artifact from each would you keep?
