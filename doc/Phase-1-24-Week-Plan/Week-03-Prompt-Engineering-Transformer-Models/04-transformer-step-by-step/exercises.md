# Exercises — Transformer Step-by-Step

> Subfolder index: [README.md](README.md) · Parent: [../04-transformer-step-by-step.md](../04-transformer-step-by-step.md)

Labs for this subfolder. Shared fixture: the 4-token toy from file 01 and Qwen2.5-0.5B.

---

## E1 — Attention by hand (file 01)

1. Compute all 16 scores and the full softmax matrix on paper; verify against NumPy to 1e-6.
2. The √d derivation: with unnormalized 3-d vectors, show scores grow linearly with d; with d=512, show the softmax entropy collapse.
3. The permutation test: swap tokens 1 and 2 in `x` without positional encoding — show the attention output permutes identically (order-blindness).

**Worked approach:** exercise 3's result is the *proof* that position embeddings are load-bearing — the same math without them can't distinguish "dog bites man" from "man bites dog".

## E2 — The attention function (file 02)

1. Mask verification: with the causal mask, print the full weight matrix; assert the upper triangle is exactly 0.
2. The scaling ablation: remove √d_k on 64-dim heads; measure softmax entropy per row before/after — the saturation visible.
3. Multi-head count sweep: heads ∈ {1, 2, 4, 8} at fixed width — quality vs heads on a small copy task; find the knee.

**Worked approach:** exercise 2's entropy collapse is the numerical signature of the vanishing-gradient problem (file 03-03) — the two lessons connect mechanistically.

## E3 — The block (file 03)

1. Parameter census per component: embeddings, per-block attention, FFN, head — reconciled totals for MiniGPT and Qwen-0.5B.
2. Residual ablation: 2 vs 4 blocks with/without residuals on the sin task — the deep-stack stability difference.
3. Pre-vs-post norm: implement both; train 6 blocks — the stability difference at depth.
4. FFN-capacity probe: d_ff ∈ {1×, 2×, 4×} d_model — quality vs parameters; the knee located.

**Worked approach:** exercise 3's pre/post-norm result explains why every modern model is pre-norm — the difference is visible in a 6-block toy.

## E4 — Real-model tracing (file 04)

1. Full parameter reconciliation for Qwen2.5-0.5B from the architecture print — within 1% of ~494M.
2. The logit-lens trajectory: hidden states 5/10/15/20/24 through `lm_head` on "The capital of France is" — when does "Paris" crystallize?
3. The next-token probe: 10 prefixes; top-5 next-token predictions at each — the model's live distribution, inspected.
4. Attention archaeology: find the head/layer where coreference routing appears on the animal sentence (W13's probe, deeper).

**Worked approach:** exercise 2's logit lens is the interpretability gateway (E10-02) — the answer forming across depth is the model's "thinking" made visible.

## Self-assessment

- Can you compute attention by hand for a 4-token sequence — scores, softmax, and output — in under 5 minutes?
- Can you reconcile a real model's parameter count from its config alone?
- Can you state, for each transformer component (embed, attention, FFN, norm, head), its role in one sentence?
