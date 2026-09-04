# 02.4 — Zero-Shot Classification via NLI

> Subfolder index: [README.md](README.md) · Parent: [../02-ready-to-use-models.md](../02-ready-to-use-models.md)

---

## What you'll learn

- The NLI entailment mechanism — why "labels as hypotheses" works at all
- Template sensitivity, measured
- Multi-label vs multi-class mode and the scoring difference
- When zero-shot beats trained classifiers — with the boundary cases

## 1. The NLI mechanism

A zero-shot classifier is a **Natural Language Inference** model: trained to judge whether a *premise* entails, contradicts, or is neutral toward a *hypothesis*. Zero-shot classification repurposes it:

```text
premise    = "My laptop battery drains within two hours after the update."
hypothesis = "This example is about hardware issues."
           → ENTAILS  → score the label "hardware issue" high
```

Each candidate label becomes a hypothesis; the model scores all of them; softmax across labels (multi-class mode) or sigmoid per label (multi-label mode) produces the ranking:

```python
from transformers import pipeline

zsc = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

zsc("My laptop battery drains within two hours after the update.",
    candidate_labels=["hardware issue", "software bug", "billing", "account access"])
# {'labels': ['hardware issue', ...], 'scores': [0.72, 0.21, ...]}

# multi-label mode — labels judged independently:
zsc(text, candidate_labels=[...], multi_label=True)
```

| Mode | Scoring | Use |
|---|---|---|
| multi-class (default) | softmax across labels — they compete | exactly one category |
| `multi_label=True` | sigmoid per label — independent | overlapping categories ("billing AND technical") |

## 2. Template sensitivity, measured

The default hypothesis is `"This example is {}."` — and wording moves scores dramatically:

```python
templates = [
    "This example is about {}.",
    "The customer is complaining about {}.",
    "This text discusses a problem with {}.",
]
for tpl in templates:
    out = zsc(text, candidate_labels=labels,
              hypothesis_template=tpl)
    print(tpl, "->", out["labels"][0], round(out["scores"][0], 3))
```

Run it: the top label can flip between templates. The W2-02 claim ("label wording strongly affects scores") is measurable in one cell of this experiment — and the fix is the same discipline as prompts: **test templates on your data, pin the winner** (W3-01's template rule applied to NLI).

## 3. Where zero-shot wins and loses

| Scenario | Zero-shot | Trained classifier (W1-05) |
|---|---|---|
| labels change weekly | ✅ edit the list | ❌ retrain |
| < 50 labeled examples | ✅ no training data | needs data |
| fixed labels, 1M/day | ❌ slow (N passes) | ✅ ms latency |
| need calibrated confidence | ⚠️ uncalibrated | ✅ calibratable |
| cross-lingual | ✅ with XNLI models | per-language models |

The W1-05 taxonomy's place: zero-shot is the *bootstrap* — use it to label seed data, train the fast classifier, and retire the zero-shot calls from the hot path (the W2-02 §5 pattern).

## 4. The calibration caveat (and the fix path)

Zero-shot scores are softmax over entailment logits — not calibrated to your decision costs. The fix path:

1. collect 50–100 labeled examples (the zero-shot output can *bootstrap* labels for review)
2. fit a calibration (Platt/isotonic) on the scores, or
3. graduate to the trained classifier (W1-05) once labels exist

Track the calibration curve (W5-04 ex. 3's reliability diagram) whenever the label set changes — every edit reshapes the score distribution.

## Exercises

1. Template sweep: 5 templates × 20 questions; measure top-1 agreement across templates — the disagreement rate is your template sensitivity.
2. Multi-label drill: 10 texts with overlapping categories; compare multi-class vs `multi_label=True` outputs — which matches the true labels?
3. Cross-lingual: XNLI model on Hindi questions with English labels — quality vs the English baseline.
4. Bootstrap workflow: zero-shot label 100 unlabeled tickets → hand-verify 40 → train the W1-05 classifier on verified labels → compare zero-shot vs trained on the held-out 60.
5. Threshold calibration: reliability diagram for zero-shot scores on 50 labeled cases — is 0.7 "hardware issue" actually right 70% of the time?

## Pitfalls

- **Single-word labels on domain jargon** — "SSO" as a label means nothing to the NLI model; expand to a phrase ("single sign-on login system")
- **Label sets that overlap** — "billing" and "refunds" compete in multi-class mode; use multi-label or merge
- **Score calibration assumed** — 0.72 isn't 72% accuracy; calibrate or use rankings only
- **Multi-class mode for multi-label data** — independent labels forced to sum to 1 distort everything
- **Template drift between runs** — changing `hypothesis_template` mid-project silently changes the system (W16-01's versioning)

## Resources

- Yin et al., *Benchmarking Zero-shot Text Classification* — the NLI-repurposing analysis
- HF [zero-shot classification docs](https://huggingface.co/docs/transformers/tasks/zero_shot_classification)
- [facebook/bart-large-mnli](https://huggingface.co/facebook/bart-large-mnli) card — the training details
- W1-05 (trained classifiers) — the comparison partner
