# Agent Assembly — Loop + Registry + MCP Tools

**What you'll learn:** the final wiring: your hand-rolled loop driving
registry-validated tools served over MCP, with the constitution, fitter,
and gates in their slots. Nothing is new here — that is the point.

## 1. The assembly diagram

```text
run_react (foundations file 02)
  ├── constitution (file 05)          → system message
  ├── fit_context (file 05)           → per-step context
  ├── ToolRegistry (file 02)          → local validation
  │     └── MCP client (file 03)      → served tools (retrieve, get_unit_text, ...)
  ├── gates (file 04)                 → pre-execute check
  └── trajectory log (file 04)        → the store every run feeds
```

Each box is a tested component; assembly is composition. The only new
code is the client bridge — the adapter that makes MCP calls look like
registry calls:

```python
class MCPBackedRegistry:
    def __init__(self, client, local_schemas: list[dict]):
        self.client = client
        self._schemas = local_schemas            # from server's tools/list

    def schemas(self) -> list[dict]:
        return self._schemas

    def call(self, name: str, args: dict) -> str:
        res = self.client.call(name, args)       # server revalidates too
        if res.isError:
            raise ToolError(res.text)            # hint text → observation path
        return res.text
```

One class, one job: preserve the registry's semantics across the wire
(hint fidelity was file 03's drill — this is where it pays).

## 2. The run path, end to end

| Step | Component | Artifact produced |
|---|---|---|
| 1. fit context | fitter | layers within budget |
| 2. decide | LLM + schemas | tool_calls or final |
| 3. validate | registry + MCP | schema gate (twice) |
| 4. gate | `needs_gate` | gate payload (rare, v1) |
| 5. execute | server handler | Week-09 functions |
| 6. observe | formatters | instructive observation |
| 7. log | trajectory store | parquet row + JSONL trace |

Steps 1–7 run `max_steps` times; the trajectory row is complete at exit
regardless of outcome — degraded runs are measurements too.

## 3. Configuration as one file

```python
AGENT_CONFIG = {
    "model": "pinned-model-id",
    "temperature": 0.0,
    "max_steps": 6,
    "budgets": BUDGETS,                 # fitter
    "constitution_version": "cv1",
    "hint_version": "hv3",
    "server": {"url": "stdio:mcp_rag_server.py", "version": "1.0.0"},
    "gate_policy": GATE_POLICY,
}
```

Every run stamps `AGENT_CONFIG` (hash or version strings) into its
trajectory row — the header discipline that makes A/B results and drift
trends attributable.

## 4. The smoke test — the agent equivalent of "hello world"

```python
def test_smoke_agent_runs():
    run = agent.run("What does the corpus contain?")     # stats-only task
    assert run.steps <= 2
    assert run.outcome in {"success", "refused"}
    assert run.trajectory_complete()
```

One task that needs at most one tool call. It runs in CI (Tier 1, canned
LLM) and Tier 2 (nightly) — the canary for every wiring regression this
program will introduce later.

## Exercises

1. Assemble the agent; run the smoke test on canned LLM and real LLM;
   diff the traces' shapes (tools used, steps) — they need not match,
   but both must be legal.
2. Config-drift drill: change one budget; verify the trajectory row
   reflects it (version stamp) and the fitter's assert catches an
   impossible config.
3. Bridge fidelity: force an MCP error; confirm the observation path
   receives the hint verbatim (the file 03 fidelity test, now live).

## Pitfalls

- Logic creeping into `MCPBackedRegistry` — it is an adapter; logic in
  the bridge is untested logic.
- Config not stamped into trajectories — A/B and drift results become
  unattributable within a week.
- Smoke test that only runs on the real LLM — the canned-LLM variant is
  what makes CI meaningful.

## Resources

- Files 01–05 of this week — every box in the diagram.
- Your Week-09 server (`mcp_rag_server.py`) — the tool side.
