# Trace Hygiene — PII Scrubbing, Retention, Sampling

**What you'll learn:** the trace layer's hygiene: PII scrubbing before
export, retention windows, and sampling policies — what leaves your
machine, how much of it, and for how long.

## 1. The scrubber

```python
import re

SCRUBBERS = {
    "email": (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    "phone": (re.compile(r"\+?\d[\d\s-]{8,}\d"), "[PHONE]"),
    "api_key": (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[KEY]"),
    "path": (re.compile(r"[A-Z]:\\[^\s'\"]+|/home/[^\s'\"]+"), "[PATH]"),
}

def scrub(obj) -> object:
    """Recursively scrub strings in dicts/lists; returns clean copy."""
    if isinstance(obj, str):
        out = obj
        for pat, repl in SCRUBBERS.values():
            out = pat.sub(repl, out)
        return out
    if isinstance(obj, dict):
        return {k: scrub(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub(v) for v in obj]
    return obj
```

| Pattern | Catches |
|---|---|
| email/phone | the W14 PII set, at the trace boundary |
| API key shapes | credential leaks in logs |
| absolute paths | the W10 firewall rule, trace edition |

The scrubber runs at the *export boundary* (the W11 custom processor
and the LangSmith hook both call it) — the raw trace stays local and
full-fidelity; only the export is scrubbed. Debugging keeps its detail;
the platform sees clean data.

## 2. Retention (the time dimension)

| Store | Retention | Rationale |
|---|---|---|
| local raw traces (JSONL) | 30 days, rotated | debugging window |
| local parquet store | indefinitely (it's the record) | metrics need history |
| hosted platform | platform default or custom | check the setting |
| checkpoint db | 20/thread (W13 policy) | the W13 prune |

Retention is per-store policy — the W10 pin-note discipline extended to
every trace surface. The debug window (30 days) covers any realistic
incident investigation; the parquet's indefinite retention is fine
because it is already scrubbed and schema-shaped.

## 3. Sampling (what gets traced at all)

| Mode | Policy | Use |
|---|---|---|
| dev | 100% | everything, while building |
| eval | 100% | the eval set is the point |
| prod | 10–20% + all failures | cost vs signal |

```python
def should_trace(run_id: str, outcome: str | None = None) -> bool:
    if ENV == "dev" or ENV == "eval":
        return True
    if outcome in ("failed", "degraded"):
        return True                     # failures always trace
    return int(hash(run_id), 16) % 10 < 2
```

The sampling rule: failures always trace, successes sample — the
W13-nightly-report logic applied to tracing volume. The hash-based
sampling is deterministic per run (same run_id → same decision), which
keeps the trajectory store and the traced subset consistent.

## 5. The hygiene pin note (the privacy page)

```markdown
# Trace hygiene (W15)
- scrubber: 4 patterns, runs at export boundary only
- local raw: 30-day rotation, full fidelity
- parquet store: indefinite, scrubbed, schema-shaped
- sampling: dev/eval 100%; prod 20% + all failures (deterministic)
- hosted retention: set per policy (checked, not defaulted)
```

The hygiene page is the privacy policy for traces — the W11 hygiene
rules (firewall at export, sanitize both directions) plus the W15
additions (retention, sampling). It is the page a privacy reviewer
reads; every rule cites its test.

## Exercises

1. Wire the scrubber into the export boundary; plant PII in a run; the
   exported trace is clean while the local JSONL has full detail.
2. Retention drill: run the rotation; verify old traces prune and the
   parquet survives.
3. Sampling drill: run 100 prod-mode invocations; ~20% trace, and every
   failed run traces — the policy, measured.
4. Pin drill: write the page; every rule cites its drill.

## Pitfalls

- Scrubbing the *local* trace too — debugging needs full fidelity; scrub
  at export only.
- Sampling that drops failures — failures are the signal; the outcome-
  based rule overrides the rate.
- Retention "forever" on the hosted platform — check and set it; the
  platform default is not your policy.