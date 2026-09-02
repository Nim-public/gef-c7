# 03 — Distillation: Frontier Capability in SLM Packaging

> E1 index: [README.md](README.md)

**Core topic:** *Distillation — compressing a large (teacher) model's behavior into a small (student) model.*

---

## What you'll learn

- The distillation taxonomy: logit distillation vs sequence-level (data) distillation vs on-policy distillation
- The recipe: teacher data generation → filtering → student SFT (everything you know, composed)
- What distillation *doesn't* transfer, and the measurement for each gap
- The capstone decision: which of your agent paths deserves a distilled student

## 1. The taxonomy

| Approach | Teacher signal | Student trains on | Example |
|---|---|---|---|
| **Logit/KL distillation** | teacher's full next-token distribution | KL(teacher ‖ student) per token | classic KD; needs teacher logits (white-box) |
| **Sequence-level (data) distillation** | teacher's *outputs* | SFT on teacher-generated (prompt → response) pairs | most open small models (W12-05's "honest description") |
| **On-policy distillation** | teacher scores/edits *student-generated* rollouts | student learns on its own trajectories | GPT-5-class distillation recipes; the modern best |
| **Feature distillation** | intermediate hidden states | alignment losses | research |

For practitioners with API teachers (black-box): **sequence-level is your tool**, on-policy is the upgrade when you can score rollouts. The math-lite version: sequence-level KD = SFT (file 16-03) where the training data is *teacher-written* instead of human-written — everything you know about SFT data quality applies with double force.

## 2. The recipe (sequence-level, end to end)

### Step 1 — task decomposition and teacher data generation

```python
DISTILL_PROMPT = """You are the gold-standard capstone assistant. Answer with:
- a direct answer first
- reasoning only if the question needs it
- citations as [doc:id] when the context block supports it
- "I don't have that information." when the context is insufficient

Context: {context}
Question: {question}"""

# 300–2000 diverse questions (W16-02's synthetic expansion over real seeds)
responses = [teacher(DISTILL_PROMPT.format(context=c, question=q)) for q, c in tasks]
```

### Step 2 — filter (the step everyone skips)

Every row passes the W5-04/W12-04 gates *before* training:

- citation ids resolve to real chunks
- numbers present in tool/context rows (`numbers_supported`)
- JSON/contracts parse
- length/format constraints hold
- **dedup** (W16-02 §3) + held-out split discipline

Expect to drop 10–30% of teacher output. Bad rows in = student learns the teacher's hallucinations *concentrated*.

### Step 3 — student SFT (file 16-03 unchanged)

```python
# LoRA on Qwen2.5-0.5B-Instruct, 1–3 epochs on the filtered pairs
# (file 16-04's exact recipe; LR 2e-4, r=16)
```

### Step 4 — parity + gap eval

| Check | Tool |
|---|---|
| task success (vs teacher on held-out) | your eval harness |
| general capability parity | W11-05 battery |
| grounding | citations resolve; `numbers_supported` |
| refusal/insufficiency behavior | the 5-question battery |
| cost/latency | W15-05 table |

## 3. What distillation doesn't transfer (the honest list)

1. **Novel reasoning depth** — the student imitates *outputs*, not the teacher's search; hard multi-step questions degrade first
2. **Robustness tail** — teacher handles adversarial phrasings the student never saw; synthetic coverage helps but never closes it
3. **Up-to-date knowledge** — teacher knowledge is frozen at *its* cutoff, then the student's at distillation date
4. **Calibration** — student confidence ≠ teacher confidence; re-verify logprob-based routing (W15-04) after distillation
5. **Tool-use judgment** — if teacher trajectories used tools, the student needs those trajectories *in the data* (on-policy distillation territory)

## 4. On-policy distillation (the upgrade)

Sequence-level KD trains the student on the *teacher's* outputs — the student never learns from its own mistakes. On-policy fixes that: the **student generates**, the teacher (or a judge/RM, W17-02) **scores/corrects**, and the student trains on its own rollouts with teacher-quality labels. In your stack: student generates → your citation/grounding validators score → failures get teacher rewrites → the corrected pairs feed SFT. Loop weekly; the eval harness (W16-01) gates each iteration.

## 5. The capstone decision

| Path | Cost | When |
|---|---|---|
| Keep API frontier for everything | $ per query, no training | volume low, quality maximal |
| Distill the top-3 question classes into a 0.5B student (W15-04 routing) | 1–2 days + GPU-hours | 80% of traffic is formulaic |
| Distill the whole assistant | weeks | volume justifies + you accept the tail loss |

The measured pattern from W15-04's router: route the formulaic classes to the distilled student, escalate the tail — your W14-06/W15-05 tables already tell you which classes those are.

## Exercises

1. Generate 500 teacher pairs over your corpus (W16-02 Pattern A seeds); run the §2 filter; report the drop rate and the top-3 rejection reasons.
2. Distill a 0.5B student with LoRA; run the W11-05 battery + task eval. Table: teacher vs student vs base on task success, parity, cost.
3. On-policy loop v0: student answers 50 questions; your validators flag 12 failures; regenerate those with the teacher; retrain; re-eval. Measure the failure-rate delta per iteration.
4. Calibration check: student logprobs vs answer correctness on 20 cases — is the student *confidently wrong* anywhere your router trusts it?
5. Cost decision: at 1M queries/month, API vs distilled-SLM serving (W15-05's table extended with the distillation training cost amortized). Where's the break-even month?

## Pitfalls

- **Distilling the teacher's hallucinations** — unfiltered teacher data concentrates errors into the student (§2 step 2 is not optional)
- **Diversity collapse** — 500 questions all phrased one way → a student that only answers that way (W16-02's grid)
- **Comparing student to teacher on the teacher's home turf** — the teacher defined the data distribution; use *held-out, human-phrased* questions
- **Expecting reasoning transfer** — chain-of-thought distillation copies CoT *style*; depth needs scale or on-policy RL (W17-02 GRPO)
- **Serving the student without the W15 layers** — budgets/tracing/routing apply to distilled students too (they're the same deployment surface)

## Resources

- Hinton et al., *Distilling the Knowledge in a Neural Network* — the KD origin
- Agarwal et al., *GKD: Generalized Knowledge Distillation* / on-policy distillation papers — the modern framing
- HF blog, *Distillation of LLMs* + TRL distillation examples
- W16-03/04 (SFT/LoRA), W15-04 (routing), W16-02 (data generation) — composed here
