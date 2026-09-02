# 04 — Practice: Constrained-Decoding Lab

> E6 index: [README.md](README.md) · **Due: before E7**

*(Practice lab — measures the guarantee: grammar-constrained vs free decoding across speed, validity, and quality, on your own tasks.)*

---

## 1. Deliverable

```
decoding-lab/
  lab.py                 # the experiments below (free vs retry vs grammar)
  grammars/
    schemas.py           # Pydantic schemas: triage, extraction, routing (W13/W14 reuse)
  eval/
    results.md           # the tables + verdict
  README.md              # where constrained decoding enters your capstone
```

Demo: one extraction task shown three ways — free decoding with retry, API structured output, grammar-constrained — same prompt, side-by-side outputs and failure counts.

## 2. Experiments

### A. Validity guarantee (file 02 §1)
20 tasks × 3 modes (free+parse, free+retry×3, grammar) → parse-failure rate per mode. Expect: free >0%, retry ≈ small%, grammar = 0. Table it.

### B. Speed (file 01)
Tokens/s for free vs constrained (0.5B local model, 200-token outputs) — the masking overhead, measured.

### C. Content quality (file 02 §4)
The guaranteed outputs still need verification: run the W12-04 `numbers_supported` / citation checks on 20 grammar-guaranteed outputs. Flag rate = the content-risk you still own.

### D. Enum drift (file 02 ex. 2)
Rename a category in the schema; rerun old prompts. Grammar mode: compile error at build (schema is source of truth) — vs prompt mode: silent misclassification.

### E. Speculative + grammar (files 01+02 combined, GPU)
Speculative decoding *with* grammar constraints — speedup maintained? Acceptance rate under masking? (The frontier combination — measure it.)

## 3. Rubric

| Area | Weight |
|---|---|
| Validity experiment rigor (20+ tasks, 3 modes, honest failure counts) | 30% |
| Speed measurement (proper freeze rules, W15-03) | 20% |
| Content-quality verification kept in the loop | 20% |
| GGUF quant table (file 03 ex. 1) | 15% |
| README capstone integration plan | 15% |

## 4. README sections (answer explicitly)

1. **Guarantee map**: which capstone outputs become grammar-constrained (tool args? classification nodes? extraction contracts?) — list with schemas
2. **Retry/fallback deletion**: which W14-01 retry loops become unnecessary — and which content checks stay
3. **Serving matrix** (file 03 ex. 5): model × quant × engine per environment
4. **Speculative verdict** (if GPU): adopt/skip per traffic class, with the acceptance-rate evidence
5. **E7 bridge**: your security posture (W3-02/W5-04 layers) — which attacks would grammar-constrained outputs *neutralize* (none — why?) and which *new* surface does guaranteed-JSON create? (One paragraph: guaranteed parseable output that's wrong is a *faster* path to confident wrong answers.)

## 5. Stretch (pick one)

- GBNF hand-written grammar for a complex output (W14-04's report format) — compare maintainability vs Pydantic-schema approach
- vLLM guided decoding server benchmark (file 02 §2's serving tier): constrained throughput on 7B
- Speculative decoding acceptance-rate profiler: log per-position acceptance for 100 generations — which positions reject most (structure transitions? numbers?)

Bring the lab results to your next mentor session: "guaranteed structure with verified content" is the production-grade answer to the structured-output question — the lab is the evidence.
