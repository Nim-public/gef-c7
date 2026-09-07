# Hand-Rolled ReAct — The 50-Line Implementation, Traced

**What you'll learn:** the full ReAct loop built on the OpenAI-style
function-calling protocol — every line load-bearing, a complete trace of
one run, and the three failure points the loop must handle.

## 1. The implementation

```python
import json

SYSTEM = ("You are a retrieval agent. Use tools; then answer with citations. "
          "If tools cannot answer, say so.")

def run_react(query: str, registry, max_steps: int = 6) -> dict:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": query}]
    trace = []
    for step in range(1, max_steps + 1):
        resp = llm(messages, tools=registry.schemas())          # 1) decide
        if not getattr(resp, "tool_calls", None):               # 2) answer
            return {"answer": resp.content, "trace": trace, "steps": step}
        for call in resp.tool_calls:                            # 3) execute
            entry = {"step": step, "tool": call.name, "args": call.args}
            try:
                obs = registry.call(call.name, call.args)       # validated
                entry["obs"] = str(obs)[:500]
            except Exception as e:
                entry["obs_error"] = f"{type(e).__name__}: {e}"  # 4) recover
            trace.append(entry)
            messages.append(tool_message(call, entry))
    return {"answer": "budget exhausted", "trace": trace,
            "steps": max_steps, "degraded": True}
```

That is the entire loop: **decide → answer-or-execute → observe → feed
back**. Everything else in agentic frameworks is decoration on these four
movements.

## 2. A complete trace, annotated

Query: *"Which chart shows the highest Q3 margin, and what does it say?"*

| Step | Thought (model) | Tool call | Observation (yours) |
|---|---|---|---|
| 1 | need image retrieval | `retrieve(query="Q3 margin chart", modality="image")` | 5 hits, top: `u042` score 0.61 |
| 2 | need the chart's numbers | `get_unit_text(unit_id="u042")` | OCR: "Gross margin 12.4% ..." |
| 3 | answerable now | *(no tool call)* | answer with [u042] citation |

Three steps, one citation, done. The same query with a vague
`retrieve(query=...)` description that omits `modality` typically burns a
fourth step re-retrieving text-side — the cost of under-specified tools,
visible in one trace.

## 3. The three failure points, handled explicitly

| Failure | Symptom | Loop's answer |
|---|---|---|
| Tool raises | exception mid-step | catch → `obs_error` as *instructive* observation (file 05) |
| Model loops (same call repeatedly) | identical args, step k+1 | budget stop + `degraded` flag |
| Model answers without evidence | hallucinated citation | citation audit (W9-04 file 03) on the final answer |

```python
def looks_looped(trace: list[dict]) -> bool:
    if len(trace) < 2:
        return False
    a, b = trace[-2], trace[-1]
    return a["tool"] == b["tool"] and a["args"] == b["args"]
```

The loop-detector is 4 lines and catches the most common failure in
student agents — the model re-calling the same tool hoping for different
output. On detection: inject an observation saying so (file 05's failure
phrasing), not a silent retry.

## 4. Why hand-roll before frameworks

Frameworks (LangGraph, smolagents, LlamaIndex workflows) buy you state
management, retries, streaming — after you can read the 50 lines. The
capstone rule: hand-roll first (this file), then adopt a framework only
when its feature list matches a *felt* pain, never to avoid understanding
the loop you are shipping.

## Exercises

1. Run the trace of §2 on your corpus with your tools; diff your actual
   trajectory against the table — every extra step names a description or
   schema gap.
2. Implement `looks_looped` + the loop-breaker observation; force the
   failure by giving a tool a misleading description; verify recovery.
3. Budget ladder: run 10 queries at `max_steps` ∈ {3, 6, 10}; report
   success rate and token cost per budget — the curve that picks your
   default.

## Pitfalls

- Swallowing tool errors into empty observations — the model learns
  nothing and retries blindly; errors are prompts (file 05).
- `str(obs)[:500]` truncation *without* thought — truncate mid-JSON and
  the model sees garbage; truncate at field boundaries.
- Trusting the model's "final answer" without the citation audit — the
  trace shows what it *did*, the audit shows whether it may claim it.

## Resources

- ReAct paper (Yao et al. 2022); OpenAI function-calling docs.
- Your Week-09 tool contract — the registry this loop calls.
