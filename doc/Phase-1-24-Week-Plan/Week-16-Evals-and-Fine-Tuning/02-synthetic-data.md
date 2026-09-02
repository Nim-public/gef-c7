# 02 — Generating Synthetic Data

> Week 16 index: [README.md](README.md)

**Session 1 topic:** *Generating Synthetic Data.*

---

## What you'll learn

- What synthetic data is for: eval sets, fine-tuning sets, adversarial cases
- Generation patterns: seed-conditioned LLM generation, persona/parameter variation, self-instruct
- Validation: how to keep synthetic data from poisoning your metrics
- Ethics/licensing guardrails for synthetic corpora

## 1. What synthetic data is for (and not for)

| Use | Legitimate? | Notes |
|---|---|---|
| **Eval cases** at volume | ✅ | expand a 25-case golden set to 200; seeds hand-labeled, variants generated |
| Fine-tuning data (style/format tasks) | ✅ | when real examples are scarce; distillation-style (W3-05) |
| Adversarial batteries (injection, edge cases) | ✅✅ | the highest-value use — coverage you can't hand-write |
| Replacing real data wholesale for *knowledge* | ❌ | W3-05's rule: facts come from your corpus/RAG, not from a model's imagination |
| Benchmark bragging | ❌ | synthetic-on-synthetic evaluation is circular |

## 2. Generation patterns

### Pattern A — seed-conditioned expansion (eval sets)

Start from real, hand-labeled seeds; generate paraphrases and variations:

```python
EXPAND_PROMPT = """You are expanding a test set for a support-intent classifier.

Seed question: "{seed}"
Label: {label}

Generate {n} variations that a real user might write, covering:
- typos and abbreviations
- a different language mixed in
- a longer, rambling version
- an adversarial version (prompt-injection embedded)

Return JSON: [{{"text": "...", "label": "{label}", "kind": "typo|mixed|rambling|adversarial"}}]"""
```

Every variation inherits the *hand* label — which is why seeds must be trusted (human-labeled) before expansion. 20 seeds → 200 cases in an hour.

### Pattern B — persona/parameter sweep (coverage)

Parameterize by the dimensions your system varies on:

```python
personas = ["frustrated customer", "new user", "engineer", "executive"]
channels = ["email", "chat", "phone-transcript"]
intents  = ["billing", "technical", "account"]

for p, c, i in itertools.product(personas, channels, intents):
    case = generate_case(p, c, i)          # one LLM call per cell
```

This guarantees *coverage* — the grid exposes the cell your routing (W12-05) silently fails on.

### Pattern C — adversarial generation (red-team at scale)

```python
ATTACK_PROMPT = """Generate 5 novel prompt-injection attempts against a support agent
that has tools: search_knowledge, sql_query (read-only), issue_refund (gated).
Vary: encoding tricks, role-play framing, indirect (document-embedded) injection.
Return one attempt per line."""
```

Feed the output to your guardrail battery (W3-02/W11-02). Anything that passes your guards becomes a regression test *and* a hardening ticket — the generator is your red team.

### Pattern D — self-instruct / distillation (fine-tuning data)

For LoRA training (file 04): take your pipeline's *best* outputs (frontier model, verified by your checks) as (instruction → response) pairs — the W3-05 distillation lever. Quality gate every row (citation present, numbers supported, format valid) before it enters the training set.

## 3. Validation: keeping synthetic data honest

| Check | How |
|---|---|
| **Label validity** | hand-audit a sample (20% minimum); drop or relabel |
| **Diversity** | embedding-cluster the set (W2-03); flag single-cluster domination |
| **Leakage** | near-duplicates between train and eval sets (cosine > 0.95) — split *before* generating variants |
| **Distribution** | per-label/per-kind counts vs intended grid; report gaps |
| **Detectability** | can a classifier tell synthetic from real? (If trivially yes, your evals are self-fulfilling) |

```python
import numpy as np

def dedup_by_embedding(texts, model, thresh=0.95):
    embs = model.encode(texts, normalize_embeddings=True)
    sims = embs @ embs.T
    keep, dropped = [], []
    for i in range(len(texts)):
        if max((sims[i, j] for j in keep), default=0) > thresh:
            dropped.append(texts[i])
        else:
            keep.append(i)
    return keep, dropped
```

## 4. Guardrails (ethics/licensing)

- **No real-PII synthesis from real records** — generate PII-shaped *placeholders*, or use your W2-02 scrubber before any LLM sees real rows
- **License the seeds** — generated data inherits the seed's provenance claims; document sources (W7-01)
- **Disclose synthetic content** — in datasets shipped to others, and in demo answers when asked ("this example is synthetic")
- **Bias checks** — synthetic personas can encode stereotypes (your personas *are* a distribution); review the grid for skew before training on it

## Exercises

1. Expand 15 hand-labeled seed questions ×4 variations (Pattern A); hand-audit 20% — what % of labels survived? That ratio is your generator's trust score.
2. Run the persona×channel×intent grid (Pattern B) over your router (W12-05); heatmap route accuracy per cell — find the dead cell.
3. Generate 10 novel injections (Pattern C); run your W3-02/W11-02 battery — how many get through? Harden one guard, rerun.
4. Leakage check: build train/eval splits *before* expanding variants; run the embedding dedup (§3) across the split — did any near-duplicates leak?
5. Distillation prep: collect 50 verified answers from your W11 agent (citations + grounding checks passed); format as a LoRA training JSONL (file 04's format). Validate 10 by hand.

## Pitfalls

- **Synthetic-on-synthetic evals** — generator and judge from the same model family with the same prompts = agreement by construction
- **Label inheritance errors** — one mislabeled seed × 20 variations = 20 poisoned cases
- **Grid without weights** — uniform personas don't match real traffic; weight generation by observed query distribution (your W10-04 logs)
- **Training on synthetic *facts*** — invented policies/prices become confident training targets (W3-05's rot, accelerated)
- **Adversarial generator as a toy** — novel attacks that pass your guards are tickets, not trivia (W12-05's hardening loop)

## Resources

- Wang et al., *Self-Instruct* — the seed-expansion pattern's origin
- Eldan & Li, *TinyStories* — synthetic data enabling capability (the extreme case, for perspective)
- Anthropic/OpenAI synthetic-data guidance + [presidio](https://microsoft.github.io/presidio/) for PII placeholders
- W5-05 (judge discipline), W10-04 (logs), W16-03/04 — the consumers of what you generate here
