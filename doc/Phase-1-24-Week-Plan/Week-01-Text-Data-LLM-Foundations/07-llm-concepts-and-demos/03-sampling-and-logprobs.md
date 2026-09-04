# 07.3 — Sampling & Logprobs

> Subfolder index: [README.md](README.md) · Parent: [../07-llm-concepts-and-demos.md](../07-llm-concepts-and-demos.md)

---

## What you'll learn

- Temperature/top_p as distribution surgery — with plots
- Logprob-based confidence, classification, and routing
- The determinism stack: temperature, seed, and what still varies

## 1. Temperature as distribution surgery

```python
import numpy as np
import matplotlib.pyplot as plt

logits = np.array([2.0, 1.2, 0.8, 0.1, -0.5])
labels = ["GPU", "CPU", "RAM", "SSD", "case"]

def softmax(z, temp=1.0):
    e = np.exp(z / temp); return e / e.sum()

fig, axes = plt.subplots(1, 4, figsize=(14, 3))
for ax, t in zip(axes, [0.2, 0.7, 1.0, 2.0]):
    ax.bar(labels, softmax(logits, t)); ax.set_title(f"T={t}")
plt.tight_layout(); plt.savefig("temperature.png")
```

The four panels are the whole lesson: T→0 concentrates on the argmax (near-deterministic); T=1 samples the raw distribution; T→2 flattens toward uniform. `top_p` composes: it truncates the distribution to the smallest set covering probability p *before* renormalization — tune temperature **or** top_p, not both blind.

## 2. Task-appropriate settings

| Task | Setting | Why |
|---|---|---|
| extraction/classification/routing | T=0 (or 0.1) | reproducibility beats variety |
| summaries | T=0.3–0.5 | slight variation, low hallucination pressure |
| creative naming/brainstorm | T=0.8–1.0 | diversity is the point |
| eval runs | T=0 + fixed seed | W16-01's determinism rule |

**Production default: the lowest temperature that passes your eval** — variety is a cost unless measured as a benefit (W10-04's A/B on temperature, file 05-02).

## 3. Logprobs — the confidence layer

```python
resp = client.chat.completions.create(
    model="gpt-4o-mini", temperature=0, logprobs=True, top_logprobs=5,
    messages=[{"role": "user", "content": "Is 17 prime? Answer yes or no."}])

for tok in resp.choices[0].logprobs.content:
    print(f"{tok.token!r:8} logprob={tok.logprob:.3f} prob={2.718281828**tok.logprob:.4f}")
    for alt in tok.top_logprobs:
        print(f"    alt {alt.token!r:8} {2.718281828**alt.logprob:.4f}")
```

Three applications (W1-07 previewed; here measured):

1. **Confidence gating** — low probability of the emitted answer → escalate to human or the frontier model (W5-04's hook)
2. **Zero-shot classification** — compare P("Positive") vs P("Negative") directly from top-logprobs — no classifier training (W1-05's contrast)
3. **Distribution inspection** — "the model was 51/49 between two labels" changes how you trust the output (E10-02's probing, applied)

Caveats: logprobs are *post-sampling-recipe* and only loosely calibrated; some endpoints don't provide them; top_logprobs has a max (typically 5–20).

## 4. The determinism stack (what you can and can't pin)

| Control | Effect | Guarantee level |
|---|---|---|
| `temperature=0` | greedy (argmax) | near-deterministic |
| `seed` | reproducible sampling *given identical infra* | best-effort |
| pinned model revision | same weights | strong |
| serving infra | batching order can perturb float sums | not guaranteed |

Test empirically: same prompt, seed, temperature 0, called 5× — identical? (Usually yes on the same day; occasionally not across infra changes.) Design systems that tolerate drift rather than require bit-identity (W15-02's distributional baselines).

## Exercises

1. Temperature plots: for 3 different prompts, render the top-5 probability bars at T ∈ {0.2, 0.7, 1.5} — annotate where ordering flips.
2. Confidence audit: 30 classification calls; compare emitted-label logprob against correctness — build the reliability diagram (W5-04 ex. 3's pattern).
3. Zero-shot vs trained: the W1-05 ticket classifier vs logprob zero-shot on the same 40 tickets — accuracy, cost, latency table.
4. Determinism probe: 10 identical calls at T=0 with the same seed — count mismatches; then across two days — recount.
5. Routing integration: feed the logprob confidence into the W15-04 router's escalation rule — measure the escalation rate on benign traffic.

## Pitfalls

- **Both temperature and top_p tuned together** — compounding effects; fix one, sweep the other
- **Logprobs read as calibrated probabilities** — they're model-internal confidences; calibrate on labeled data before gating decisions
- **High temperature on data pipelines** — variety in extracted fields breaks downstream parsers (W15-01's determinism requirement)
- **top_p with tiny values** — truncates to 1–2 tokens; output collapses
- **Seed as a promise** — infra changes can break reproducibility; verify rather than assume (W15-03's freeze rule)

## Resources

- OpenAI [logprobs docs](https://platform.openai.com/docs/api-reference/chat/create) — parameters and limits
- W1-07 (parent), W15-04 (routing), W16-01 (determinism in evals) — composed here
- OpenAI Cookbook, *Using logprobs* — the confidence-application recipes
