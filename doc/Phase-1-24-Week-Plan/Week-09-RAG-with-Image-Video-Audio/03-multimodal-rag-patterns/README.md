# Deep-Dive: Multimodal RAG Patterns

Parent overview: [`../03-multimodal-rag-patterns.md`](../03-multimodal-rag-patterns.md)

The four RAG patterns named here differ in *where modality and text meet*:
before indexing, in embedding space, or at generation. This subfolder
implements each pattern's trade-offs with numbers you can measure, and ends
with the routing table your capstone planner uses.

## File map

| File | What it covers |
|---|---|
| [`01-traditional-rag-review.md`](01-traditional-rag-review.md) | The text-RAG contract, restated for extension |
| [`02-caption-then-index.md`](02-caption-then-index.md) | Pattern 1: caption → text index, trade-offs |
| [`03-unified-embedding-spaces.md`](03-unified-embedding-spaces.md) | Pattern 2: CLIP-style shared space |
| [`04-vlm-generation.md`](04-vlm-generation.md) | Pattern 3: VLM economics and grounding |
| [`05-pattern-selection.md`](05-pattern-selection.md) | The routing table + decision drills |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-traditional-rag-review.md` — the contract everything extends.
2. `02-caption-then-index.md` — the cheapest pattern, its failure modes.
3. `03-unified-embedding-spaces.md` — the CLIP-native pattern.
4. `04-vlm-generation.md` — the expensive, most-grounded pattern.
5. `05-pattern-selection.md` — pick per query, not per corpus.

## Prerequisites

- Week 04 (text RAG), Week 08 (encoders, VLM pattern).
- [`../../Week-07-Multimodal-AI-Building-the-Foundation/01-multimodal-ai-landscape/04-the-modality-gap.md`](../../Week-07-Multimodal-AI-Building-the-Foundation/01-multimodal-ai-landscape/04-the-modality-gap.md)
  — the gap this week's patterns navigate.
