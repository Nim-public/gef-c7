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

## Exercises

1. Build the SFT dataset from your corpus QA logs (the 15-case pattern,
   scaled); 200 records minimum for a demo fine-tune.
2. Distribution drill: compute the source shares; adjust to the §3
   table; record the mix in the dataset's changelog.
3. Format drill: one record whose assistant turn lacks a citation;
   the fine-tune will learn to drop citations — the format rule, proven
   by its violation.