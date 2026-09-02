# 05 — Practice: Red-Team Your Capstone Agent

> E7 index: [README.md](README.md) · **Due: before E8**

*(Practice build — the full security exercise: threat model, automated red-team, triage, hardening, and the capstone security section.)*

---

## 1. Deliverable

```
security/
  threat_model.md        # file 01 §4 worksheet (assets, actors, risks, controls)
  redteam/
    taxonomy.jsonl       # the attack matrix (file 02 §1: families × templates)
    run_redteam.py       # orchestration + judge (file 03 §2)
    results.jsonl        # every attack + outcome + verdict
  battery/
    test_battery.py      # pytest: all bypass regressions (file 03 §4)
  sandbox/
    runner.sh            # the tier-2 container runner (file 04 §2)
    egress_report.md     # egress audit (file 04 ex. 2)
  README.md              # security section: threats, controls, accepted risks
```

Demo: a live red-team run (15 attacks) with the per-family table; one critical bypass traced to root cause and fixed; the sandbox refusing three escape attempts.

## 2. Requirements (graded)

### Threat model (file 01)
- [ ] Worksheet complete: assets, actors, top-3 risks by blast radius, controls with evidence links
- [ ] Accepted risks documented with justification

### Red-team (files 02/03)
- [ ] Attack matrix: ≥5 families × ≥3 variants = ≥15 cases, including encoding + multi-turn
- [ ] Automated run with judge (calibrated ≥0.8 agreement on 20 hand-labeled outcomes)
- [ ] Per-family pass table + benign false-block rate ≤5%

### Hardening (file 04)
- [ ] Tier-2 sandbox for any code execution (`--network none`, read-only, capped)
- [ ] Egress audit: one day of proxy logs reviewed; allow-list enforced
- [ ] Blast-radius table completed for every capstone tool

### Regression (file 03 §4)
- [ ] All fixed bypasses in the pytest battery
- [ ] Deliberate-guardrail-removal drill caught by the suite

## 3. Rubric

| Area | Weight |
|---|---|
| Threat model (worksheet quality, blast-radius ranking) | 20% |
| Red-team coverage + automation (families, judge, benign controls) | 30% |
| Triage + hardening (fixes, sandbox, egress) | 25% |
| Regression suite (bypasses as tests) | 15% |
| README security section (evidence-linked) | 10% |

## 4. README security section (answer explicitly)

1. **Threat model** (file 01 §4 worksheet, final version)
2. **Red-team results**: per-family pass rates, top bypasses, judge calibration numbers
3. **Controls inventory**: every control with its evidence artifact (test, config, log)
4. **Accepted risks**: explicit list with justifications
5. **E8 bridge**: your LLMOps posture — which security controls (gates, budgets, tracing) need to survive *deployment automation* (registries, CI/CD), and where does deployment itself become an attack surface? (One paragraph — E8's security angle, pre-identified.)

## 5. Stretch (pick one)

- PyRIT integration: port your taxonomy into PyRIT's orchestrator; compare coverage vs your hand-rolled loop
- Fuzzing the tool schemas: malformed/oversized tool args (W10-02 validators) at 10× scale — crash or degrade?
- Social-engineering eval: multi-turn escalation across *sessions* (episodic memory, file E9) — does remembered context amplify attacks? (Yes — test it.)

Bring the red-team table and the threat model to your next mentor session: the capstone's security section is only credible with attack evidence — this practice is that evidence.
