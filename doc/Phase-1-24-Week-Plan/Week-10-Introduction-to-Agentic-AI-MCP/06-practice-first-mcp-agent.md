# 06 — Practice: Your First MCP-Powered Agent

> Week 10 index: [README.md](README.md) · **Due: before Week 11 (by 21 Nov)**

*(No formal task row in the schedule — this practice build cements the hand-rolled agent before the SDK week, and leaves the capstone with a working tool server.)*

---

## 1. Deliverable

```
agent/
  agent.py               # the hand-rolled loop (files 01/05)
  registry.py            # ToolRegistry + validated tools (file 02)
  capstone_mcp.py        # FastMCP server exposing search_knowledge + sql_query (file 03)
  tests/
    test_tools.py        # client battery for the MCP server (file 03 ex. 2)
    test_agent.py        # trajectory eval: 10 labeled tasks (file 04)
  eval/
    agent_cases.jsonl    # 10 tasks: goal + expected tools + expected answer shape
    results.md           # metrics table + judge scores + phrasing A/B notes
  README.md              # architecture, decisions, failure analysis
```

Demo: one multi-tool trajectory (search → SQL → cited answer), one injection deflection, one HITL denial, plus the MCP tools callable from an external client.

## 2. Requirements (graded)

### The agent (files 01+05 composed)
- [ ] Hand-rolled loop: max steps, FINAL termination, forced-decision nudge
- [ ] 7-rule constitution in `prompts/agent.system.md`, loaded at startup
- [ ] `ToolRegistry` with jsonschema validation; errors as instructive observations
- [ ] Scratchpad tools (`save_note`/`read_notes`) + episodic recall (`recall_similar` in the first system message)
- [ ] Context fitter active; token budget logged per run

### The MCP server (file 03)
- [ ] `capstone_mcp.py` with ≥2 tools wrapping W9's `search_knowledge` and W6's `sql_query`
- [ ] FastMCP client battery passing (happy paths + injection probe + no-match caveat)
- [ ] One external-client demo (Claude Desktop config, or the Agents-SDK preview from file 03 §3)

### Measurement (file 04)
- [ ] 10-task eval set with expected tools + answer shape
- [ ] Metrics: success rate, steps p50/p95, tokens p95, tool-error rate, guard trips
- [ ] LLM-judge scores (tool_choice/efficiency/grounding) with judge model pinned
- [ ] HITL gate on one fake write tool, with a logged denial

## 3. The 10-task eval set (design guide)

| # | Goal shape | Expected tools | Notes |
|---|---|---|---|
| 1–3 | single-tool prose questions | search | tests selection |
| 4–5 | single-tool numeric | sql | date phrasing included |
| 6–7 | multi-tool (doc + number) | search → sql (either order) | the flagship demos |
| 8 | unanswerable | any → insufficiency | "I don't have that information." |
| 9 | injection-flavored | must deflect | W3-02 battery style |
| 10 | HITL-triggering | gate fires | fake `issue_refund` |

Score success = right answer shape + right tool family used. Log everything to `data/agent_runs.jsonl` — this file is reusable in Week 11 (SDK comparison) and Week 15 (reliability).

## 4. Rubric

| Area | Weight |
|---|---|
| Agent loop correctness (termination, validation, observation quality) | 25% |
| MCP server + client battery + external-client demo | 25% |
| Measurement: metrics table + judge + HITL | 25% |
| Prompt/context engineering evidence (constitution, phrasing A/B) | 15% |
| README: decisions, failure modes, W11 comparison plan | 10% |

## 5. README architecture section (answer explicitly)

1. **Loop spec**: termination conditions, budgets (steps/tokens), the failure paths you handle
2. **Tool surface**: which capstone systems became tools, their safety rails (W6/W9 layers)
3. **Constitution**: your 7 rules and which failures each prevents (with trajectory evidence)
4. **Metrics**: the table, plus the *worst* trajectory dissected step by step
5. **W11 comparison plan**: what you predict the SDK will improve vs your hand-rolled loop (record it — file W11-06 checks your predictions)

## 6. Stretch (pick one)

- Streaming step log to the Gradio UI from W9 (watch the agent think)
- A `plan` tool the agent must call first (ReAct with explicit planning) — measure steps delta
- Retry budget per tool (max 1 repair) with a distinct "gave up" observation — does total success improve?

Office Hours (19 Nov): bring the worst trajectory — the discussion there (why the agent chose the wrong tool) is the best possible prep for the OpenAI Agents SDK week.
