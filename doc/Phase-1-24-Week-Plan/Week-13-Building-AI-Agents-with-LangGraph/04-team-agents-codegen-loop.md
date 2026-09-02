# 04 — Team of Agents: Code-Generation & Self-Repair Loop

> Week 13 index: [README.md](README.md)

**Session 2 projects:** *Team of AI Agents using LangGraph. Project 1: Code-generation & self-repair agent — a dev-tool that takes a natural-language feature request and spawns nodes for: (a) planning, (b) writing code, (c) running unit tests, (d) debugging failures. The graph loops until tests pass, mirroring how a human iterates. Useful inside IDE extensions or CI pipelines. Project 2: Team of 5 AI Agents involving computer agents and LangGraph — e.g., a team that writes technical blogs.*

---

## What you'll learn

- The self-repair loop — the graph pattern where the *test result* is the edge condition
- Supervisor/team-of-agents topology (session Project 2)
- Sandbox discipline: executing LLM-written code safely
- When a team beats a single agent (and when it's overhead)

## 1. Project 1: the code-gen & self-repair graph

The schedule's shape — plan → write → run tests → debug → loop:

```
START ─► plan ─► write_code ─► run_tests ─┬─(pass)─► END
                       ▲                  └─(fail)─► debug ─┐
                       └────────────────────────────────────┘
```

State carries the artifacts between stages:

```python
from typing import Annotated, TypedDict

class CodeState(TypedDict):
    request: str                     # natural-language feature request
    plan: str
    code: str
    test_results: str                # pytest stdout/stderr
    iteration: int                   # the loop bound (W11-03's anti-pattern fix)
    history: Annotated[list[str], lambda a, b: a + [b]]
```

### Nodes

```python
def plan(state):                     # (a) planning
    r = client.chat.completions.create(model=MODEL, temperature=0,
        messages=[{"role": "user", "content":
                   f"Feature request: {state['request']}\n"
                   "Produce: 1) function signature(s) 2) behavior spec 3) the unit tests "
                   "they must pass. No code yet."}])
    return {"plan": r.choices[0].message.content, "iteration": 0}

def write_code(state):               # (b) writing — rewrites with the debug critique on retries
    crit = state["test_results"] if state["iteration"] else ""
    r = client.chat.completions.create(model=MODEL, temperature=0,
        messages=[{"role": "user", "content":
                   f"Spec:\n{state['plan']}\n\nPrevious failures:\n{crit}\n"
                   "Write the implementation only. Code between ```python fences."}])
    code = r.choices[0].message.content.split("```python")[-1].split("```")[0]
    return {"code": code}

def run_tests(state):                # (c) execution — in a sandbox, never your shell
    import subprocess, tempfile, os
    with tempfile.TemporaryDirectory() as d:
        open(f"{d}/impl.py", "w").write(state["code"])
        open(f"{d}/test_impl.py", "w").write(make_tests(state["plan"]))
        p = subprocess.run(["py", "-m", "pytest", "-q", d],
                           capture_output=True, text=True, timeout=30, cwd=d)
    return {"test_results": (p.stdout + p.stderr)[-3000:],
            "iteration": state["iteration"] + 1}
```

### The loop edge — test result decides

```python
def after_tests(state) -> str:
    if "passed" in state["test_results"] or state["iteration"] >= 3:
        return "done"                        # exit condition: pass OR bounded retries
    return "debug"

g.add_conditional_edges("run_tests", after_tests, {"done": END, "debug": "debug"})
g.add_edge("debug", "write_code")            # (d) debugging feeds the rewrite
```

The `debug` node's job is *diagnosis*, not rewriting:

```python
def debug(state):                    # (d) analyze the failure into instructions
    r = client.chat.completions.create(model=MODEL, temperature=0,
        messages=[{"role": "user", "content":
                   f"Code:\n{state['code'][:4000]}\nTest output:\n{state['test_results']}\n"
                   "Diagnose the root cause in 3 bullets and state the fix as instructions."}])
    return {"history": [r.choices[0].message.content]}
```

`iteration >= 3` is the schedule's "loops until tests pass" *bounded* — the W11-03 anti-pattern rule made structural.

## 2. Sandbox discipline (non-negotiable)

LLM-written code executing on your machine = arbitrary code execution. Minimum rules:

- Run in a **temp dir** with only the written file + test harness (above)
- **Timeouts** on the subprocess (30 s) — infinite loops are the norm, not the exception
- No network, no credentials in env for the child process
- In production: containers/micro-VMs (Docker, Firecracker-class) — the tempfile version is for learning only

## 3. Project 2: team of agents (supervisor topology)

The blog-writing team — the second session shape:

```
START ─► supervisor ─┬─► researcher ─┐
                     ├─► writer ◄────┤ (supervisor routes work, aggregates)
                     ├─► editor      │
                     └─► fact_checker┘ ─► END
```

The **supervisor pattern**: one node whose only job is routing (a small LLM call returning the next worker), workers as nodes, shared state as the deliverable:

```python
def supervisor(state):
    r = client.chat.completions.create(model=MODEL, temperature=0, response_format= SupervisorDecision,
        messages=[{"role": "user", "content":
                   f"Blog task: {state['request']}\nDone so far: {state['history'][-1:]}\n"
                   "Who works next: researcher | writer | editor | fact_checker | DONE?"}])
    return {"next": r.choices[0].message.parsed.next}

g.add_conditional_edges("supervisor", lambda s: s["next"],
    {"researcher": "researcher", "writer": "writer", "editor": "editor",
     "fact_checker": "fact_checker", "DONE": END})
```

Supervisor vs the W11 delegation-as-tools pattern: same topology, different visibility — the supervisor's routing is now a node you can trace, gate, and time-travel (file 06). Handoffs remain better for *exclusive* control transfer; supervisors for *collaborative* assembly.

## 4. When a team beats a single agent

| Signal | Team |
|---|---|
| stages need *different* instructions/prompts | ✓ (writer vs editor personas) |
| outputs must be independently verifiable (tests, fact-checks) | ✓ (separate nodes = separate gates) |
| single agent keeps conflating steps | ✓ (state separates artifacts) |
| one LLM call answers fine | ✗ (W3-05: overhead without benefit) |
| latency budget tight | ✗ (each node = a roundtrip) |

## Exercises

1. Build the self-repair graph; give it a failing feature request ("write `is_prime` with tests"). Log iterations until pass; verify the bound at 3.
2. Sabotage drill: make `write_code` emit a syntax error on iteration 1 only (prompt patch). Trace the debug→rewrite path and confirm recovery.
3. Add a `security_review` node between `run_tests` pass and END (checks for `os.system`/network imports). Make it a hard gate.
4. Build the blog team; cap supervisor decisions at 8. Which worker fires most on a typical task — is the topology balanced or is one worker a bottleneck?
5. Team-vs-single A/B: one strong single agent vs the team on 5 blog requests; judge outputs with the W10-04 rubric. When does the team actually win?

## Pitfalls

- **Executing code outside a sandbox** — the demo works until it doesn't; subprocess+tempdir minimum, containers for anything shared
- **Test harness written by the same model pass** — self-grading; derive tests from the *spec* node, or fix them per feature family
- **Unbounded repair loops** — the `iteration` bound is structural, not optional (W11-03)
- **Supervisor with a god-prompt** — routing quality lives in the decision prompt; test it separately (it's a classifier, W2-02 style)
- **State as a dumping ground** — code, tests, logs, plan in one blob; design fields per consumer (W13-01's state-as-API rule)

## Resources

- LangGraph examples: [code generation with self-correction](https://langchain-ai.github.io/langgraph/tutorials/) (the session project's canonical implementation)
- LangGraph [multi-agent concepts](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) — supervisor vs network topologies
- Anthropic, *Building effective agents* — the "evaluator-optimizer" pattern (your test edge)
- W11-03 (topologies), W10-04 (sandbox/gates), W8 (why tests-and-diagnosis beats one-shot generation)
