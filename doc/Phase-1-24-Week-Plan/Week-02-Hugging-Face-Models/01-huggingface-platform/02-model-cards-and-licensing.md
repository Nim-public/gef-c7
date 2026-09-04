# 01.2 — Model Cards & Licensing

> Subfolder index: [README.md](README.md) · Parent: [../01-huggingface-platform.md](../01-huggingface-platform.md)

---

## What you'll learn

- The model-card sections as a six-question audit
- License classes decoded — what each permits for study, product, and redistribution
- Gated models: what accepting terms binds you to
- Dataset cards: the same discipline for data

## 1. The six-question card audit

| # | Question | Where on the card |
|---|---|---|
| 1 | Can I use this commercially? | License badge + license link |
| 2 | What was it trained on? | Training data / dataset sections |
| 3 | How big / fast is it? | Model config + Files tab |
| 4 | What will it fail at? | Limitations / Bias sections |
| 5 | How was it evaluated? | Metrics + eval harness description |
| 6 | Who maintains it, how actively? | Commits, discussions, org page |

The audit applied to `distilbert-base-uncased-finetuned-sst-2-english`: Apache-2.0 (commercial OK); SST-2 movie reviews (your support tickets are out of domain — plan your own eval); 66M params (CPU-friendly); limitations state short-text bias; eval is SST-2 F1 91% (not your F1); distilbert team, stable. Conclusion: usable baseline, needs domain eval — exactly the W2-06 protocol.

## 2. License classes decoded

| License | Commercial | Modification | Redistribution | Notes |
|---|---|---|---|---|
| **Apache-2.0** | ✅ | ✅ | ✅ | the open-work default; patent grant included |
| **MIT** | ✅ | ✅ | ✅ | minimal, permissive |
| **CC-BY-4.0** | ✅ | ✅ | ✅ | attribution required |
| **CC-BY-NC-4.0** | ❌ | ✅ research only | ✅ non-commercial | common on datasets — check before training |
| **Llama Community** | conditional | ✅ | ✅ <700M MAU | named user thresholds, branding terms |
| **Gemma** | conditional | ✅ | ✅ with terms | gated acceptance binds your org |
| **Custom/research-only** | read carefully | varies | varies | assume ❌ for products |

Decision rule for the capstone: **Apache-2.0/MIT for anything you might ship; research-only only for learning artifacts you won't deploy.** The license is checked at shortlist time (W2-06 §3), not at deployment time.

## 3. Gated models — what acceptance binds you to

Accepting a gated model's terms (Gemma, Llama) typically means: your HF account is bound to the license, your *organization* may be liable for member use, and usage reporting may apply. Concretely: `huggingface-cli login` with the accepting account, then downloads work — for that account. Team members each need their own acceptance.

Practical consequences:

- CI systems need a token with accepted-terms access (a bot account with its own acceptance where terms permit)
- Private mirrors of gated weights inside your org need explicit license review — most terms prohibit re-sharing
- The gate is enforced per-revision, not per-download — historical revisions remain accessible after acceptance

## 4. Dataset cards — the same discipline for data

| Field | Question |
|---|---|
| Splits | train/validation/test defined? sizes? |
| Features | schema, label classes, languages |
| Source | where the data came from, collection method |
| License | usage rights for training *and* redistribution |
| Personal info | PII statement (LLM06 awareness, E7-01) |

The viewer on the Hub shows all of it before download — inspect 10 rows before you `load_dataset` (W2-01's rule).

## Exercises

1. Card audit ×3: run the six-question audit on 3 candidate models for your capstone task; produce the evidence table.
2. License mapping: find one model each under Apache-2.0, CC-BY-NC, and a custom license; write the usage verdict for (a) study, (b) internal product, (c) public demo.
3. Gated flow: request access to a gated model (e.g., Gemma); document the acceptance flow and what changed in your account.
4. Dataset card audit: for your chosen dataset, fill the four dataset-card questions; flag any missing field as a risk.
5. License chain: if you fine-tune a CC-BY-NC model (W17-04), what license applies to the adapter? Research the base-model terms and write the verdict.

## Pitfalls

- **License read at deploy time, not selection time** — a CC-BY-NC discovery at week 20 is a re-architecture (W2-06's rule)
- **"Open weights" ≠ open license** — several famous models have restrictive terms; the badge is the truth, not the name
- **Dataset licenses inherited by derived work** — fine-tuning on CC-BY-NC data can taint downstream artifacts
- **Gated access shared across a team** — tokens must be per-person where terms require; audit who accepted what
- **Ignoring dataset PII statements** — LLM02 exposure starts at the dataset layer, not the model layer

## Resources

- HF [model cards](https://huggingface.co/docs/hub/model-cards) & [dataset cards](https://huggingface.co/docs/hub/datasets-cards) — the standard templates
- [Choose a license](https://choosealicense.com/) — the permissive-license primer
- HF [gated repos](https://huggingface.co/docs/hub/en/models-gated) — the acceptance mechanism
- W2-01 parent, W2-06 (the protocol), W17-04 (fine-tuning license chain) — composed here
