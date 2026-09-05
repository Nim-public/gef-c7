# Trace Debugging — Planted Failure, Root-Caused

**What you'll learn:** the Week-10 replay workflow executed on the SDK
implementation: plant a failure, bisect spans, replay the failing call,
fix at the evidence-named layer, add the regression test — in under an
hour.

## 1. The planted failure

```python
# deliberately vague handoff description, for the drill:
handoff(chart_agent, tool_description_override="handles stuff")
```

Symptom: task 3 ("Which chart shows Q3 margin?") answers *without*
retrieving — the router guessed. The W10 prediction discipline would
have caught it; today the trace does.

## 2. The bisect, in span order

```text
1. WHERE?  → last ok span: router generation, step 1 — no tool call emitted
2. INPUTS? → router saw the query + handoff schema "handles stuff"
3. WHAT?   → no tool_calls: the model had no reason to route
4. LAYER?  → description (the failure-signature table, file 05-02)
```

The trace answers all four questions in one read — which is the entire
argument for having merged spans into the store (file 05-03). On the W10
hand-rolled agent, the same hunt took the predict-actual diff; the span
view is faster and post-hoc.

## 3. Replay and fix

```python
# replay: same inputs, the failing generation, temperature 0
r = Runner.run_sync(router, span["input_messages"])
# fix: the description that says when-to-route (file 02's discipline)
handoff(chart_agent, tool_description_override=(
    "Answer chart/table questions (margins, series, comparisons) using "
    "get_unit_text; always cites unit_ids."))
```

Then the verification ladder: replay green → task 3 green → full eval
set green → battery green. The fix is one description line; the ladder
is what makes the fix *safe*.

## 4. The regression test (the deliverable)

```python
def test_task3_routes_to_chart(canned_agent):
    run = run_agent(canned_agent, "Which chart shows Q3 margin?",
                    max_steps=3)
    used = {t["tool"] for t in run.trace}
    assert "retrieve" in used or run.last_agent.name == "ChartAgent"
    assert run.final_output.citations, "must cite the chart unit"
```

The post-mortem paragraph (W10 file 05-02 format) plus this test — the
debugging loop's complete output. The planted failure's costume changes
next week; the test's shape does not.

## Exercises

1. Execute the drill end-to-end: plant, bisect, replay, fix, ladder,
   post-mortem, test — time it; the target is under an hour.
2. Stochastic-vs-logic drill: replay 5× at temperature 0 and 5× at 0.7;
   classify; write which fix class each implies (prompt vs eval).
3. Speedrun drill: hand the post-mortem to a teammate; they fix from the
   artifact alone without re-bisecting — the artifact's quality gate.

## Pitfalls

- Fixing the symptom (forcing a tool call via prompt) instead of the
  description — the failure returns when the prompt changes.
- Skipping the ladder after the local fix — one green test is not a
  green system; the ladder is cheap and decisive.
- Post-mortems that stop at "model behavior" — the taxonomy (file 05-02)
  exists because every failure has an owner layer.

## Resources

- [`../05-observability-eval-agents/02-replay-debugging.md`](../05-observability-eval-agents/02-replay-debugging.md)
  — the workflow this executes.
- [`../02-tools-handoffs-guardrails/02-handoffs.md`](../02-tools-handoffs-guardrails/02-handoffs.md)
  — the description discipline the fix lands in.