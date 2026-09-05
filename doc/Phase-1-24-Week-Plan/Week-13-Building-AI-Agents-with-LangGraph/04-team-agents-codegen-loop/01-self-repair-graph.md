# The Self-Repair Graph — Plan / Write / Test / Debug Cycle

**What you'll learn:** the classic four-node loop: plan the function,
write it, test it in a sandbox, debug from failures — bounded, sandboxed,
and measured.

## 1. The graph

```python
from langgraph.graph import StateGraph, START, END

class CodeState(TypedDict):
    task: str
    plan: str
    code: str
    test_results: str
    attempts: int
    done: bool

builder = StateGraph(CodeState)
for n in ("plan", "write", "test", "debug"):
    builder.add_node(n, globals()[f"{n}_node"])

builder.add_edge(START, "plan")
builder.add_edge("plan", "write")
builder.add_edge("write", "test")
builder.add_conditional_edges("test", route_after_test,
                              {"debug": "debug", "done": END})
builder.add_edge("debug", "write")          # the repair cycle
```

```python
def route_after_test(state: CodeState) -> str:
    if state["done"]:
        return "done"
    if state["attempts"] >= 4:               # the bound
        return "done"                        # degraded exit
    return "debug"
```

Four nodes, one cycle, one bound — the plan/write/test/debug loop as a
picture. `attempts` increments in `debug` (or `write`); the bound is
4 (drill-tuned; W10 file 03's rules apply verbatim).

## 2. The test node is the graph's truth source

```python
def test_node(state: CodeState) -> dict:
    result = run_in_sandbox(state["code"], TEST_SUITE[state["task"]])
    passed = result.returncode == 0
    return {"test_result": result.stdout[-500:],
            "attempts": state["attempts"] + 1,
            "done": passed}
```

The sandbox (file 02) is what makes the cycle safe; the *test suite* is
what makes it honest. Generated code passes only real assertions — the
eval-set discipline (W10 file 06-02) applied to code instead of answers.

## 3. The debug node — failures as instructions

```python
def debug_node(state: CodeState) -> dict:
    hint = (f"Previous attempt failed:\n{state['test_result']}\n"
            f"Fix the code. Do not repeat the same mistake.")
    return {"plan": f"{state['plan']}\n\nRepair note: {hint}"}
```

The debug node rewrites the plan with the failure — the W10 failure-
phrasing pattern (errors as instructive prompts), node-shaped. The
attempt counter + the failure text in the plan is what prevents the
same-error spiral (the W10 loop detector's structural cousin).

## 4. What the loop measures (the A/B substrate)

| Metric | Source | Target |
|---|---|---|
| attempts to green | state counter | ≤2 for most tasks |
| test-pass rate per attempt | test node | rising per attempt |
| token cost per repair | fitter ledger | bounded by budget |
| sandbox escapes | sandbox layer | zero, always |

The self-repair loop's value is the *attempts curve*: if attempt 2
passes where attempt 1 failed, the debug node works; if attempts never
converge, the task or the test suite is broken — and the A/B (file 04)
quantifies it.

## Exercises

1. Build the four-node graph; run 5 codegen tasks; produce the attempts
   curve (histogram of attempts-to-green).
2. Debug-node drill: plant a recurring bug (missing import); verify the
   repair note breaks the repetition within 2 attempts.
3. Bound drill: set attempts ≥4 on a hard task; the loop exits with
   honest failure — no infinite repair.

## Pitfalls

- Test suites that only check "runs without error" — the loop then
  optimizes for garbage that executes; real assertions only.
- Debug notes that restate the failure without directing — the W10
  phrasing rules (constraint, shape, next action) apply to repair notes.
- Unbounded repair cycles — 4 attempts or the honest failure; the bound
  is the product's promise.