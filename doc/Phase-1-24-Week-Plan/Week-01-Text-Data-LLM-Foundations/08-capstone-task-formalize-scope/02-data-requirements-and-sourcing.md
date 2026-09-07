# 08.2 — Data Requirements & Sourcing

> Subfolder index: [README.md](README.md) · Parent: [../08-capstone-task-formalize-scope.md](../08-capstone-task-formalize-scope.md)

---

## What you'll learn

- The data-requirements table, completed with *decided* values (not descriptions)
- Volume modeling: how much data each pipeline stage actually needs
- Licensing and PII as selection filters, not afterthoughts
- The sourcing decision: own vs public vs synthetic (W16-02's patterns, scoped)

## 1. The requirements table, decided

| Item | Value (decided) | Basis |
|---|---|---|
| Sources | Portal ticket export (CSV) + handbook PDFs (6) + resolved-ticket archive (JSONL) | access confirmed 2026-11-18 |
| Volume | 400 tickets, 60 handbook pages, 1,200 resolved tickets | counted, not estimated |
| PII | emails, names, phones in ticket bodies | scrubbing required (W2-02) before any indexing |
| Labels | triage labels exist on 100% of resolved tickets | free supervision for the baseline |
| Licensing | internal — no redistribution; demo with masked data | legal check done 2026-11-19 |
| Eval split | 60 train / 20 test / 20 unanswerable | W16-01's versioned set |

Every row is a **decision with a basis** — the difference between a requirements table and a hope list. "Volume: counted, not estimated" is the single most credibility-building phrase in a scope doc.

## 2. Volume modeling (how much is enough)

Per pipeline stage, the real minimums:

| Stage | Minimum | Why |
|---|---|---|
| retrieval corpus | whatever the domain needs | breadth, not count — 60 good pages beat 600 bad ones |
| classification baseline | 30+ per class | stable per-class metrics (W1-05) |
| Ragas eval set | 20–30 + slices | stable scores need n (W5-05) |
| fine-tuning (if ever) | 500–5k verified rows | W16-03 — and only after RAG plateaus |

Model the volume *per stage* against your actual traffic: "400 tickets/week → 18k/year" tells you whether the corpus grows fast enough for RAG to keep improving without new sources.

## 3. Licensing and PII as selection filters

```
source → {license compatible?} → {PII classifiable?} → {scrub feasible?} → INCLUDE
```

| Check | Tool | Failure action |
|---|---|---|
| license | model/dataset card (W2-01) | exclude or get written permission |
| PII detection | W2-02 NER + W1-02 regex | scrub, mask, or exclude |
| re-distribution | terms of the source | demo on masked data only |

The PII decision is per-*field*, not per-source: a ticket body with a customer email is usable if the email is masked and the mask is logged (W5-04's trip log). Document the field-level policy in the scope's PII row.

## 4. Sourcing decision: own vs public vs synthetic

| Source | Use | Risk |
|---|---|---|
| **Own/organizational** | primary corpus — the differentiator | access approvals, PII |
| **Public datasets** (HF/Kaggle) | augmentation, eval calibration | domain mismatch, license |
| **Crawled** | public docs | ToS, quality, freshness (W1-04) |
| **Synthetic** (W16-02) | eval expansion, adversarial cases | label inheritance, distribution skew |
| **LLM-generated knowledge** | never for facts | hallucination becomes ground truth |

The rule from the program FAQ holds: own data is the differentiator; public data fills gaps; synthetic only where labeled truth exists or for adversarial coverage.

## Exercises

1. Complete the §1 table for your project — every row with a basis (date, count, or document link). No "TBD" allowed.
2. PII field-census: take 20 real-ish records; classify every field (none/low/medium/high sensitivity); write the per-field handling row (mask/encrypt/exclude).
3. Volume model: traffic → per-stage minimums (§2) → is your data enough for each stage? Write the gap-closing plan per gap.
4. Licensing memo: for each public source you use, record the license, the attribution requirement, and the redistribution right — one row each.
5. Synthetic boundary: list the eval cases you'd synthesize (W16-02) and prove each has a verifiable ground truth (citation, number, or label you control).

## Pitfalls

- **"We'll anonymize later"** — later never comes; scrub at ingestion (W5-04's intake layer)
- **Volume counted in documents, needed in *answers*** — 400 tickets ≠ 400 eval questions; label coverage per class is what counts
- **Public data silently reshaped** — license terms can prohibit derivative datasets; check before fine-tuning on scraped corpora
- **Eval set contaminated by training choices** — W16-02's leakage check before splitting
- **PII in derived artifacts** — masked source but unmasked eval exports; audit every output artifact (W5-04's trip log)

## Resources

- W1-08 parent (template), W16-02 (synthetic), W2-01 (licensing discipline) — composed here
- HF [dataset licenses](https://huggingface.co/docs/hub/datasets-cards) · Kaggle [terms](https://www.kaggle.com/terms) — the checks
- W1-02/04 (scrubbing and crawling tools) — the enforcement layer
