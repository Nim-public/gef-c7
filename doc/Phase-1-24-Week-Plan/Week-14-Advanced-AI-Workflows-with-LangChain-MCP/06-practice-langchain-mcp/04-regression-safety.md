# Regression & Safety Integration — The Gates That Keep It Shipped

**What you'll learn:** the final CI integration: every gate the program
built, one workflow, one acceptance command — the system's complete
safety net, documented and mutation-tested.

## 1. The gate inventory

| Gate | Source week | CI slot |
|---|---|---|
| ingestion validation (V1–V8) | W7 | per ingest |
| parity tests (schemas, capture) | W9/W11/W13 | every push |
| trajectory + battery suites (canned) | W10–W12 | every push |
| real-model batteries | W11–W12 | nightly |
| retrieval + numeric value gates | W7/W13 | nightly |
| regression baselines (all) | W7+ | nightly |
| safety batteries (injection, containment) | W9/W13/W14 | every push + nightly |

```yaml
# .github/workflows/gates.yml (excerpt)
push:    [fast-batteries, containment, parity]
nightly: [real-model, value-gates, regression-baselines]
pre-demo: [accept.py --full]
```

The gate inventory is the program's safety net, one table — every gate
cites its week, and every week's gates still run. Nothing was built and
abandoned; that is the integration's whole point.

## 2. The mutation map (every gate has a planted bug)

| Gate | Mutation that must trip it |
|---|---|
| validation | corrupt one hash |
| parity | drift one schema |
| canned battery | break one tool description |
| value gate | degrade one metric |
| containment | remove one wall |
| injection battery | weaken one firewall |

The mutation map is the gates' own test suite — each gate proven by its
planted failure. The drill results live in `reports/mutation-map.md`
and re-run quarterly (or before any demo).

## 3. The acceptance command (one command, whole system)

```bash
py scripts/accept.py --full
# [1/6] ingest gates ......... PASS
# [2/6] parity ............... PASS
# [3/6] canned batteries ..... PASS
# [4/6] safety batteries ..... PASS
# [5/6] four pillars demo .... PASS
# [6/6] mutation spot-checks . PASS
```

The acceptance command is the W13-06 pattern, final form — six gates,
one verdict each, runtime under 10 minutes. It is the command a reviewer
runs, the command CI runs, and the command you run at 2 a.m.

## 4. The safety documentation (the capstone's security chapter)

```markdown
## Safety (capstone README chapter)
- Containment: per-server scopes (W14-02) + sandbox (W13-04)
- Injection: layered defenses, federated battery (W14-04)
- HITL: gate policy + interrupts (W10-04, W13-06)
- Numeric: verification policy + mismatch drills (W12-04)
- Escape drills: codegen sandbox (W13-04-02)
```

The chapter is the safety documentation's index — each line links to
its drills and artifacts. The reviewer's security questions are
answered before they are asked.

## 5. The gate onboarding (how a new gate joins)

```text
1. the gate is a test (pytest) or a script step
2. it has a mutation (a planted bug that trips it)
3. it has a CI slot (push / nightly / pre-demo)
4. it joins the inventory table + the acceptance command
5. its first mutation run is committed as evidence
```

The onboarding is the gate's five-step entry — the same procedure every
gate in the inventory followed. A new safety idea without these five
steps is a wish; the onboarding is what makes it a gate.

## Exercises

1. Wire the gate inventory into the workflow; verify each gate's CI slot
   runs on schedule.
2. Mutation-map drill: run every mutation; every gate trips; restore;
   every gate green — the map is committed.
3. Acceptance drill: run `accept.py --full` from a fresh clone; all six
   gates PASS under the time budget.
4. Documentation drill: the safety chapter's every link resolves to a
   committed artifact; no dead links, no vibes.
5. Onboarding drill: add one new gate through the §5 procedure (e.g., a
   prompt-injection spot-check for the analytics path); its first
   mutation run committed.

## Pitfalls

- Gates that exist in the inventory but not in CI — the inventory is the
  CI config or it is fiction.
- Mutation drills run once, in the past — quarterly re-runs or the walls
  rot.
- The acceptance command that needs "just one manual step" — automation
  or it is not acceptance.