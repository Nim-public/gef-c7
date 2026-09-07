# 02.1 — Dense Models Comparison

> Subfolder index: [README.md](README.md) · Parent topic: [../02-embedding-models.md](../02-embedding-models.md)

The local dense embedders compared on the key dimensions:

```python
from sentence_transformers import SentenceTransformer

CANDIDATES = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "mpnet": "sentence-transformers/all-mpnet-base-v2",
    "bge": "BAAI/bge-small-en-v1.5",
    "e5": "intfloat/e5-base-v2",
}
```

| Model | Dim | Speed (1k sents) | Quality signal | Prefix |
|---|---|---|---|---|
| MiniLM | 384 | ~40s | the baseline | none |
| mpnet | 768 | ~160s | stronger, slower | none |
| BGE-small | 384 | ~40s | query instruction | "Represent this sentence..." |
| E5-base | 768 | ~160s | "query:"/"passage:" prefixes | mandatory |

The E5 and BGE models have **mandatory prefixes** — omitting them degrades quality silently. E5 needs `"query: "` before queries and `"passage: "` before documents. BGE wants a query instruction. These aren't optional style choices — they're part of the model's training contract.

The measurement protocol (W5-02 parent §3): same chunks, same eval set, same decision rule — one variable at a time. The bake-off table:

| Model | Hit@5 | MRR | tokens/s | Memory |
|---|---|---|---|---|
| MiniLM | | | | |
| BGE | | | | |
| E5 | | | | |

Fill from your harness runs; the winner is the fastest model that clears your quality bar.

## Exercises

1. Run the bake-off with prefix compliance; measure the quality delta with and without E5 prefixes.
2. The speed-vs-quality Pareto: plot hit rate vs tokens/s; identify the efficient frontier.
3. Cross-model agreement: same 10 queries through MiniLM and BGE — how often do the top-5 overlap? (Low overlap = the models see different things.)
