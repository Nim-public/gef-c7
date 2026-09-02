# 04 — Measuring Agents & Best Practices

> Week 10 index: [README.md](README.md)

**Session 1 topics:** *Measuring Agents & Best Practices. Some advanced topics like human-in-the-loop & LLM-as-a-judge.*

---

## What you'll learn

- The trajectory metrics that answer "is the agent actually good?"
- Instrumenting the hand-rolled loop so every run produces evaluable logs
- Best practices that separate demo agents from production agents
- Human-in-the-loop gates and LLM-as-judge trajectory scoring — with their failure modes

## 1. What "measuring an agent" means

An agent run is a **trajectory**: goal → steps (thought, tool, args, observation) → outcome. Three dimensions, none sufficient alone:

| Dimension | Metric | Questions it answers |
|---|---|---|
| **Task success** | success rate on a labeled task set | does it reach the right answer? |
| **Efficiency** | steps/task, tokens/task, $/task, p95 latency | at what cost? is it degrading? |
| **Process quality** | tool-error rate, redundant-call rate, guard trips, repair rate | *how* did it get there — luck or method? |

```python
# logged per run (the instrumentation below), aggregated like W5-05
report = {
    "n": 10,
    "success_rate": 0.8,          # label per task: expected answer / expected tools used
    "steps_p50": 3, "steps_p95": 6,
    "tokens_p95": 9800, "cost_usd_p95": 0.011,
    "tool_error_rate": 0.09,      # error observations / all observations
    "guard_trips": 2,             # injection/refusal events (W3-02 battery)
}
```

**Ablation-based attribution** (the skill that makes the numbers actionable): rerun the suite with one component degraded (weaker model, removed tool, truncated observations) — which metric moves tells you what that component was buying. Same discipline as W5-02's bake-off, one level up.

## 2. Instrumenting the loop

```python
import time, json

def run_agent(goal, max_steps=8, log_path="data/agent_runs.jsonl"):
    trace, messages = [], [...]
    run_meta = {"goal": goal, "steps": trace, "success": None}
    try:
        for step in range(max_steps):
            t0 = time.time()
            resp = client.chat.completions.create(...)          # as file 01
            trace.append({"step": step, "role": "llm",
                          "tool": msg.tool_calls[0].function.name if msg.tool_calls else None,
                          "args": ..., "latency_s": round(time.time() - t0, 2),
                          "tokens": resp.usage.total_tokens if resp.usage else None})
            # ... tool execution, with its own latency + ok/error fields per W10-02
        run_meta["success"] = outcome                          # labeled or judged
    finally:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(run_meta, ensure_ascii=False) + "\n")
```

Log **everything** (W5-04's habit, agent-scaled): full messages, args, raw observations, errors, token counts. The JSONL becomes: your eval set (file 06's practice), your regression suite, and your incident reviews.

## 3. Best practices (demo → production)

| Practice | Rule |
|---|---|
| **Deterministic tools** | same args → same result (cache or fix seeds); nondeterminism multiplies agent variance |
| **Idempotency** | retries must not double-charge/dupe (W10-02) |
| **Timeouts everywhere** | per tool call *and* per run; a hung tool hangs the loop |
| **Fail loudly, feed back** | errors as structured observations, never swallowed (W10-01) |
| **Least-power tools** | read-only first; write tools only behind gates (§4) |
| **Max turns + token ceilings** | both set, both tested |
| **Version prompts *and* tool descriptions** | they change behavior like code (W3-02) |
| **One trajectory = one JSONL line** | the unit of debugging, eval, and replay |

## 4. Human-in-the-loop (HITL)

W3-02's privilege separation becomes concrete: any *state-changing or hard-to-reverse* tool requires approval before execution:

```python
APPROVAL_REQUIRED = {"send_email", "issue_refund", "write_file"}

def maybe_execute(name, args) -> str:
    if name in APPROVAL_REQUIRED:
        print(f"\nAPPROVAL NEEDED: {name}({args})\n[y/N]: ")
        if input().strip().lower() != "y":
            return json.dumps({"ok": False, "error": "denied by human reviewer"})
    return registry.execute(name, json.dumps(args))
```

Design notes from production practice:

- **Approve the *action*, not the agent** — show the exact call (tool + args + diff); "the agent said it will be careful" is not a gate
- **Budget the interruptions** — if 60% of runs need approval, the tools are too scary or the model too weak; track the rate (it's a metric in §1)
- **Escalation as a first-class outcome** — "I need a human for this" is a *success* trajectory when stakes are high (W5-04's confidence hook, now with teeth)
- W11's guardrails and W13's LangGraph checkpoints mechanize this same gate

## 5. LLM-as-a-judge for trajectories

Some qualities have no programmatic check ("was the tool sequence sensible?"). A judge LLM scores the *trace*, not just the answer:

```python
JUDGE_PROMPT = """You are evaluating an agent trajectory.

GOAL: {goal}
TRAJECTORY:
{trajectory}     # step-by-step: tool, args, observation summary, final answer

Score 1-5 each:
- tool_choice: were the right tools used, in a sensible order?
- efficiency: any redundant/looping steps?
- grounding: is the final answer supported by the observations?

Return JSON: {"tool_choice": n, "efficiency": n, "grounding": n, "issues": ["..."]}"""

def judge_trajectory(goal, trace) -> dict:
    return json.loads(client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            goal=goal, trajectory=json.dumps(trace, indent=1)[:6000])}],
    ).choices[0].message.content)
```

Judge discipline (all of W5-05's caveats, restated because they bite harder here): pin the judge model + temperature; **never** let the judge grade outputs it generated; report n with every mean; run twice and report spread; treat judge scores as *direction*, programmatic checks (schema, citations, DB cross-checks) as *fact*.

## Exercises

1. Instrument file 01's loop with the trace/logging above; run 10 tasks; produce the §1 metrics table (success, steps p50/p95, tokens p95, tool-error rate).
2. Build the judge; score the same 10 trajectories. Where do judge scores disagree with your hand labels? (That disagreement *is* your judge-quality eval.)
3. HITL drill: add `issue_refund` as a fake write tool behind `maybe_execute`; run 3 trajectories that try to use it — log denial outcomes. What does the model do after a denial? (If it retries blindly, add "denied — do not retry" phrasing to the observation.)
4. Ablation: rerun the suite with `temperature=0.7` vs 0. Report the tool-error rate delta and p95 steps. Pick a setting, justify it.
5. Regression suite: pick your 3 best and 3 worst trajectories; save as `eval/agent_cases.jsonl` (goal + expected tools + expected answer shape). This file becomes Week 11's SDK practice and Week 15's reliability harness.

## Pitfalls

- **Success-rate myopia** — an 80% success rate with 12-step p95 trajectories is a cost incident in waiting; report all three dimensions
- **Judging only outcomes** — a lucky right answer via wrong tools is a time bomb; score trajectories too
- **Unversioned prompts/tools in the loop** — your eval numbers die when the system prompt drifts (W3-02)
- **HITL as an afterthought** — retrofitting approval gates into a deployed agent is a redesign; the gate lives in the *executor* (§4), which you control
- **Judge == agent model** — self-preference bias (W5-05); use a different family, pin everything

## Resources

- Anthropic, *Building effective agents* — the practices in §3, expanded
- OpenAI Cookbook, *Evaluating agentic workflows* patterns
- W5-05 (Ragas) + W3-02 (testing prompts) — the two disciplines this file composes
- Yao et al., *ReAct* (§4 evaluation) — how the original paper measured its agent
- LangSmith/Langfuse docs — hosted trace-and-judge platforms (what your JSONL becomes at scale)
