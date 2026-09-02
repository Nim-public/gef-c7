# 05 — Practice: The Full LLMOps Loop

> E8 index: [README.md](README.md) · **Due: before E9**

*(Practice build — registry, CI/CD gates, A/B + shadow + canary, cost ledger, and OTel observability operating together on your capstone agent.)*

---

## 1. Deliverable

```
llmops/
  registry/
    manifest.yaml            # the deployment manifest (E8-01 §1)
    versions/                # pinned artifacts per release
  ci/
    agent-cd.yml             # the 4-gate workflow (E8-01 §2)
    run_regression.py        # W15-02 hosted evals, CLI
  deploy/
    router.py                # arm() + canary plan (E8-02)
    shadow.py                # shadow runner (E8-02 §3)
    rollback.py              # tested rollback script
  cost/
    ledger.py                # the token ledger (E8-03 §1)
    budgets.py               # FeatureBudget + degradation (E8-03 §2)
    forecast.md              # the growth curve (E8-03 §4)
  otel/
    instrumentation.py       # OTel spans (E8-04 §2)
    dashboard.json           # Grafana dashboard export
    alerts.md                # the alert set + thresholds (E8-04 §4)
  eval/
    results.md               # the LLMOps results: A/B numbers, rollback drill, cost table
  README.md                  # the operating manual
```

Demo: a prompt change walks the full loop — PR opens → 4 CI gates run → canary promotes 1%→100% with metrics → one simulated regression triggers auto-rollback — then the cost/latency table shows the change's effect.

## 2. Requirements (graded)

### Registry + CI/CD (file 01)
- [ ] Deployment manifest pinning model/prompts/tools/router/eval-set versions
- [ ] CI with the 4 gates (unit, eval regression, security battery, budget check) — demonstrated catching a planted regression
- [ ] Rollback drill completed in <10 minutes, verified by eval parity

### Deployment strategies (file 02)
- [ ] Deterministic A/B split with experiment logging (pre-registered metric/threshold)
- [ ] Shadow runner demonstrated with a deliberately broken candidate (users unaffected, breakage visible)
- [ ] Canary script with auto-rollback thresholds from your baseline (drill: simulated breach → revert)

### Cost + observability (files 03/04)
- [ ] Token ledger with feature attribution + cached-token column; one-week table
- [ ] FeatureBudget with SLM-path degradation (W15-04) on breach — load-tested
- [ ] OTel spans (agent/retrieval/tool) exported; dashboard with ≥4 panels; alert set tuned

## 3. Rubric

| Area | Weight |
|---|---|
| Registry + CI/CD gates (enforcement, rollback drill) | 25% |
| Deployment strategies (A/B rigor, shadow, canary auto-rollback) | 25% |
| Cost ledger + budgets + forecast | 20% |
| OTel instrumentation + dashboard + alerts | 20% |
| README operating manual | 10% |

## 4. README operating manual (answer explicitly)

1. **Deployment topology**: manifest, environments, promotion gates (E8-01 §4's ladder)
2. **Change playbook**: for each change class (W14's §5 table), the exact deployment path
3. **Incident playbook**: budget breach, quality regression, guard-trip spike, cost anomaly — who gets paged and what's the first action (E8-04 §4)
4. **The ledger**: current per-feature costs, the optimization ledger, and the 6-month forecast
5. **E9 bridge**: the moving-baseline problem — your memory-based agent (E9) changes behavior over time by design; which of these gates/metrics must become *distributional* (comparing against a rolling baseline) rather than static? (One paragraph — E9 opens with it.)

## 5. Stretch (pick one)

- Progressive delivery end-to-end: canary with per-feature (not global) rollout percentages — the router ships features, not just models
- Cost anomaly detection: a simple model on the ledger forecasting daily spend; alert on deviation (E8-04's alert set, predictive)
- Multi-tenant quotas: per-user FeatureBudget with the E8-03 degradation mode — and the abuse log that catches the user who trips it

Bring the operating manual to your next mentor session: the capstone phase asks "is this production-ready?" — this manual is the yes, with the drills as proof.
