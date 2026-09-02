# Week 10 — Introduction to Agentic AI + MCP

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 14 Nov, 7–10 PM IST (Session 1) · Sun 15 Nov, 7–10 PM IST (Session 2) · Office Hours Thu 19 Nov, 7–8 PM IST · *first week after the break (7–8 Nov)*

**Practice build:** [06-practice-first-mcp-agent.md](06-practice-first-mcp-agent.md)

---

## Why this week matters

The retrieval arc (Weeks 4–9) built your capstone's *knowledge*; the agentic arc (Weeks 10–14) gives it *hands*. This week you build the agent loop yourself — no framework — so that when the OpenAI Agents SDK (W11), phiData (W12), LangGraph (W13), and LangChain (W14) arrive, you know exactly which 40 lines each framework is hiding. MCP (Model Context Protocol) then turns your Week 5–6 retrieval system into a tool that *any* MCP client can call.

## What you will be able to do after this week

- [ ] Define an agent precisely (LLM + tools + memory + loop) and explain what it can/can't do
- [ ] Implement the ReAct-style agent loop from scratch: plan → act → observe → iterate
- [ ] Build tool schemas, registries, and execution with validation
- [ ] Add memory: conversation history, scratchpad, and vector-backed recall
- [ ] Stand up an MCP server with FastMCP exposing your capstone tools; test it with a real LLM
- [ ] Measure agent runs: task success, steps, tool errors, cost — and apply best practices
- [ ] Apply human-in-the-loop gates and LLM-as-judge evaluation to trajectories

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-agents-foundations.md](01-agents-foundations.md) | What agents are, the loop, a no-framework agent | 3–4 h |
| 2 | [02-tools-and-memory.md](02-tools-and-memory.md) | Tool schemas/execution, memory taxonomy, context budget | 3 h |
| 3 | [03-mcp-servers-fastmcp.md](03-mcp-servers-fastmcp.md) | MCP protocol, FastMCP server + client, capstone tools | 3 h |
| 4 | [04-measuring-agents-patterns.md](04-measuring-agents-patterns.md) | Trajectory eval, best practices, HITL, LLM-as-judge | 2–3 h |
| 5 | [05-prompt-context-engineering-agentic.md](05-prompt-context-engineering-agentic.md) | Agentic prompts, observation formatting, context budgeting | 2 h |
| 6 | [06-practice-first-mcp-agent.md](06-practice-first-mcp-agent.md) | Agent + your MCP tools + 10-task eval (practice) | 4 h |

## Environment setup

```powershell
pip install fastmcp openai tiktoken python-dotenv pytest
```

## Self-check before Week 11

1. In your hand-rolled loop, what exactly stops it from running forever — and what does the SDK call this?
2. Your agent called `sql_query` with a typo'd column name. Trace the three layers that should catch it (W6's validator, the loop, the eval) — what does each do?
3. Why does MCP exist — what breaks without a protocol when 5 agent apps each need your RAG tool?
4. A trajectory succeeded (right answer) but took 9 steps and $0.11. Success alone isn't the metric — name the other two dimensions you'd report.
5. Which of your capstone tasks are agent-shaped (dynamic tool selection) vs pipeline-shaped (fixed RAG flow)? Name one of each.
