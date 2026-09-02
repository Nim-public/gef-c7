# 01 — Benchmark Literacy

> E10 index: [README.md](README.md)

**Core topics:** *Reading benchmark claims correctly — MMLU/arena/SWE-bench, contamination, and designing task-eval claims that survive review.*

---

## What you'll learn

- What the major benchmarks actually measure (and what they silently don't)
- Contamination, saturation, and Goodhart — the three failure lenses
- The claim→evidence discipline: matching evaluation design to the claim you make
- Your capstone's benchmark plan: which claims, which evidence

## 1. The benchmark landscape, honestly categorized

| Benchmark | Measures | Silent weaknesses |
|---|---|---|
| **MMLU / MMLU-Pro** | broad knowledge (multiple choice) | multiple-choice guessing; contamination; ≠ your domain |
| **Arena (LMSYS)** | human pairwise preference | style/length bias; crowd preferences ≠ correctness |
| **SWE-bench** | real repo issue resolution | subset-specific; scaffolding-dependent; patch ≠ production code |
| **GSM8K / MATH** | math reasoning | calculators/cot variance; contamination pressure |
| **HumanEval / LiveCodeBench** | code generation | narrow; LiveCodeBench fights contamination with fresh problems |
| **GAIA / AgentBench** | multi-step agent tasks | scaffolding-sensitive; few tasks |
| **BEIR / MTEB** (W5-02) | retrieval | benchmark ≠ your corpus |
| **DocVQA / MMMU** (W7-05) | document/vision QA | template leakage risks |

**The two universal lessons:**

1. **Contamination** — public benchmarks leak into training data; scores inflate without ability improving. The fix is *private, rotating, task-relevant* evals (your W4-05 harness, W16-01's versioning — you already run the anti-contamination playbook).
2. **Saturation** — MMLU-class benchmarks near ceiling; deltas there measure trivia, not capability. Look at *task-shaped, recent* benchmarks.

## 2. Reading a benchmark claim (the checklist)

```markdown
Claim: "Our model achieves SOTA on SWE-bench Verified (49%)."
Questions:
1. Verified vs full set? (Verified = human-validated subset — much harder, more honest)
2. What scaffolding? (Agent loop, tools, retries — the scaffold is half the score)
3. Same test-time compute as baselines? (More samples/budget = free points)
4. Contamination audit published?
5. On which languages/frameworks? (Python-heavy; your Java repo is untested)
6. What does a human reviewer say about the *merged* patches? (Tests pass ≠ good code, W13-04)
```

Every leaderboard claim decomposes into: *capability signal × scaffolding × test-time compute × contamination risk*. Your capstone claims should be auditable by the same checklist.

## 3. Claim → evidence discipline (for YOUR capstone)

| Claim you want to make | Evidence that survives review |
|---|---|
| "Our RAG answers are accurate" | Ragas faithfulness + human-verified sample, held-out slice (W16-01) |
| "Our agent completes tasks" | trajectory success rate on a *held-out, human-phrased* case set (W10-04) |
| "Our retrieval beats baseline X" | same harness, same queries, both systems (W16-05's table) |
| "Our fine-tune improved formatting" | parity + task eval, contamination-checked (W16-04) |
| "Production-ready" | W15-05 table + E7 security evidence + E8 drills |

The meta-rule from W5-02 (bake-off) and W10-04 (metrics): **task-specific, held-out, human-anchored evidence beats every leaderboard** — and it's the only kind a mentor, employer, or security reviewer accepts.

## 4. Designing your capstone's benchmark claim

```markdown
## Evaluation claim (demo-day slide)
Claim: The assistant answers domain questions with 92% grounded-accuracy
(faithfulness ≥ 0.9, all citations verified) on a 100-question held-out set
covering 4 doc types, vs 71% for the pre-RAG baseline.
Design: human-phrased questions (not from corpus), blind judge (different model family),
versioned eval set v4 (W16-01), slices by route and doc type.
Known limits: adversarial multi-hop coverage is thin (12 cases); no multilingual slice yet.
```

That paragraph is worth more than any leaderboard row — it states the claim, the evidence, and the limits (W5-05's reporting discipline, final form).

## Exercises

1. Benchmark teardown: pick 3 leaderboard rows for a model you use (any vendor page); run the §2 checklist on each claim. What survives?
2. Contamination probe: ask your model to complete a *recent* (post-training-cutoff) document verbatim — then an older one. Compare. What does this tell you about your eval design?
3. Arena bias test: generate a short-but-correct answer and a long-but-vague answer to the same question; ask an LLM judge to rank them (style bias test, W5-05's judge rules). Document the bias you find.
4. Claim upgrade: rewrite your capstone's weakest demo-day claim using §4's template (claim/design/limits).
5. Benchmark shopping audit: list the benchmarks relevant to your capstone (task, agent, retrieval, security) — then mark which you could actually run this month, and what each would cost.

## Pitfalls

- **Leaderboard worship** — MMLU tells you nothing about ticket routing (W5-02's rule, at field scale)
- **Scaffolding-blind comparison** — comparing your agent to a paper's score without accounting for scaffolding differences
- **Contaminated self-evals** — eval questions the model helped generate (W16-02's synthetic-on-synthetic trap)
- **Claiming beyond the eval** — "production-ready" from a 20-case offline run (W16-01's offline/online split)
- **Static claims** — a claim measured in November re-verified never (W16-01's versioning exists to prevent exactly this)

## Resources

- [SWE-bench](https://www.swebench.com/) · [LiveCodeBench](https://livecodebench.github.io/) · [GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) — contamination-aware benchmark design examples
- [LMSYS Chatbot Arena](https://lmarena.ai/) + its methodology paper — what preference rankings measure
- W5-02/05, W10-04, W16-01 — your eval discipline, this file's evidence base
- Papers-with-code per-task leaderboards — with the contamination caveats above attached
