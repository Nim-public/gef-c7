# 02 — Embedding Models: The Bake-Off

> Week 5 index: [README.md](README.md)

**Session 1 topic:** *Embedding strategies: Compare characteristics of popular models like OpenAI embeddings, Sentence Transformers (all-MiniLM-L6-v2, all-mpnet-base-v2, E5, BGE), Cohere embeddings, and Sparse models (ELSER).*

---

## What you'll learn

- The dense-vs-sparse divide, and where each wins
- The leading model families with their real trade-offs
- A reproducible bake-off on *your* corpus (the only benchmark that matters)
- API vs local embedding: cost, latency, privacy math

## 1. The field, grouped

### Dense local (Sentence Transformers family)

| Model | Dim | Max input | Character |
|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | 512 tok | fast, small, the classic baseline |
| `all-mpnet-base-v2` | 768 | 512 tok | stronger, ~3× slower |
| `intfloat/e5-base-v2` | 768 | 512 tok | **prefix-sensitive** ("query:"/"passage:") |
| `BAAI/bge-small/base-en-v1.5` | 384/768 | 512 tok | top MTEB in class; query instruction |
| `intfloat/multilingual-e5-*` | 768 | 512 tok | 100+ languages |

### Dense via API

- **OpenAI** `text-embedding-3-small/large` (1536/3072 dims, 8k input): strong, zero infra, $0.02–0.13/1M tokens; privacy: your text leaves the building
- **Cohere** `embed-multilingual-v3` / `embed-english-*`: top multilingual quality, **int8/binary compressed variants** (cheap at scale), 512-token inputs

### Sparse (the other family)

- **ELSER** (Elastic Learned Sparse EncodeR): produces *learned term-weight vectors* — like BM25, but the "terms" are expanded by a model ("refund" also activates "reimbursement", "money-back")
- Runs inside Elasticsearch (proprietary model, free license terms to check)
- Wins: exact terms + learned synonyms, no vectors needed, transparent matches
- Loses: no true cross-lingual geometry, ecosystem lock-in, you need an ES stack

The practical takeaway even if you never run ELSER: **hybrid dense+sparse is the production pattern** — and a plain BM25 column (Week 4) is your stand-in for sparse until/unless ES enters your stack.

## 2. Dimension & cost intuition

- **Dims** = storage & speed: 384-d × 1M chunks × 4B ≈ 1.5 GB vs 1536-d ≈ 6 GB. LanceDB/FAISS compress (IVF-PQ, Week 9), but dims still drive query latency
- **API embedding cost**: ~$0.02/1M tokens ≈ essentially free at eval scale; the real costs are egress (privacy/compliance) and a network hop at query time (latency + availability)
- **MTEB leaderboard** (Hugging Face) ranks models on 56 tasks — useful shortlist generator, *not* a substitute for your corpus (leaderboard ≠ your domain; see exercise 1)

## 3. The bake-off (on YOUR corpus, with YOUR harness)

Same rules as always: same chunks (fix chunking first — don't confound variables), same eval set, same k.

```python
from sentence_transformers import SentenceTransformer

CANDIDATES = {
    "minilm":  ("sentence-transformers/all-MiniLM-L6-v2",  {}),
    "mpnet":   ("sentence-transformers/all-mpnet-base-v2", {}),
    "bge":     ("BAAI/bge-small-en-v1.5",  {"query_instruction": "Represent this sentence for searching relevant passages: "}),
    "e5":      ("intfloat/e5-base-v2",     {"query_prefix": "query: ", "doc_prefix": "passage: "}),
}

def encode_with(name, texts):
    model_id, cfg = CANDIDATES[name]
    model = SentenceTransformer(model_id)
    if name == "e5":                       # E5 REQUIRES its prefixes
        texts = [cfg["doc_prefix"] + t for t in texts]
    return model.encode(texts, normalize_embeddings=True)
```

Gotchas the bake-off *will* catch if you're careful:

- **E5/BGE prefixes**: e5 needs `query:` / `passage:` on respective sides; BGE wants a query instruction — omit them and you're measuring a handicapped model
- **Rebuild the index per model** — never mix vector spaces
- **Dims differ per model** — separate LanceDB tables (or fresh columns)
- Report: hit rate @5, mean reciprocal rank, index size, encode speed (docs/sec), query latency

APIs in the same harness: wrap `OpenAI().embeddings.create(input=..., model="text-embedding-3-small")` and Cohere's `embed()` behind the same `search_fn` signature — one line each, and the table gains two rows.

## 4. Decision guide

| Situation | Default pick |
|---|---|
| Fast baseline, CPU, English | `all-MiniLM-L6-v2` |
| +1–3% quality matters, CPU ok | `bge-small-en-v1.5` or `e5-base-v2` (with prefixes!) |
| Multilingual corpus | `intfloat/multilingual-e5-base` |
| Don't want to host, fine with egress | OpenAI `3-small` |
| Heavy non-English + rank matters | Cohere `embed-multilingual-v3` |
| Keyword-critical corpus (codes/names) | hybrid with BM25 regardless of dense choice |

The capstone rule: **one model wins, one model is pinned with `revision=`, one table exists.** Two "better" models living in parallel = nobody knows which answer to trust.

## Exercises

1. Run the full bake-off on your corpus (≥3 local models + 1 API). Full table: hit rate, MRR, ingest time, query latency, index size.
2. Test prefix sensitivity: run E5 *without* prefixes. How far does hit rate drop? (This is the most common silent RAG bug in the wild.)
3. Long-input probe: find a 600-token chunk in your corpus (over MiniLM's 512 limit) — how does the model truncate it, and did the *answer* chunk survive? This motivates file 01's chunk-size choices.
4. Price the crossover: 10M queries/month at 400 tokens each — API vs self-hosted MiniLM on a 4-core box. When does local win?
5. Multilingual test (if relevant): 5 Hindi/vernacular queries vs English docs. Which candidate survives? Which falls to zero?

## Pitfalls

- **Confound variables** — change embedder *and* chunker in one sweep, learn nothing
- **Prefix amnesia** (E5/BGE) — silent quality tax, never an error
- **Leaderboard worship** — MTEB ≠ your domain; your 25-query harness outranks any leaderboard
- **Different normalization per arm** — normalize all or none, and say which in the README
- **Forgetting re-embedding on model swap** — old vectors + new query model = silent zero-quality RAG (the Week 4 pitfall, now at bake-off scale)

## Resources

- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- Sentence Transformers [pretrained models list](https://sbert.net/docs/sentence_transformer_models.html) + E5/BGE model cards (prefix requirements live there)
- OpenAI [embeddings guide](https://platform.openai.com/docs/guides/embeddings) · Cohere [embed docs](https://docs.cohere.com/docs/embed-api)
- Elastic [ELSER docs](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html) — sparse expansion explained
