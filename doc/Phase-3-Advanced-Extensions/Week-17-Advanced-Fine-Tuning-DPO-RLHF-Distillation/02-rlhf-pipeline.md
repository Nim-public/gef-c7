# 02 — The RLHF Pipeline: Reward Models, PPO, GRPO

> E1 index: [README.md](README.md)

**Core topic:** *The full RLHF pipeline — reward modeling, PPO, and the newer GRPO — and when DPO replaces it.*

---

## What you'll learn

- The complete RLHF pipeline stages and what each contributes
- Reward model training: data, loss, and how to read reward-model scores
- PPO's mechanics and why it's hard to run; GRPO's simplification
- A decision table: DPO vs PPO/GRPO for your use case

## 1. The pipeline (recap + depth)

```
SFT model ─► collect preference pairs ─► train Reward Model (RM)
                                              │
SFT model ─► PPO/GRPO optimize policy ────────┘ (reward signal)
              + KL penalty vs reference
```

Each stage's output is the next stage's input; the RM translates human preferences into a dense signal the policy can gradient-descend against. DPO (file 01) collapses the RM+RL into one loss; the full pipeline remains the state of the art for *maximal* alignment quality at scale (it's what frontier labs run, with real humans in the loop).

## 2. Reward model training

The RM is a transformer with a scalar head, trained on pairwise comparisons:

```python
from trl import RewardTrainer, RewardConfig
from datasets import load_dataset

ds = load_dataset("json", data_files="data/preferences.jsonl", split="train")

rm = RewardTrainer(
    model="Qwen/Qwen2.5-0.5B-Instruct",
    args=RewardConfig(output_dir="out/rm-v1", per_device_train_batch_size=4,
                      learning_rate=1e-5, num_train_epochs=1),
    train_dataset=ds,          # same prompt/chosen/rejected format
)
rm.train()
```

The loss is the pairwise Bradley–Terry form: `-log σ(r(chosen) − r(rejected))` — the RM learns to *score*, not to generate. What RM scores are good for even if you never run PPO:

- **Offline evaluation** of candidate answers without an LLM judge (fast, deterministic)
- **Best-of-N reranking** at inference: generate N, ship the highest RM score (a real production pattern, cheaper than DPO at the margin)
- **Data filtering**: score your SFT/distillation data before training on it

RM failure modes: score hacking (long answers score higher), out-of-distribution silence (scores meaningless off-distribution) — validate RM vs your golden labels (W16-01 §3).

## 3. PPO — the loop, mechanically

PPO optimizes the policy against the RM with four models in memory (policy, reference, reward, value) and a rollouts loop:

```
for batch:
    1. rollouts: sample K responses per prompt from the policy
    2. score each with the RM
    3. compute advantages (value model baseline)
    4. PPO clipped update on the policy
    5. KL penalty each token vs the reference model (stay close to SFT)
```

Why it's hard: four large models, the RL hyperparameter surface (clip range, GAE λ, KL coefficient), reward hacking pressure (the policy finds RM blind spots), and instability — the reason DPO's one-loss simplicity won adoption for everything below frontier scale. When you *do* need it: online learning from new interactions, complex multi-objective rewards (tool success + cost + safety), settings where you can't enumerate pairs.

## 4. GRPO — group relative policy optimization

DeepSeek's simplification (behind R1-style reasoning models): drop the value model; for each prompt sample a **group** of G responses, and use the *group's* reward statistics as the baseline:

```
advantage_i = (r_i − mean(r_1..r_G)) / std(r_1..r_G)
```

Same objective family as PPO, one fewer model, and it shines exactly where reasoning models live: **verifiable rewards** (unit tests pass, math checks out) computed per group. This is the loop behind R1-style "reasoning + RL" training — verifiable tasks get reward = task success, no human preference data needed.

| Method | Models in memory | Data | Use when |
|---|---|---|---|
| SFT | 1 (+LoRA) | demonstrations | format/style/knowledge (W16-03) |
| **DPO** | policy + ref (LoRA: ~1) | preference pairs | default alignment below frontier scale |
| KTO | policy + ref | unpaired good/bad | only thumbs data |
| **PPO** | 4 | prompts + RM | online/complex objectives, max quality |
| **GRPO** | 2–3 | prompts + *verifiable* rewards | reasoning tasks with checkable answers |

## 5. The alignment-data flywheel (production view)

The pipeline is a loop, not a line:

```
deploy ─► logs (W10-04) ─► failures + preferences ─► new pairs
   ▲                                                        │
   └──────── DPO/GRPO update ── eval gate (W16-01) ◄────────┘
```

Every production week of your capstone generates alignment data for free: user 👍/👎, judge scores, tool-success rates. The W17-01 exercise's 50 pairs become 5,000 over a quarter — and the alignment model improves on *your* distribution, not a benchmark's.

## Exercises

1. Train an RM on your 50 preference pairs; score 10 held-out answers — do RM scores agree with your ordering? Compute the pairwise accuracy.
2. Best-of-N demo: generate 5 answers per question (temperature 0.8), rerank with your RM vs an LLM judge — agreement rate?
3. PPO-on-paper: write the PPO update for one token given (reward=1, old policy prob 0.3, new 0.35, clip 0.2) — which term clips?
4. GRPO drill: write a verifiable-reward function for "output valid JSON with keys a,b" (parse + key check) and score 4 sampled completions — compute the group advantages by hand.
5. Decision memo: DPO vs PPO vs GRPO for (a) tone alignment, (b) JSON schema adherence, (c) multi-step task success — one paragraph each, with the data requirement stated.

## Pitfalls

- **RM score drift** — RM scores are only comparable *within* its training distribution; new domains need new pairs
- **Reward hacking in PPO** — length/style exploits the RM; KL penalty + RM ensembles are the mitigations
- **GRPO without verifiable rewards** — if rewards are LLM-judged, you've rebuilt RM bias into the group baseline
- **Skipping the eval gate** — alignment updates ship only through the W16-01 versioned eval (non-negotiable)
- **Confusing DPO's β with PPO's KL coefficient** — same spirit, different math; don't port intuition directly

## Resources

- Ouyang et al., *InstructGPT* (W1-07) — the canonical pipeline
- Rafailov et al., *DPO* — the closed form (file 01)
- DeepSeekMath / DeepSeek-R1 papers — GRPO's origin and verifiable-reward training
- HF [Alignment Handbook](https://github.com/huggingface/huggingface_alignment_handbook) — end-to-end recipes (SFT→DPO) you can run
- TRL [RewardTrainer docs](https://huggingface.co/docs/trl/reward_trainer)
