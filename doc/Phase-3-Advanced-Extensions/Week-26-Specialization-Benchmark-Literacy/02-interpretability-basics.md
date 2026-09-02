# 02 — Interpretability Basics: Opening Your Agent's Black Box

> E10 index: [README.md](README.md)

**Core topics:** *Attention inspection, probing, logit lens — practical interpretability for debugging and defending your agent.*

---

## What you'll learn

- The interpretability tiers: behavior → representations → circuits (and where practitioners live)
- Attention inspection on your own transformer (W3-04's attention, opened)
- Logit lens / probing: reading intermediate representations
- Applied interpretability: debugging your agent's routing/retrieval failures

## 1. The three tiers

| Tier | Question | Tools | Practitioner relevance |
|---|---|---|---|
| **Behavioral** | what does the model do? | evals, traces (W10-04) | daily |
| **Representational** | what does it *know* mid-forward? | embeddings analysis, probing, logit lens | debugging hard failures |
| **Circuits** | *which weights* cause it? | activation patching, SAEs | research |

Practitioners live in tiers 1–2: you rarely need circuits, but representational probes answer questions behavioral testing can't ("*why* does it always route Hindi tickets to the wrong arm?").

## 2. Attention inspection (your W3-04 graph, opened)

```python
from transformers import AutoTokenizer, AutoModel
import torch

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
model = AutoModel.from_pretrained("Qwen/Qwen2.5-0.5B", output_attentions=True)

text = "The refund will arrive after the warranty expires"
inputs = tok(text, return_tensors="pt")
out = model(**inputs)

attn = out.attentions[-1][0]           # last layer, (heads, seq, seq)
tokens = tok.convert_ids_to_tokens(inputs["input_ids"][0])

# what does "expires" attend to?
idx = tokens.index("Ġexpires")
weights = attn[:, idx, :].mean(0)      # mean over heads
top = torch.topk(weights, 3)
print([(tokens[i], round(float(w), 3)) for i, w in zip(top.indices, top.values)])
```

Reading attention maps on real inputs answers debugging questions: does the model attend to the *antecedent* of "it"? Does a Hebrew token attend to its translation? (W2-04's multilingual probe, mechanistic edition.) Caveat: attention ≠ explanation strictly speaking — but for localization debugging it's the fastest instrument you have.

## 3. Logit lens — reading intermediate layers

Project intermediate hidden states through the final unembedding matrix: what token *would* the model predict if forced to answer now? Early layers show generic continuations; mid layers approach the answer; late layers refine it.

```python
with torch.no_grad():
    h = out.last_hidden_state                          # final layer, per token
    logits = h @ model.lm_head.weight.T                # the "lens" applied at the last layer
    top = torch.topk(logits[0, -1], 5)
    print([(tok.decode([i]), round(float(v), 2)) for v, i in zip(top.values, top.indices)])
```

Applying the same projection at *earlier* layers (the true logit lens / tuned-lens variants) shows when during the depth the answer "crystallizes" — useful for diagnosing why a model is confidently wrong at step N of a reasoning chain.

## 4. Probing your agent's decisions (the applied tier)

Behavioral interpretability on your stack — the probes you can run this week:

| Question | Probe |
|---|---|
| Why did routing pick SQL? | classifier inputs + confidence (W6-04/W2-02's route log) |
| Which chunk drove the answer? | reranker scores + citation validation (W5-03/04) |
| What does the embedder think is similar? | nearest neighbors with labels (W17-04's lab) |
| Is the RAG context attended *equally*? | attention over context blocks (this file's §2 on the generation call) |
| Where does the reasoning go wrong? | logit lens per step (§3) |

Each probe turns a "the model is bad" into "the model attends to the wrong span / the router's confidence is uncalibrated / the reranker prefers long chunks" — which is a *fixable* statement.

## Exercises

1. Attention map: render (matplotlib heatmap) last-layer attention for "The animal didn't cross the street because it was too tired" — find what "it" attends to across heads. W8-01 exercise 4's prediction, verified.
2. Logit lens trajectory: apply the lens at layers {25%, 50%, 75%, 100%} depth on a math question — at which depth does the correct answer first appear in top-5?
3. Routing probe: 20 misrouted tickets (W13-03) — inspect the classifier's inputs/logprobs; classify the failure (input ambiguity vs classifier limits).
4. RAG attention probe: does the generation model attend to the *cited* chunk more than non-cited ones? (Measure attention mass per context block; verify the citation contract mechanically.)
5. Interpretability report: pick one agent failure; use ≥2 probes to produce a *mechanistic* explanation ("the router's Hindi embeddings cluster with technical tickets because…") — and the fix that follows.

## Pitfalls

- **Attention = explanation (overclaimed)** — attention is *a* signal, not causal proof; pair with behavioral counter-evidence
- **Interpreting single heads** — heads specialize unpredictably; aggregate but verify against behavior
- **Probing on the training distribution** — probes that pass in-domain say nothing about the failure case; probe *the failure*
- **Logit lens without the final norm** — intermediate states need the final LayerNorm applied (tuned-lens handles this); naive projection misleads
- **Interpretability as a replacement for evals** — it explains failures; evals (W16-01) find them. Both, always.

## Resources

- [TransformerLens](https://github.com/TransformerLensOrg/TransformerLens) — the practitioner's interpretability library (hooked transforms)
- Elhage et al., *A Mathematical Framework for Transformer Circuits* — the circuits vocabulary (tier 3, skim)
- Belinkov, *Probing Classifiers* survey — what probes can/can't establish
- logit-lens / tuned-lens repos — the §3 implementations
