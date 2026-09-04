# 06.3 — Representations & Attention Intuition

> Subfolder index: [README.md](README.md) · Parent: [../06-from-neural-networks-to-llms.md](../06-from-neural-networks-to-llms.md)

---

## What you'll learn

- Embeddings as *learned* geometry — measured, not asserted
- Attention as learned routing — verified on real inputs
- The interpretation discipline: what probes can and cannot establish (W10-02's caveat, mechanistic edition)

## 1. Embeddings as learned geometry

```python
from transformers import AutoTokenizer, AutoModel
import torch

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
model = AutoModel.from_pretrained("Qwen/Qwen2.5-0.5B")

def embed(text: str) -> torch.Tensor:
    out = model(**tok(text, return_tensors="pt")).last_hidden_state
    return out.mean(1)[0]                          # mean-pool over tokens

pairs = [("king", "queen"), ("king", "banana"), ("bank", "river"), ("bank", "money")]
for a, b in pairs:
    ea, eb = embed(a), embed(b)
    cos = torch.nn.functional.cosine_similarity(ea, eb, dim=0)
    print(f"{a:8} vs {b:8}: {cos:.3f}")
```

Contextual embeddings (W1-01) mean `"bank"` embeds differently in "river bank" vs "bank account" — verify:

```python
print(embed("river bank").shape, embed("bank account").shape)
cos = torch.nn.functional.cosine_similarity(embed("river bank"), embed("bank account"), dim=0)
# compare against the same word in matched contexts
```

## 2. Attention as learned routing

Turn on attention output and inspect where a token looks:

```python
out = model(**tok("The animal didn't cross the street because it was too tired",
                  return_tensors="pt"), output_attentions=True)
attn = out.attentions[-1][0]                       # (heads, seq, seq)
tokens = tok.convert_ids_to_tokens(tok("The animal didn't cross the street because it was too tired")["input_ids"])

pron = tokens.index("Ġtired") - 1                  # find "tired" position
head0 = attn[0, pron, :]                           # head 0's attention from that position
top = torch.topk(head0, 3)
print([(tokens[i], round(float(w), 3)) for i, w in zip(top.indices, top.values)])
```

Reading attention: for the pronoun-adjacent positions, some heads attend strongly back to `animal` — the coreference signal, learned without supervision. Caveats (file W19-01's interpretation discipline): attention is a *signal*, not proof; individual heads are noisy; aggregate and verify against behavior.

## 3. Probing: a tiny classifier on embeddings

```python
from sklearn.linear_model import LogisticRegression

X = torch.stack([embed(t) for t in train_texts]).detach().numpy()
probe = LogisticRegression().fit(X, train_labels)
print(probe.score(X_test, y_test))      # linear probe accuracy on frozen embeddings
```

A linear probe on frozen embeddings measures *how much task information the representation already contains* — the difference between "the embedding knows X" and "the model can express X in English" (W8-04's CLIP-vs-BLIP distinction, made rigorous).

## 4. Interpretation discipline (what probes establish)

| Probe result | You may conclude | You may NOT conclude |
|---|---|---|
| high attention from pronoun to noun | the model *uses* that position for this input | it "understands coreference" in general |
| linear probe 90% on sentiment | sentiment info is *linearly present* | the model "feels" sentiment |
| attention shifts after fine-tuning | fine-tuning changed routing | it changed for the right reason |

Pair every probe with a behavioral test (W10-04) — the mechanistic claim and the behavioral claim must agree, or the interpretation is wrong.

## Exercises

1. Contextual proof: embed `"bank"` in 5 different sentences; compute pairwise cosines — verify same-sense pairs score higher (W8-01's contextual claim, verified).
2. Attention maps: render (matplotlib heatmap) layers {25%, 50%, 75%, 100%} for the animal sentence — at which depth does coreference routing appear?
3. Probe the router: linear probe on W14's router classifier inputs (or its embeddings) — how separable are the four route classes? Compare with the route accuracy.
4. Bias probe: embeddings of professions ("nurse", "engineer") vs gender words — measure association asymmetries in your chosen model; document as a model-card style note.
5. Write one interpretability report (E10-02's format): a failure of your agent explained with ≥2 probes (attention + linear probe) plus the behavioral confirmation.

## Pitfalls

- **Mean-pooling vs CLS vs last-token** — different pooling gives different embedding semantics; know your model's convention before comparing
- **Attention weights renormalized by softmax per head** — raw weights ≠ probabilities across heads; don't sum across heads naively
- **Probing on tiny data** — 20 examples probe nothing; ≥200 for a stable linear probe
- **Attributing capability to attention patterns** — attention shows *correlation with inputs*, not causation; intervention experiments (activation patching) establish cause
- **Ignoring tokenization in inspection** — `"Ġtired"` includes the space marker; map subword pieces carefully

## Resources

- [TransformerLens](https://github.com/TransformerLensOrg/TransformerLens) — hooked models for attention/probing experiments
- Elhage et al., *A Mathematical Framework for Transformer Circuits* — the rigorous vocabulary (tier 3, E10-02)
- W8-01 (encoders), W3-04 (attention by hand), W10-02 (probing caveat) — composed here
