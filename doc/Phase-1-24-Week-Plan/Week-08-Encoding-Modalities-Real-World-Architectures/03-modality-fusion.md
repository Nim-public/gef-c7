# 03 — Modality Fusion

> Week 8 index: [README.md](README.md)

**Session 1 topic:** *Intuitive Understanding of Modality Fusion: Fusion types — early fusion, intermediate fusion, late fusion, and hybrid fusion.*

---

## What you'll learn

- What fusion decides: *where* in the network modalities meet
- The four fusion families with runnable code sketches
- The trade table: alignment burden, missing-modality robustness, compute, interpretability
- The LLaVA-style projection pattern — how a vision encoder plugs into an LLM (the architecture behind most VLMs and Week 9's pattern 3)

## 1. Fusion = where the modalities meet

You have per-modality encoders (files 01–02). Fusion answers: at which point do their representations interact?

```
early:      fuse raw/low-level features  ─► one joint encoder
intermediate: encoders interact mid-network (cross-attention)
late:       separate encoders ─► separate predictions ─► combine
hybrid:     a designed mix of the above
```

## 2. Early fusion

Concatenate inputs (or low-level features) and process jointly:

```python
import torch, torch.nn as nn

class EarlyFusionClassifier(nn.Module):
    def __init__(self, img_dim=512, txt_dim=384, hidden=256, n_classes=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(img_dim + txt_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, n_classes))

    def forward(self, img_emb, txt_emb):
        return self.net(torch.cat([img_emb, txt_emb], dim=-1))   # fuse at the input
```

- **Pros**: simplest; lets the model learn cross-modal interactions at every layer; strong when modalities are *always* present and *aligned*
- **Cons**: brittle to missing modalities (no image → half the input is garbage); low-level fusion needs paired, synchronized data; little interpretability
- Text+image *early* fusion at the embedding level (as above) is the standard cheap baseline for classification

## 3. Intermediate fusion (cross-attention)

Modalities stay in separate streams but *interact* mid-network — one stream's queries attend to the other's keys/values:

```python
class CrossAttentionFusion(nn.Module):
    def __init__(self, d=256, heads=4):
        super().__init__()
        self.cross_attn = nn.MultiheadAttention(d, heads, batch_first=True)
        self.norm = nn.LayerNorm(d)

    def forward(self, query_mod, kv_mod):            # e.g. text queries attend to image patches
        attn_out, weights = self.cross_attn(query_mod, kv_mod, kv_mod)
        return self.norm(query_mod + attn_out), weights   # residual + attention map!
```

- **Pros**: fine-grained grounding ("which *patch* does this word refer to?" — `weights` are inspectable); partial robustness; the mechanism inside Flamingo/LLaVA/VLMs
- **Cons**: most engineering effort; needs matched semantic levels (tokens vs patches)
- The **LLaVA pattern** (know this one cold): ViT encodes the image → a small **projection layer** maps image embeddings into the LLM's token space → injected into the prompt as if they were "image tokens" → the LLM attends to them with its native attention. One linear layer turns a vision encoder into LLM context.

## 4. Late fusion

Full separation — each modality runs its own model; predictions combine:

```python
def late_fuse(img_logits, txt_logits, w_img=0.5):
    p = w_img * torch.softmax(img_logits, -1) + (1 - w_img) * torch.softmax(txt_logits, -1)
    return p.argmax(-1)
```

- **Pros**: modular (swap/upgrade one side); **graceful degradation** (image model down? text-only prediction still ships); interpretable per-stream scores; parallelizable
- **Cons**: never learns cross-modal interactions (no "the red *thing* in the image is the 'GPU' in the text"); ensembles cost double compute
- Product-level use: your Week 13/14 multi-agent designs are *late fusion at the system level* (one agent's output conditions another's)

## 5. Hybrid fusion

Real systems mix strategies: CLIP trains with deep *intermediate* interaction (contrastive across the tower outputs), then *serves* as late-fusion-style independent embeddings; LLaVA is early-style (vision tokens in the prompt) built on intermediate machinery (projection + attention); a production pipeline might early-fuse image+caption embeddings for retrieval (Week 9) and late-fuse VLM + keyword-matcher decisions for the final answer.

The design question is always: **at what level do the modalities need to know about each other?**

| Need | Fusion choice |
|---|---|
| Cheap baseline, always-aligned inputs | early (concat) |
| Fine-grained grounding, "which part of the image" | intermediate (cross-attention) |
| Robustness to missing/failing modalities | late (+ fallbacks) |
| Reuse pretrained unimodal giants | projection into LLM (LLaVA) or ensembling (late) |

## 6. Missing modality — the deployment reality

Sensors fail; users send text-only. Test every fusion choice under ablation:

```python
for missing in ("image", "text", "none"):
    pred = model(img_emb if missing != "image" else torch.zeros_like(img_emb),
                 txt_emb if missing != "text" else torch.zeros_like(txt_emb))
```

Expected ordering: late > intermediate > early for graceful degradation. If your early-fusion model collapses without one input, that's a finding — route around it (file 03 of Week 5's fallback thinking, now in vision).

## Exercises

1. Train `EarlyFusionClassifier` on synthetic embeddings (two informative dims + noise per modality). Then zero one modality at eval — how far does accuracy fall?
2. Modify `CrossAttentionFusion` to return `weights`; visualize a 4×4 attention map for a toy "text queries attend to image patches" case. Which patch wins and why?
3. Late-fusion calibration: sweep `w_img` 0→1 on a 2-stream toy problem where streams have different reliabilities. Plot accuracy vs weight.
4. The LLaVA pattern on paper: given ViT(197×768) and an LLM with d=4096, write the projection layer's shape and where its output goes in the prompt. What's the parameter cost?
5. Pick your capstone's multimodal task; write the fusion decision (§5 table) with one paragraph of justification — this feeds Week 9's architecture choice.

## Pitfalls

- **Early fusion with misaligned data** — concat assumes positional correspondence; misalignment is silent garbage
- **Cross-attention without residuals/norm** — the W3-04 stability glue is not optional here
- **Late fusion averaging probabilities from differently-calibrated models** — one model's 0.7 isn't another's; calibrate or learn the weights
- **Zero-vector "missing" imputation unmarked** — the model can't distinguish "absent" from "black image"; add a missing-flag feature
- **Overengineering fusion before baseline** — run the early-fusion baseline first; measure the delta the fancy fusion buys

## Resources

- Baltrušaitis et al., *Multimodal ML Survey* — the fusion taxonomy (early/intermediate/late is theirs)
- Liu et al., *Visual Instruction Tuning* (LLaVA) — the projection pattern paper, §2
- Alayrac et al., *Flamingo* — gated cross-attention at scale (skim figures)
- HF blog: *Vision-language models explained* (LLaVA-family walkthrough)
