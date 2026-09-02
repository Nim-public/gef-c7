# 05 — Practice: The Alignment Lab

> E1 index: [README.md](README.md) · **Due: before E2**

*(Practice build — collects every fine-tuning artifact from the extension into one evaluated, versioned alignment pipeline.)*

---

## 1. Deliverable

```
alignment-lab/
  data/
    preferences.jsonl        # ≥50 pairs (chosen/rejected, content-parallel)
    sft_train.jsonl          # ≥200 filtered distillation rows (W16-02 Pattern D)
    retrieval_train.jsonl    # ≥500 query/positive (+hard negatives)
  dpo/
    train_dpo.py             # file 01 recipe, pinned
    adapter/                 # the DPO adapter artifact
  distill/
    student/                 # LoRA artifact from file 03
    filter_report.md         # §2 step-2 drop analysis
  retrieval/
    embedder/                # file 04 fine-tuned embedder
    reranker/                # file 04 fine-tuned reranker
  eval/
    results.md               # all parity tables + versioned eval set reference
  README.md                  # decisions, verdicts
```

Demo: one DPO'd answer vs its SFT parent on the same question (win-rate evidence), one distilled-student answer with cost delta, one retrieval query where the domain embedder finds what the base missed.

## 2. Requirements (graded)

### DPO (file 01)
- [ ] 50+ pairs, content-parallel, from real logs (sources documented)
- [ ] Training run with margin/accuracy curves; β chosen from a sweep
- [ ] Win-rate eval vs SFT parent + general-parity battery (W11-05) — no regression

### Pipeline (RLHF/RM)
- [ ] Reward model trained on the same pairs; pairwise accuracy on held-out reported
- [ ] Best-of-N reranking demo (N=5) using the RM vs an LLM judge — agreement rate

### Distillation (file 03)
- [ ] ≥200 teacher pairs generated + filtered (filter report with drop reasons)
- [ ] Student LoRA trained; task + parity tables; calibration spot-check
- [ ] Cost break-even analysis at your capstone volume (file 03 ex. 5)

### Retrieval fine-tuning (file 04)
- [ ] ≥500 pairs + hard negatives; embedder fine-tuned; bake-off table updated
- [ ] Reranker fine-tuned on 300 labels; W5-03 rerank gain measured
- [ ] Re-index plan executed (new vectors validated before switch)

### Versioning (W16-01)
- [ ] Every artifact versioned (eval set v, judge pinned, adapter revisions)
- [ ] One CHANGELOG entry mapping each score movement to its cause

## 3. Rubric

| Area | Weight |
|---|---|
| DPO training + preference eval rigor | 25% |
| Distillation pipeline + filter honesty | 20% |
| Retrieval fine-tuning + re-index discipline | 20% |
| Parity/non-regression checks everywhere | 20% |
| README verdicts + versioning | 15% |

## 4. README verdicts (answer explicitly)

1. **DPO verdict**: did preference training improve your agent's *specific* weakness (name it)? What's the alignment tax?
2. **RM utility**: is the reward model useful as an offline evaluator in your CI (W15-02), or too noisy?
3. **Distillation decision**: which question classes route to the distilled student (W15-04), and what's the measured quality floor?
4. **Retrieval fine-tuning**: keep the domain embedder/reranker? (Numbers.)
5. **Version register**: every model/adapter/dataset version in one table — the W16-01 discipline applied to training artifacts.

## 5. Stretch (pick one)

- KTO on unpaired 👍/👎 from your logs — compare against DPO on the same eval
- GRPO with a verifiable reward on a small JSON-schema task (file 02 §4's reward function) — 4-group training on a 0.5B model
- DPO on your multimodal RAG answers (W9) — preference pairs over groundedness

Bring the parity tables to your next mentor session: these are the artifacts that make the capstone's "evaluation and fine-tuning" claims concrete — and the DPO/distill decisions are exactly what the production phase will question.
