# Port Methodology — W10 Agent to SDK Primitives

**What you'll learn:** the port, component by component, in an order
that keeps the battery green at every step — the migration discipline
from Week 09's LanceDB file, applied to your own agent.

## 1. The port order (battery-green at each step)

| Step | Port | Battery gate |
|---|---|---|
| 1 | tools → `@function_tool` | error fidelity (hints intact) |
| 2 | loop → `Runner.run` + `max_turns` | trajectory shapes match |
| 3 | constitution → `instructions` | constitution cases 7/7 |
| 4 | typed output → `output_type` | citation validator catches phantoms |
| 5 | history → `SQLiteSession` | budget drills (trim pattern) |
| 6 | guardrails → input/output | tripwires fire on battery cases |
| 7 | instrumentation → traces | parity test ≤5% |

Never two components at once: the battery is the migration's continuous
integration, and each row's gate is *the same test that validated the
W10 original* — that is what makes the comparison honest.

## 2. The component mapping, finalized

| W10 component | SDK primitive | Status after port |
|---|---|---|
| `run_react` loop | `Runner.run` | replaced |
| `ToolRegistry.call` | `@function_tool` + handler | logic preserved, skin replaced |
| error contracts | `failure_error_function` + raises | preserved verbatim |
| gates (HITL) | `needs_approval` callback | preserved |
| context fitter | **manual** — trimmed-list pattern | still yours |
| trajectory store | traces → merge (file 05-03) | dual capture, one store |
| anti-pattern detectors | harness over spans | still yours |

The "still yours" rows are the port's honest remainder: the SDK moved
the *mechanism*; it did not move your *policies*.

## 3. Port-then-delete (no parallel paths)

The migration's end state: the W10 loop is deleted, not shelved behind a
flag. The comparison (file 02) happens *before* deletion; after it, one
implementation remains:

```text
git rm scripts/handrolled_agent.py        # after the verdict memo
# the SDK implementation is now the only path; the W10 tests
# (trajectory shapes, battery) run against it unchanged
```

The test suite survives the port unchanged — that is the proof the port
is behavior-preserving. Tests are the contract; implementations are
fungible.

## 4. What the port *teaches* (the real deliverable)

| Insight | Where it shows |
|---|---|
| your 50-line loop ≈ the SDK's 4 documented steps | the loop was never the hard part |
| context fitting was always manual | SDKs do not solve budgets |
| the registry was two layers: contract + transport | decorators are the transport |
| traces replace hand instrumentation *if* merged | observability is a schema problem |

## Exercises

1. Port in the §1 order; at each step run the named battery gate; record
   the green/red sequence — the port's commit history *is* the evidence.
2. Mapping-freeze drill: after step 7, re-write the mapping table from
   the final code; diff against §2 — any drift is an undocumented
   decision.
3. Delete drill: remove the W10 loop; run the full suite (shape + value
   + battery); confirm green with no flag-flipping.

## Pitfalls

- Porting two components per step — a red battery then names no culprit;
  one component per commit.
- Keeping the hand-rolled path "just in case" — parallel paths diverge
  silently; delete after the verdict.
- Porting the *fitter* into the SDK "somehow" — it stays manual; forcing
  it into SDK idioms loses the property tests.

## Resources

- All five prior subfolders — each port step links there.
- [`../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/`](../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/)
  — the migration discipline this reuses.