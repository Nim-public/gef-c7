# 02.3 — The Bake-off Protocol

> Subfolder index: [README.md](README.md) · Parent topic: [../02-embedding-models.md](../02-embedding-models.md)

The protocol that turns model selection from opinion to measurement. Rules:

1. **Same chunks** across all models — the chunking is held constant
2. **Same eval set** — the W4-05 25-query harness
3. **Same decision rule** — hit rate @5, the primary metric
4. **Same hardware** — or note the differences
5. **One variable at a time** — embedder only, chunking fixed

The output table (from the parent file's protocol):

| Model | Hit@5 | MRR | Dim | Size | Speed | Cost/1k |
|---|---|---|---|---|---|---|
| MiniLM | 0.72 | 0.58 | 384 | 90 MB | 40/s | free |
| BGE-small | 0.76 | 0.61 | 384 | 90 MB | 40/s | free |
| E5-base | 0.74 | 0.59 | 768 | 440 MB | 160/s | free |
| OpenAI 3-small | 0.78 | 0.63 | 1536 | API | API | $0.02/1M |
| **Selected** | | | | | | |

The **Selected** row names the model, the revision, and the evidence. The runner-up is recorded as the fallback (W2-06's protocol).

## Exercises

1. Run the bake-off with your eval set and at least 3 local models + 1 API model; produce the table.
2. The prefix-compliance test: E5 without prefixes vs with — the quality delta measured.
3. The robustness slice: evaluate on the adversarial queries (W4-04's probes) — which model handles identifiers best?

## Pitfalls

- **Changing the chunker during the bake-off** — the confound invalidates the comparison (W5-02's rule)
- **Comparing across different normalization settings** — pin normalize=True everywhere
- **No held-out queries** — the bake-off tunes on the eval set; hold out 10 queries for validation
- **Forgetting to re-embed on model switch** — the old vectors are incompatible with the new model's query embeddings

## Resources

- W5-02 parent (the full model landscape), W4-05 (the harness) — composed here
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — the shortlist generator
