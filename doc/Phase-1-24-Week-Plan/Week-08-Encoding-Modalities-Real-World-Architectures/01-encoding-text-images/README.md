# Deep-Dive: Encoding Text & Images

Parent overview: [`../01-encoding-text-images.md`](../01-encoding-text-images.md)

This subfolder treats the text pipeline as the *template* for all encoders,
then builds the two image encoder families by hand: CNN mechanics computed
on small arrays you can verify, and ViT with honest token-count math. It
ends with the comparison table that decides your capstone encoders.

## File map

| File | What it covers |
|---|---|
| [`01-text-encoder-template.md`](01-text-encoder-template.md) | tokens → embeddings → pooling, as the reusable pattern |
| [`02-cnn-mechanics.md`](02-cnn-mechanics.md) | convolution/pooling/receptive fields by hand, on numpy |
| [`03-vit-patch-tokens.md`](03-vit-patch-tokens.md) | patches as tokens, count math, position embeddings |
| [`04-cnn-vs-vit.md`](04-cnn-vs-vit.md) | inductive bias, data hunger, compute trade-offs |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-text-encoder-template.md` — internalize the interface once.
2. `02-cnn-mechanics.md` — build the mechanics your hands can check.
3. `03-vit-patch-tokens.md` — the math that predicts memory and cost.
4. `04-cnn-vs-vit.md` — turn understanding into a capstone decision.

## Prerequisites

- Week 01 (tokens, embeddings), Week 02 (encoder interfaces).
- [`../../Week-07-Multimodal-AI-Building-the-Foundation/02-modality-processing-pipelines/`](../../Week-07-Multimodal-AI-Building-the-Foundation/02-modality-processing-pipelines/)
  — the preprocessing these encoders consume.
