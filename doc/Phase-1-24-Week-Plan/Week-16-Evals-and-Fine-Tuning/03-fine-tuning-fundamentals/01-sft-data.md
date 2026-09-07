# SFT Data — Formatting, Masking, Distribution Matching

**What you'll learn:** the SFT dataset: chat-format records with *loss
masking* (train on responses, not prompts), and a distribution that
matches the deployment task — the data decides the fine-tune.

## 1. The record format

```json
{
  "messages": [
    {"role": "system", "content": "You are a corpus QA agent..."},
    {"role": "user", "content": "Which chart shows Q3 margin?"},
    {"role": "assistant", "content": "Chart u042 shows gross margin 12.4%. [u042]"}
  ]
}
```

| Element | Rule |
|---|---|
| system | the deployment constitution, verbatim |
| user | queries from the real distribution |
| assistant | answers in the *exact* deployment format (citations included) |

The assistant turns teach the model its deployment behavior — format,
citation style, refusal phrasing. A fine-tune on answers without
citations produces an agent that stops citing; the data's format *is*
the behavior.

## 2. Loss masking — train on responses only

```text
prompt tokens:   [MASKED]  (no loss)
response tokens: [TRAINED] (loss computed)
```

Masking the prompt means the model learns to *produce* answers, not to
*parrot* questions. Most frameworks implement it (chat templates with
`train_on_inputs=False` or loss masks); the audit (file 02) verifies
the mask landed — a masking bug teaches the model to generate prompts.

## 3. Distribution matching (the deployment-task rule)

| Source | Share | Why |
|---|---|---|
| real queries (W12-04 mined) | ~50% | the actual distribution |
| failure-class cases (W14-04-03) | ~25% | repair the observed weaknesses |
| refusal examples | ~15% | honest "not found" behavior |
| synthetic persona queries | ~10% | coverage for thin cells |

The distribution mirrors the deployment: the W14 self-improving loop's
mined failures become training data; the refusal family is
*over-represented* relative to natural traffic because honesty is the
behavior you are teaching. The persona grid fills the thin coverage
cells — the W16-02 grid, reused.

## 5. The data-quantity question (how much is enough)

| Records | What it can teach | What it cannot |
|---|---|---|
| 50–100 | format, refusal phrasing, style | broad domain coverage |
| 200–500 | reliable format + narrow-domain competence | new knowledge |
| 1000+ | robust behavior across the distribution | actual world knowledge |

The quantity table sets the expectation: SFT teaches *format and
behavior*, not knowledge — knowledge lives in your RAG stack (the W12
lesson). The capstone's 200-record demo fine-tune teaches citation
discipline and refusal phrasing; the eval set (file 02) must not test
knowledge the model cannot have.

## 6. The data pin note (the SFT set's manifest)

```markdown
# SFT dataset (W16)
- source mix: 50% logs, 25% failure clusters, 15% refusals, 10% persona
- records: 200 (v1, changelog in the dataset dir)
- format: chat messages, masking on final assistant turn
- validation: W16-02 gates green (labels, diversity, leakage, dist)
```

The manifest is the SFT set's pin — source mix, count, format, and the
validation verdict. It is the dataset-governance page (W16 file 01-04)
applied to training data.

## Exercises

1. Build the SFT dataset from your corpus QA logs (the 15-case pattern,
   scaled); 200 records minimum for a demo fine-tune.
2. Distribution drill: compute the source shares; adjust to the §3
   table; record the mix in the dataset's changelog.
3. Format drill: one record whose assistant turn lacks a citation; the
   fine-tune will learn to drop citations — the format rule, proven by
   its violation.
4. Pin drill: write the manifest; the validation command green as
   recorded.

## 7. The SFT-vs-RAG fork (the decision above the decision)

| Symptom | Fix |
|---|---|
| the model doesn't know facts | RAG (your stack) — SFT cannot add knowledge |
| the model knows but formats badly | SFT — format and style |
| the model refuses when it shouldn't | SFT on refusal examples |
| the model is slow/expensive | distillation (advanced SFT) |

The fork is the SFT decision's first question: *is the failure a
knowledge failure or a behavior failure?* Knowledge failures route to
the retrieval stack (W12); behavior failures route here. A fine-tune
attempting to teach facts produces a confident, still-wrong model —
the fork prevents that week-long detour.