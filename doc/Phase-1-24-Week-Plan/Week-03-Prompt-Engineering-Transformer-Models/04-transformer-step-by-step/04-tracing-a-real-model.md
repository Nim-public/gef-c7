# 04.4 — Tracing a Real Model

> Subfolder index: [README.md](README.md) · Parent: [../04-transformer-step-by-step.md](../04-transformer-step-by-step.md)

---

## What you'll learn

- Reading Qwen2.5-0.5B's architecture print: every component mapped
- Reconciling the parameter count with the block math
- Probing the model's internals: embeddings, attention, logits

## 1. The architecture print

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")
print(model)
```

Reading the print (annotated):

```text
Qwen2ForCausalLM(
  (model): Qwen2Model(
    (embed_tokens): Embedding(151936, 896)          ← vocab × d_model (136M params!)
    (layers): ModuleList(24 × Qwen2DecoderLayer)    ← 24 blocks
      each: attn(k,q,v,o) + mlp(gate,up,down) + 2×LayerNorm
    (norm): RMSNorm(896)
  )
  (lm_head): Linear(896, 151936, bias=False)        ← the output projection (136M, TIED)
)
```

Three reconciliations to perform:

| Component | Math | Params |
|---|---|---|
| embeddings | 151,936 × 896 | 136.1M |
| per block | attn(4×896×896) + mlp(896×4864×2 + 4864×896) ≈ 14.9M | ×24 ≈ 358M |
| final norm + head | tied to embed | 0 (tied) |
| **total** | | **~494M** ✓ |

The embedding table is the surprise: 136M params — 27% of the model — just for the token lookup. The tied lm_head shares it (transposed), which is why vocab-heavy models "waste" so many parameters (file 01 §4's counting formula, now at scale).

## 2. Probing the internals

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
inputs = tok("The capital of France is", return_tensors="pt")

out = model(**inputs, output_attentions=True, output_hidden_states=True)
print(len(out.hidden_states))          # 25 = embeddings + 24 blocks
print(out.hidden_states[0].shape)      # (1, 6, 896)
print(len(out.attentions))             # 24 — one per block
print(out.attentions[0][0].shape)      # (1, 12, 6, 6) — 12 heads × 6×6

logits = out.logits
next_id = logits[0, -1].argmax()
print(repr(tok.decode([next_id])))     # the model's next-token guess
```

The layer-by-layer hidden states are the logit-lens probe (E10-02): apply `lm_head` to hidden state k and see when the answer "crystallizes" across depth.

## 3. The forward pass, traced

```python
with torch.no_grad():
    out = model(**inputs)
probs = out.logits[0, -1].softmax(-1)
top = torch.topk(probs, 5)
for p, i in zip(top.values, top.indices):
    print(f"{tok.decode([i])!r:12} {p:.3f}")
# ' Paris' 0.61, ' the' 0.04, ... — the model's distribution over the next token
```

The trace answers the mechanical questions: which layer produced what, how attention flowed, where the distribution concentrated. Every debugging session (W11-05's traces, at the model level) starts here.

## Exercises

1. Full reconciliation: sum all parameter groups from the print; match ~494M within 1% — show your arithmetic.
2. The logit lens: apply `lm_head` to hidden states 5/10/15/20/24 on "The capital of France is" — at which depth does "Paris" take the lead?
3. Attention archaeology: for "The animal didn't cross the street because it was too tired", find the head+layer where "tired" attends most to "animal" — the coreference circuit, located.
4. The tied-weights check: verify `model.lm_head.weight` shares storage with `model.model.embed_tokens.weight` (or untied in some models — check `config.tie_word_embeddings`).
5. Tokenizer round-trip at depth: encode → decode through the full model — confirm the logits' argmax decode chain matches the tokenizer's vocabulary exactly (W1-01's ids ↔ tokens, end to end).

## Pitfalls

- **Hidden-states count off by one** — N layers produce N+1 hidden states (embeddings included); indexing errors follow
- **Logits at the wrong position** — the next-token distribution lives at the LAST position's logits; earlier positions predict earlier next-tokens
- **Tied-weight double-counting** — if lm_head shares embed weights, don't count both in the census
- **Comparing logits across positions** — each position predicts the *next* token; position i's logits are for token i+1
- **Assuming `output_attentions` is free** — it materializes attention for every layer/head; memory grows fast on long sequences

## Resources

- HF [Qwen2 architecture docs](https://huggingface.co/docs/transformers/model_doc/qwen2) — the config fields
- W3-04 (the block you built), W16-03 (training these), W8-01 (the ViT cousin) — composed here
- [Transformer math 101](https://huggingface.co/blog/stas/ml-series-day-04) — the memory/parameter formulas
