# Exercises — Agents Foundations

Expanded set with worked approaches. The deliverable: a working 50-line
agent over your Week-09 tools, with three predicted trajectories and the
boundary statement.

## 1. The loop, from scratch (from 02-hand-rolled-react)

**Task:** implement `run_react` + `ToolRegistry` stub against a fake LLM
(recorded tool-call decisions), and verify the three failure paths (tool
error, loop, budget) with scripted responses.

**Worked approach:** the fake LLM is a list of canned responses popped per
call — deterministic tests for a stochastic component. The three failure
paths get one scripted case each; the loop detector (4 lines) gets its
own test.

**Pass criterion:** 5 scripted-trajectory tests green; loop-breaker fires
on the repeat fixture; budget stop flags `degraded`.

## 2. Prediction discipline (from 03-demo-trajectories)

**Task:** for 10 queries across your routing classes, write the expected
trajectory *before* running (tools as a set + max steps), run, and log
the delta with a one-line cause.

**Worked approach:** the predict-run-diff loop is the skill of the week —
deltas are not failures, they are *measurement* of description quality.
Group deltas by cause: missing parameter in schema, vague description,
missing tool.

**Pass criterion:** the 10-row predict/actual table committed to
`reports/trajectory-predictions.md`; ≥7/10 exact matches.

## 3. The boundary memo (from 04-when-not-agents)

**Task:** write `doc/capstone/agentic-boundary.md` with your measured
query distribution, the pipeline/agent split, and one trace-mined
pipeline proposal.

**Worked approach:** the percentages come from the Week-09 router logs —
no vibes. The proposal names the repeated trajectory and its projected
savings (steps and tokens) as a pipeline route.

**Pass criterion:** memo committed; the split matches `needs_agent`'s
output on your data.

## 4. Tool description A/B (from 02)

**Task:** take your worst-trajectory query; write two versions of the
offending tool description; run each 5×; report mean steps and success.

**Worked approach:** one variable per experiment (the description text);
the A/B table is 2 rows × (steps, success, tokens). This drill feeds
file 05's failure-phrasing section with your own evidence.

**Pass criterion:** the better description wins on mean steps; the delta
is recorded with the exact texts.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| 50-line loop + 3 failure paths tested | tests/ green | 4 |
| 10 predicted trajectories, ≥70% exact | predict table | 3 |
| Impossible-query battery ≥4/5 honest | battery results | 3 |
| Boundary memo with measured split | agentic-boundary.md | 2 |

**Pass bar:** 9/12 to proceed to file 02 (tools and memory). The loop
tests are the week's foundation — every later week runs on them.

## 5. The definition drill, on real systems

**Task:** classify five systems against §5's one-question test (who
chooses the next function?): your W9 pipeline, a UI chatbot with
"tool-like" buttons, a cron job that calls retrieval, an agent framework's
default template, and your own `run_react`. Write one sentence each.

**Worked approach:** the drill's value is calibration — after five
verdicts you will stop calling pipelines agents, and start seeing where
the transfer actually sits in frameworks (usually: their `AgentExecutor`
*is* the loop you hand-rolled, with more logging).

**Pass criterion:** five verdicts, each citing the decision-maker; any
"it depends" gets resolved by writing the if-statement question precisely.

## 6. Capstone tie-in: the boundary artifact

**Task:** append the boundary statement to
`doc/capstone/agentic-boundary.md` (from exercise 3) with the shadow-mode
plan: which week the agent goes live, on which flag, with which
win-metric.

**Worked approach:** the artifact is three sentences plus the shadow
metric — it is the contract between this week's enthusiasm and the
measured cutover.

**Pass criterion:** artifact committed; the cutover metric is testable
(success AND steps ≤ pipeline+1), not vibes.

## Pitfalls recap

- Scripted-LLM tests that only cover the happy path — the three failure
  fixtures are the point of the exercise.
- Predictions written *after* running — the table becomes fiction; write
  first, run second, diff honestly.
- Boundary decided by enthusiasm rather than the 80/20 measurement — the
  memo cites router logs or it is not a decision.
