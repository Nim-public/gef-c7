# Week 11 — Building AI Agents with OpenAI Agents SDK

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 21 Nov, 7–10 PM IST (Session 1) · Sun 22 Nov, 7–10 PM IST (Session 2) · Office Hours Thu 26 Nov, 7–8 PM IST

**Practice build:** [06-practice-agents-sdk-capstone.md](06-practice-agents-sdk-capstone.md)

---

## Why this week matters

Week 10 taught you the agent loop by hand; this week you learn what a framework buys you — typed primitives, handoffs, guardrails, sessions, and built-in tracing — by rebuilding your agent with the **OpenAI Agents SDK** and comparing honestly against your hand-rolled version. The patterns here (handoffs, guardrail tripwires, sessions) are the vocabulary every later framework week (phiData, LangGraph, LangChain) will reuse.

## What you will be able to do after this week

- [ ] Set up the SDK, run an agent, and read `RunResult`/trace output
- [ ] Build tools with `@function_tool` (typed args, docstrings-as-descriptions)
- [ ] Orchestrate multi-agent flows with handoffs and delegation
- [ ] Add input/output guardrails with tripwires (reusing the W3-02 battery)
- [ ] Persist conversations with sessions; debug via traces
- [ ] Sketch a voice-agent stack and its latency budget
- [ ] Port your Week 10 practice to the SDK and quantify the differences

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-agents-sdk-quickstart.md](01-agents-sdk-quickstart.md) | Install, Agent/Runner anatomy, sessions, tracing | 3 h |
| 2 | [02-tools-handoffs-guardrails.md](02-tools-handoffs-guardrails.md) | function_tool, handoffs, guardrail tripwires | 3–4 h |
| 3 | [03-multi-agent-orchestration.md](03-multi-agent-orchestration.md) | Router→specialist, chaining, delegation patterns | 3 h |
| 4 | [04-voice-agents.md](04-voice-agents.md) | STT→agent→TTS stack, realtime APIs, latency budgets | 2 h |
| 5 | [05-observability-eval-agents.md](05-observability-eval-agents.md) | Traces/spans, debugging, trajectory regression suites | 2–3 h |
| 6 | [06-practice-agents-sdk-capstone.md](06-practice-agents-sdk-capstone.md) | Port W10's agent; hand-rolled vs SDK comparison | 4 h |

## Environment setup

```powershell
pip install openai-agents
setx OPENAI_API_KEY "sk-..."     # or your .env + dotenv pattern (W1-07)
```

W10's stack (fastmcp, pytest) stays installed — the SDK consumes your MCP server in file 03's exercises.

## Self-check before Week 12

1. What does `Runner.run` do between your prompt and `final_output` — list the four loop steps from the SDK's own docs.
2. A handoff happens mid-run. Which agent's input guardrails ran — and where does the user's context live after the switch?
3. Your guardrail tripped. What exception does the caller see, and what should your API return to the user?
4. Voice p95 budget is 1.5 s. Which stage blows it first — STT, the agent loop, or TTS — and which design (turn-based vs realtime) fixes it?
5. Compared to your Week 10 loop: what did the SDK remove (lines), what did it *add* (capabilities), and where did it hide something you now can't see? (You wrote this prediction in W10 — check it.)
