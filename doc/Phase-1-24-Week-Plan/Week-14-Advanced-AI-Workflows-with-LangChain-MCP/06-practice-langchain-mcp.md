# 06 — Practice: LangChain + MCP Integration

> Week 14 index: [README.md](README.md) · **Due: before Week 15 (by 19 Dec)**

*(No formal task row in the schedule — this practice build consolidates the LangChain week and unifies your tool layer under MCP before the production week.)*

---

## 1. Deliverable

```
langchain-mcp/
  assistant.py           # the scoped workflow assistant (file 05)
  chains.py              # LCEL chains: triage, analysis, report (file 01)
  projects/
    csv_analyzer.py      # file 02 (Gradio front end)
    code_review.py       # file 03 (structured Review output)
    agentic_rag.py       # file 04 (three-source routing)
  eval/
    cases.jsonl          # 15 mixed tasks across all four pillars
    results.md           # routing/tool-selection table + regression notes
  README.md              # integration map, framework verdict, MCP topology
```

Demo: one CSV-analysis run (chart + interpretation), one code-review report, one cross-server automation with an approval gate — all through the same assistant.

## 2. Requirements (graded)

### Chains & agents
- [ ] ≥3 LCEL chains with `with_structured_output` + `.with_retry`/fallbacks (file 01)
- [ ] `create_agent` assistant holding MCP tools (your W10 server + ≥2 public servers)
- [ ] CSV Analyzer and Code Review projects runnable as sub-flows

### MCP topology
- [ ] `MultiServerMCPClient` config committed (stdio + one HTTP transport)
- [ ] Tool count documented and justified (lean, W10-05)
- [ ] Path/scope containment verified (workspace-root, read-only DB, minimal tokens)

### Safety & evaluation
- [ ] Cross-server injection battery (file 05 §4) — all refusals logged
- [ ] 15-case eval: routing accuracy + numeric grounding (W12-04) + citation coverage
- [ ] Every write action behind a gate (W10-04), gates logged

## 3. The framework verdict (the README centerpiece)

Four frameworks built this month — one table, from your measurements:

| Need | W10 hand-rolled | W11 OpenAI SDK | W12 Agno | W13 LangGraph | W14 LangChain |
|---|---|---|---|---|---|
| agent loop |  |  |  |  |  |
| tools/MCP |  |  |  |  |  |
| guardrails |  |  |  |  |  |
| memory/state |  |  |  |  |  |
| observability |  |  |  |  |  |
| multi-agent patterns |  |  |  |  |  |
| best-fit role in the capstone |  |  |  |  |  |

Then the decision paragraph: which framework(s) the capstone *ships* with, which stay as learning artifacts — reasoned from your tables, not preference.

## 4. Rubric

| Area | Weight |
|---|---|
| LCEL chains + structured output + retries/fallbacks | 20% |
| MCP topology (servers, scoping, tool budget) | 25% |
| The four pillar features working end-to-end | 25% |
| Safety battery + gates + logs | 15% |
| README: framework verdict + integration map | 15% |

## 5. README integration map (answer explicitly)

1. **MCP topology diagram**: servers → tools → assistant → gates (ASCII)
2. **Tool inventory**: every tool, its server, its write/read class, its gate
3. **The verdict table** (§3) with the shipping decision
4. **Failure modes** (≥3) with traces
5. **W15 bridge**: your agent's current p95 latency and $/task — the two numbers Week 15's optimization work targets. Measure them now, or the optimization week has no baseline.

## 6. Stretch (pick one)

- LangSmith free tier: trace the 15-case eval; compare span data with your JSONL (W11-05's join, hosted)
- A second assistant persona ("auditor") with the same servers but read-only gating — same tools, different constitution
- Migrate the CSV Analyzer's pandas tool to DuckDB (W6-04) — measure query latency on a 1M-row file

Bring the framework verdict to Office Hours (17 Dec): Week 15 is production hardening, and it starts by choosing what to harden.
