# 06 — Practice: Port Your Agent to the OpenAI Agents SDK

> Week 11 index: [README.md](README.md) · **Due: before Week 12 (by 28 Nov)**

*(No formal task row in the schedule — this practice build converts Week 10's agent to the SDK and quantifies what the framework bought you.)*

---

## 1. Deliverable

```
sdk-agent/
  agents.py              # triage + specialists (handoffs) + guardrails
  tools.py               # @function_tool wrappers over W9 search_knowledge / W6 sql_query
  eval/
    run_cases.py         # the W10 10-task suite, SDK edition
    results.md           # hand-rolled vs SDK comparison table
  traces/                # exported traces for the worst/best runs
  README.md              # prediction check, decisions, failure modes
```

Demo: one handoff trajectory (triage → specialist → cited answer), one guardrail tripwire, one session-resumed multi-turn conversation — each with its trace open.

## 2. Requirements (graded)

### Agents
- [ ] Triage agent with handoffs to Knowledge specialist (W9 tools) and Data analyst (W6 tools)
- [ ] `output_type=Answer(answer, citations, confidence)` on the specialists
- [ ] Input guardrail from file 02 (injection battery passing); output guardrail for citations
- [ ] `SQLiteSession` multi-turn demo; `max_turns` set and tested

### Tools
- [ ] `@function_tool` wrappers with model-facing docstrings (W10-02 rules)
- [ ] One `is_enabled`-gated tool demonstrating least privilege
- [ ] (Optional) your W10 MCP server attached via `MCPServerStdio` — tools reachable from the SDK

### Evaluation (file 05)
- [ ] W10's 10 cases rerun through the SDK agent
- [ ] Metrics table: success, steps p50/p95, tokens p95, tool-error rate — *both* implementations
- [ ] Trace assertions (tool family + answer shape) as pytest cases
- [ ] One failing-run debug story: trace → root cause → fix → side-by-side traces

## 3. The comparison table (the graded centerpiece)

Fill from real runs — no vibes:

| Dimension | W10 hand-rolled | W11 SDK | Delta |
|---|---|---|---|
| lines of code (agent core) |  |  |  |
| success rate (10 tasks) |  |  |  |
| steps p50 / p95 |  |  |  |
| tokens p95 / $ per task |  |  |  |
| guardrails (coverage) |  |  |  |
| multi-turn memory |  |  |  |
| observability |  |  |  |
| effort to add a new tool |  |  |  |

Then the *prediction check* (W10 README §5): what did you predict the SDK would improve? Which predictions held, which didn't — and what does the SDK hide that you now debug differently (hint: observation formatting and context budgeting are still yours, W10-05)?

## 4. Rubric

| Area | Weight |
|---|---|
| Agents + handoffs + guardrails correctness | 30% |
| Tool wrappers (W9/W6 reuse, gating, docstrings) | 20% |
| Comparison table rigor (both implementations, same cases) | 25% |
| Traces/debug story + regression cases | 15% |
| README decisions + prediction check | 10% |

## 5. README architecture section (answer explicitly)

1. **Final architecture**: agents, edges (handoffs), tools, guardrails — as a diagram
2. **What the SDK replaced vs what you kept** (validators, context fitter, HITL gates — where do they live now?)
3. **Guardrail calibration**: trip rates on the W3-02 battery + benign set (file 02 ex. 3 numbers)
4. **Failure modes found** (≥3) with trace evidence
5. **W12–14 bridge**: phiData (W12), LangGraph (W13), LangChain+MCP (W14) all promise the same primitives — list which of your five concepts (tools, handoffs, guardrails, sessions, tracing) you expect to map where

## 6. Stretch (pick one)

- Attach your W10 FastMCP server via `MCPServerStdio` and run the eval *without* `@function_tool` copies — compare tool-selection accuracy vs native tools
- Streaming: `Runner.run_streamed` into a Gradio chat (W9-01) with step events shown live
- Voice: wrap file 04's cascade around the SDK agent (push-to-talk + 3 tools) — measure the added latency per tool call

Office Hours (26 Nov): bring the comparison table — the phiData (W12) and LangGraph (W13) discussions start from "what did the SDK already give you, and what's still missing?"
