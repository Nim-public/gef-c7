# 02 — A/B, Shadow & Canary Deployment

> E8 index: [README.md](README.md)

**Core topics:** *A/B testing, shadow deployment, and canary releases for agent changes.*

---

## What you will be able to do after this week

- [ ] Run an A/B test for an agent change with statistical validity (not vibes)
- [ ] Deploy changes in shadow mode (run, don't serve) before user exposure
- [ ] Use canary releases with automated rollback on metric regressions
- [ ] Choose the deployment strategy per change class (prompt, model, tool, routing)

## 1. The deployment strategies

| Strategy | Mechanism | Use when |
|---|---|---|
| **A/B test** | split traffic; compare metrics on both arms | measuring a *claimed* improvement |
| **Shadow** | new version runs on real traffic; outputs logged, **not served** | validating parity/safety without user risk |
| **Canary** | 1% → 5% → 25% → 100% with auto-rollback thresholds | staged exposure of a validated change |
| **Blue-green** | two full environments, instant switch | infra-level changes |

The agent-specific twist: quality metrics need **judges/evals** (W5-05, W16-01), not just latency/error rates — so A/B and shadow both need your eval stack wired to live traffic.

## 2. A/B testing agent changes

```python
import hashlib

def arm(user_id: str) -> str:
    """Deterministic 50/50 split — sticky per user."""
    h = hashlib.sha256(f"{user_id}:triage-v8".encode()).hexdigest()
    return "B" if int(h[:8], 16) % 2 else "A"

def handle(user_id, question):
    arm_name = arm(user_id)
    agent = AGENT_B if arm_name == "B" else AGENT_A
    result = agent.handle(question)
    log_experiment("triage-v8", user_id, arm_name,
                   {"success": result.success, "tokens": result.tokens,
                    "latency": result.latency, "citations": result.citations})
    return result
```

Design rules:

- **Deterministic stickiness** — same user, same arm, every time (hash, not random per request)
- **Pre-register the metric and threshold** — "success rate must improve ≥3 points at p<0.05" decided *before* looking (W16-01's discipline)
- **Sample size first** — with a 3-point expected lift you need ~1,000+ per arm for significance; compute before starting (W5-05's n-with-every-metric rule)
- **Track both arms' guardrails** — the E7 battery runs on B *before* exposure
- **Log per-arm** with the W10-04 schema — the experiment's analysis is a groupby

## 3. Shadow deployment (run, don't serve)

The new agent processes live traffic but its answers go to logs only:

```python
def shadow_handle(question, user_id):
    main_answer = AGENT_A.handle(question)                       # served
    try:
        shadow = run_budgeted(AGENT_B, question, RunBudget(max_seconds=8))
        log_shadow(user_id, question, main_answer, shadow)       # compare offline
    except Exception as e:
        log_shadow_failure(e)                                    # shadow failures are free lessons
    return main_answer
```

What shadowing validates cheaply: crash rate on real traffic, latency distribution, tool-call patterns, guardrail trip rates — everything except *user-perceived quality* (which needs A/B). The comparison runs through your W16-01 eval sets + spot-check judges.

**Shadow for every risky change first**: new model (W2-05), new prompt (W3-02), new router threshold (W15-04), new tool (W10-02). The W15-05 optimization ledger's "attribution" claims become shadow-verified before A/B.

## 4. Canary with auto-rollback

```python
CANARY_PLAN = [{"pct": 1, "minutes": 60}, {"pct": 5, "minutes": 120},
               {"pct": 25, "minutes": 240}, {"pct": 100}]

ROLLBACK_IF = {"error_rate": 0.03, "p95_latency": 8.0, "guard_trips_per_1k": 15,
               "thumb_down_rate": 0.15}
```

Promote only while metrics hold; any threshold breach → auto-revert to the manifest's previous version (E8-01's rollback) + alert (W15-02). The thresholds come from the W15-05 baseline ×1.5 headroom — the same discipline as W11-05's budget assertions.

## 5. Strategy per change class

| Change | Path |
|---|---|
| prompt wording tweak | shadow → A/B (if user-visible) → deploy |
| model swap (W2-05) | shadow (parity battery) → canary |
| new tool (W10-02) | shadow on read-only → gated write → canary |
| router threshold (W15-04) | offline sweep → shadow → canary |
| fine-tuned adapter (W16-04) | eval gate → shadow → canary |
| security control (E7) | battery green → canary with extra monitoring |

## Exercises

1. Implement `arm()` + experiment logging; run a 2-week A/B on a prompt change with a pre-registered threshold; report with sample size and p-value.
2. Shadow-drill: deploy a *deliberately broken* agent (dropped citations) in shadow; verify users were unaffected and the shadow logs revealed the breakage.
3. Canary drill: write the promotion script with auto-rollback on `error_rate`; simulate a metric breach (inject errors); verify auto-revert fires.
4. Sample-size math: expected lift 2 points, baseline 85%, α=0.05, power 0.8 — compute n per arm (any calculator); what does that mean for your traffic?
5. Change-class table: apply §5's mapping to your capstone's next 5 planned changes — write the deployment path for each.

## Pitfalls

- **Peeking and stopping early** — stopping the A/B the moment B looks ahead is p-hacking; pre-registered thresholds only (W16-01)
- **Non-sticky arms** — users flip versions mid-conversation; sessions confound the experiment
- **Shadow without parity checks** — shadow logs nobody reads are theater; the W16-01 comparison runs on shadow data too
- **Canary without auto-rollback** — a canary that needs a human at 3 a.m. is a canary in name only
- **Testing on synthetic traffic only** — shadow/A/B must run on *real* distribution (W16-02's synthetic ≠ prod)

## Resources

- W15-01/02/05 (reliability, tracing, baselines) + W16-01 (eval versioning) — the composed layers
- [LaunchDarkly experimentation docs](https://docs.launchdarkly.com/) / [Unleash](https://docs.getunleash.io/) — feature-flag + experiment infrastructure patterns
- Kohavi et al., *Trustworthy Online Controlled Experiments* — the A/B methodology bible (ch. 2–3)
- LangSmith [experiments](https://docs.smith.langchain.com/) — hosted A/B for prompts/models
