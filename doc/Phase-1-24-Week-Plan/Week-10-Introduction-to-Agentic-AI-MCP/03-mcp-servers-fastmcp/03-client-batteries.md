# Client Batteries — Deterministic Tests + Real-LLM Paths

**What you'll learn:** the two-tier battery that makes the MCP server
trustworthy: Tier 1 (deterministic, canned-LLM, runs in seconds) and
Tier 2 (real-LLM, sampled, runs in minutes) — one truth, two speeds.

## 1. The two tiers, and what each can catch

| Tier | LLM | Catches | Runtime | CI slot |
|---|---|---|---|---|
| 1. Deterministic | canned/scripted | protocol, schemas, error mapping, routing | seconds | every push |
| 2. Real-LLM | your actual model | description quality, trajectory shape, drift | minutes | nightly + pre-demo |

Tier 1 cannot see model behavior; Tier 2 cannot be deterministic. The
battery's power is the split: contract bugs are caught cheap and always;
model bugs are caught sampled and honestly.

## 2. Tier 1 — the deterministic battery

```python
import pytest

CASES = [
    # (query-as-toolcalls, expect)
    ([("retrieve", {"query": "EBITDA margin", "modality": "image"})], "ok"),
    ([("get_unit_text", {"unit_id": "nope"})], "error:hint"),
    ([("retrive", {"query": "x"})], "error:unknown"),
    ([("retrieve", {"query": 42})], "error:schema"),
]

@pytest.mark.parametrize("calls,expect", CASES)
def test_server_battery(calls, expect, mcp_client):
    for name, args in calls:
        res = mcp_client.call(name, args)
        if expect == "ok":
            assert not res.isError
        else:
            assert res.isError and hint_quality(res.text)
```

`hint_quality` checks the error message contains the *teaching* parts
(valid id shape, next action) — the error contract, asserted at the wire.

## 3. Tier 2 — the real-LLM battery, sampled honestly

```python
REAL_TASKS = [
    {"query": "Which chart shows Q3 margin?", "expect_tools": {"retrieve", "get_unit_text"},
     "max_steps": 3},
    {"query": "Summarize the corpus stats", "expect_tools": set(), "max_steps": 1},
    {"query": "What was the CEO's 2019 bonus?", "expect_tools": {"retrieve"},
     "must_say": "not found"},
]

def test_real_task(task, agent):
    run = agent.run(task["query"])
    tools_used = {t["tool"] for t in run.trace}
    assert tools_used == task["expect_tools"]
    assert run.steps <= task["max_steps"]
```

Tier-2 assertions are *behavioral*, not textual: which tools, how many
steps, did it refuse. Never assert exact answer text — model variance
would break the suite and teach you nothing.

## 4. Sampling discipline for Tier 2

| Rule | Value | Why |
|---|---|---|
| runs per task | 3, majority-vote | one run is anecdote |
| temperature | your demo setting | test what you ship |
| model | pinned id + version | drift is a finding, not noise |
| fail policy | 2/3 majority | flaky-single-run suites get ignored |

```python
def majority(runs: list[bool]) -> bool:
    return sum(runs) * 2 > len(runs)
```

The nightly Tier-2 report (pass rates per task, over time) is the drift
detector: a task that passed 3/3 for two weeks and now passes 1/3 is a
model-update signal, caught before your demo.

## Exercises

1. Build Tier 1 with the four-case table plus hint-quality assertions;
   wire into CI (every push).
2. Build Tier 2 with the three-task table; run 3× each; produce the
   pass-rate report with model id + date header.
3. Drift rehearsal: rerun Tier 2 with a different (weaker) model; record
   which tasks flip — the sensitivity map that tells you where description
   quality matters most.

## Pitfalls

- Tier-2 tests asserting answer text — variance theater; assert tools,
  steps, refusals.
- Deterministic tests that mock away the *server* (test handlers
  directly) — the battery's value is the wire.
- Nightly reports nobody reads — the pass-rate table belongs in the
  weekly retrospective (W9-05 exercises), with flip alerts.

## Resources

- Your registry test suite (file 02) — Tier 1's in-process sibling.
- [`../04-measuring-agents-patterns/`](../04-measuring-agents-patterns/)
  — the harness these batteries feed.
