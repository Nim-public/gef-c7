# 03 — NLP Tasks: Summarization, Q&A, Translation, Embeddings

> Week 2 index: [README.md](README.md)

**Session 2 topic:** *Different NLP Tasks: Summary, Q&A, etc.*

---

## What you'll learn

- Abstractive summarization with encoder-decoder models (BART family)
- Extractive vs generative question answering — and when each is right
- Translation with MarianMT
- Sentence embeddings for similarity/dedup — your first taste of semantic search (Week 4 preview)

## 1. Summarization (abstractive)

Encoder-decoder models *write* new sentences rather than copying them:

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

article = """
The Transformer architecture, introduced in 2017, replaced recurrence with
self-attention, allowing models to process all tokens in parallel while
capturing long-range dependencies. This enabled scaling laws: performance
improves predictably with more data, parameters, and compute. Decoder-only
transformers trained on next-token prediction became the dominant paradigm
for language models, culminating in instruction-tuned assistants aligned
with human preferences.
"""

summarizer(article, max_length=45, min_length=15, do_sample=False)[0]["summary_text"]
```

Controls that matter:

- `max_length`/`min_length` — summary size; generation stops at EOS or the cap
- `do_sample=True, temperature=...` — variance; usually `False` for factual summaries
- **Input limit ≈ 1024 tokens** (BART) — long documents need chunk-then-summarize (map-reduce), which is exactly the chunking idea RAG formalizes in Week 4

Alternatives to try: `google/pegasus-xsum` (very short summaries), `sshleifer/distilbart-cnn-12-6` (6× faster, near quality).

### Abstractive vs extractive — know which you need

| | Abstractive (BART) | Extractive (e.g., `TextRank`/`BertExtractor`) |
|---|---|---|
| Output | new sentences | selected original sentences |
| Hallucination risk | real — verify entities/numbers | none (but incoherent selections possible) |
| Compression | high | limited (must keep whole sentences) |
| Use when | digests, briefings | legal/compliance where wording matters |

## 2. Question answering

### Extractive QA — the answer is a *span* in a passage

```python
qa = pipeline("question-answering", model="distilbert/distilbert-base-cased-distilled-squad")

passage = """
RAG combines a retriever that searches a knowledge base with a generator
that conditions its answer on the retrieved passages. Retrieval grounds
the model in facts it was never trained on and enables citations.
"""
qa(question="What grounds the generator in facts?", context=passage)
# {'score': 0.79, 'start': ..., 'end': ..., 'answer': 'the retrieved passages'}
```

Returns a **span + score + offsets** — highlightable in UIs, auditable. But: no passage, no answer. The question "how many RAG?" with no passage fails silently.

This is precisely the mechanism behind *closed-book vs open-book* LLM answering — the conceptual seed of RAG (Week 4: replace "one passage you pass in" with "retriever that finds the passage").

### Generative QA — answer written from context (or not)

```python
from transformers import pipeline

gen_qa = pipeline("text2text-generation", model="google/flan-t5-base")

gen_qa("answer the question: what grounds the generator? context: " + passage)[0]["generated_text"]
```

| | Extractive | Generative |
|---|---|---|
| Answer form | exact span | natural sentence |
| Offsets/citations | yes | needs alignment work |
| Synthesis across passages | no | yes |
| Hallucination | no | yes — measure it (Week 16) |

### The retrieval sandwich (read this twice)

Both models above answer *given* a passage. Whoever finds the passage is the real system: keyword search (Week 1 skills) → embeddings (below) → vector DBs (Week 4) → full RAG (Weeks 4–6).

## 3. Translation

```python
translator = pipeline("translation_en_to_de", model="google-t5/t5-base")
translator("Retrieval makes answers verifiable.")[0]["translation_text"]

# Hindi pair, dedicated compact models:
hi = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")
hi("Knowledge retrieval improves factuality.")[0]["translation_text"]
```

- One model per language pair (Marian/opus-mt) — small, fast, CPU-friendly
- Multilingual many-to-many: `facebook/nllb-200-distilled-600M` (language codes like `hin_Deva`)
- LLMs translate too, but dedicated models are cheaper/deterministic; LLMs win on style/domain adaptation via prompt
- The capstone task this week explicitly includes *optional translation* — file 06 wires this in

## 4. Sentence embeddings — meaning as geometry

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")   # 384-dim, fast

sentences = [
    "How do I reset my password?",
    "I can't log in to my account.",
    "Where is my refund?",
]
emb = model.encode(sentences, normalize_embeddings=True)

print(util.cos_sim(emb[0], emb[1]))    # ~0.5+  (same intent, different words!)
print(util.cos_sim(emb[0], emb[2]))    # ~0.1   (different intent)
```

`"reset my password"` and `"can't log in"` share no keywords — keyword search scores them 0, embeddings score them high. **That gap is the entire motivation for semantic search and RAG.**

Standard patterns:

```python
import numpy as np

def dedup(emb, thresh=0.95):
    sims = emb @ emb.T
    pairs = np.argwhere(np.triu(sims, 1) > thresh)
    return [(int(i), int(j), float(sims[i, j])) for i, j in pairs]

def semantic_search(query, corpus_emb, k=3):
    q = model.encode([query], normalize_embeddings=True)[0]
    sims = corpus_emb @ q
    return np.argsort(-sims)[:k]
```

Model picking: `all-MiniLM-L6-v2` (384d, fast) vs `all-mpnet-base-v2` (768d, stronger) vs `BAAI/bge-*` / `intfloat/e5-*` (instruction-aware, top of MTEB). Full comparison lands in Week 5; today, encode and measure cosine.

## Exercises

1. Summarize one long article twice: once whole, once via chunk-map-reduce (3 chunks → 3 summaries → 1 final). Compare quality and cost.
2. Build a mini open-book QA over 3 paragraphs of *your capstone data*: extractive for "who/when/where", generative for "why/how". Note where each fails.
3. Translate 5 support phrases EN→HI with `opus-mt-en-hi`; back-translate to EN with the reverse model. Where does meaning drift?
4. Encode 20 sentences from your domain; find the nearest pair with `cos_sim`. Inspect: is the high similarity *real* semantic similarity or an artifact (length, boilerplate)?
5. Combine skills: NER (file 02) on a summary output — do extracted entities match the source article? This is your first hallucination check.

## Pitfalls

- **Summarizer input caps** — chunk documents; don't silently truncate to 1024 tokens
- **Numbers and names in abstractive summaries** — verify against source (script it: regex the entities, diff)
- **Extractive QA with a wrong-passage** returns a confidently wrong span — score threshold matters
- **opus-mt language-pair confusion** — `en-hi` ≠ `hi-en`; wrong pair = gibberish
- **Embedding model mismatch at query time** — corpus and query must use the *same* model (they're different vector spaces otherwise); production incident waiting to happen

## Resources

- HF Course ch. 1 (tasks) & ch. 7 (summarization, QA)
- [Sentence Transformers docs](https://sbert.net) — quickstart + semantic search patterns
- Lewis et al., *RAG paper* (skim now — Week 4 deep dive)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — embedding model rankings
