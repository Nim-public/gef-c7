# 01 — Tokenization & Text Representation

> Week 1 index: [README.md](README.md)

**Session 1 topic:** *Text Data (NLP): Tokenization (word, char, subword), stop & special tokens (`<PAD>`, `<EOS>`, `<CLS>`), string manipulation, basic encodings (one-hot, multi-label), intro to embeddings & visualization.*

---

## What you'll learn

- Why models need tokens, not raw strings
- The three tokenization strategies and where each is used
- How BPE builds a subword vocabulary
- What special tokens are for and how padding + attention masks work
- One-hot and multi-label encodings — and why they don't scale
- What embeddings are, how similarity works, and how to visualize them

## 1. Why tokenization exists

Neural networks compute with numbers. Before any model reads `"I love RAG"`, the string must become a sequence of integers: **text → tokens → token IDs → vectors**.

Every LLM cost, context-window, and latency question is answered in tokens, not words or characters:

- context window = max token count (input + output)
- API pricing = $ per million tokens
- `"hello world"` is 2 words but may be 2–3+ tokens depending on the tokenizer

## 2. The three tokenization strategies

| Strategy | Idea | Example (`unbelievable`) | Used by |
|---|---|---|---|
| **Word** | split on whitespace/punctuation | `["unbelievable"]` | early NLP, word2vec era |
| **Character** | every character is a token | `["u","n","b","e",...]` | Karpathy's char-RNN, some small models |
| **Subword** | learn frequent chunks; rare words split into pieces | `["un","believ","able"]` | **all modern LLMs** (BPE, WordPiece, SentencePiece) |

**Trade-off triangle:** vocabulary size ↔ sequence length ↔ ability to handle unseen words.

- Word-level: tiny sequences, huge vocabulary, fails on unseen/rare words (OOV problem)
- Character-level: no OOV ever, but sequences become very long → expensive attention
- Subword: the compromise — common words stay whole, rare words decompose into known pieces

### Hands-on: three ways to split the same sentence

```python
text = "Unbelievable! LLMs read tokens, not words."

print(text.split())
# ['Unbelievable!', 'LLMs', 'read', 'tokens,', 'not', 'words.']

print(list(text))
# every character, punctuation included
```

```python
import tiktoken

enc = tiktoken.get_encoding("o200k_base")      # used by newer OpenAI models
ids = enc.encode(text)
print(ids)
print([enc.decode([i]) for i in ids])
print(f"{len(text.split())} words -> {len(ids)} tokens")
```

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
ids = tok(text)["input_ids"]
print(tok.convert_ids_to_tokens(ids))
```

Run all three on the same sentence and compare segmentations. Try hard words: `antidisestablishmentarianism`, emoji 🙂, Hindi text `नमस्ते`, code `def f(x): return x*2`.

### Byte-Pair Encoding (BPE) intuition

BPE is a compression algorithm turned tokenizer:

1. start with characters as the vocabulary
2. count adjacent symbol pairs in a large corpus
3. merge the most frequent pair into a new symbol; repeat ~50k–200k times
4. result: frequent words become single tokens, rare words remain multi-token

You can train a tiny BPE yourself to see the merges happen:

```python
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders

tok = Tokenizer(models.BPE())
tok.pre_tokenizer = pre_tokenizers.Whitespace()
tok.decoder = decoders.BPEDecoder()
trainer = trainers.BpeTrainer(vocab_size=500, special_tokens=["<PAD>", "<EOS>", "<UNK>"])
tok.train_from_directory(["data/corpus.txt"], trainer)
```

## 3. Special tokens

Special tokens are reserved vocabulary entries with protocol meaning — they are *not* words:

| Token | Purpose |
|---|---|
| `<PAD>` | filler so all sequences in a batch have equal length |
| `<EOS>` / `<|endoftext|>` | "text ends here" — generation stops when the model emits it |
| `<CLS>` | BERT-style sentence-level summary position for classification |
| `<SEP>` | separator between two segments (question / passage) |
| `<UNK>` | fallback for out-of-vocabulary items (char/word models only) |
| `<|im_start|>`, `<|im_end|>` | chat template markers delimiting speaker turns |

Padding is why attention masks exist: `<PAD>` positions must be ignored by attention.

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
batch = tok(["short one", "a much longer sentence with more words in it"],
            padding=True, return_tensors="pt")

print(batch["input_ids"])
print(batch["attention_mask"])
print(tok.convert_ids_to_tokens(batch["input_ids"][0]))
```

Observe: the short sequence gets `[PAD]` tokens appended and a matching row of `0`s in `attention_mask` — "model, don't look here."

Chat models wrap every message in special tokens via a **chat template** — that's how `system`/`user`/`assistant` roles are encoded. Inspect one:

```python
print(tok.apply_chat_template(
    [{"role": "user", "content": "hi"}], tokenize=False))
```

## 4. Basic encodings: one-hot and multi-label

Before embeddings, text was encoded as sparse vectors.

### One-hot (single label)

One `1` in a vector of vocabulary length. Used for: classification targets, categorical features.

```python
import numpy as np

vocab = {"action": 0, "comedy": 1, "drama": 2, "horror": 3}
def one_hot(label):
    v = np.zeros(len(vocab))
    v[vocab[label]] = 1
    return v

one_hot("comedy")        # [0., 1., 0., 0.]
```

**Problems:** no notion of similarity (`action` and `comedy` are as different as any two words), and the vector size grows with vocabulary (50k+ dims, almost all zeros).

### Multi-label (multi-hot)

Several `1`s at once — a movie can be *action and comedy*:

```python
def multi_hot(labels):
    v = np.zeros(len(vocab))
    for label in labels:
        v[vocab[label]] = 1
    return v

multi_hot(["action", "comedy"])   # [1., 1., 0., 0.]
```

The scikit-learn equivalents you'll use in practice: `OneHotEncoder`, `LabelBinarizer`, `MultiLabelBinarizer`, `CountVectorizer`.

## 5. Embeddings: dense, learned, and similarity-aware

An **embedding** maps each token/word/document to a dense vector (e.g., 384–4096 floats) where *distance encodes meaning*. Similar items land close together — a property one-hot can never have.

A clean self-contained demo (toy vectors for intuition):

```python
import numpy as np
import matplotlib.pyplot as plt

words = ["king", "queen", "prince", "banana", "apple", "mango"]
vecs = np.array([
    [0.90, 0.10], [0.85, 0.18], [0.80, 0.12],
    [-0.70, 0.80], [-0.65, 0.85], [-0.75, 0.90],
])

def cosine(a, b):
    return a @ b / (np.linalg.norm(a) * np.linalg.norm(b))

print("king·queen:", cosine(vecs[0], vecs[1]))     # ~0.99 (similar)
print("king·banana:", cosine(vecs[0], vecs[3]))    # negative (unrelated)

for w, v in zip(words, vecs):
    plt.scatter(*v)
    plt.annotate(w, v)
plt.title("Embedding space (2-D toy example)")
plt.savefig("toy_embeddings.png")
```

Real embeddings come from models trained on corpora (Word2Vec/GloVe historically; transformer encoders today — you'll use `sentence-transformers/all-MiniLM-L6-v2` properly in Week 4). This week the goal is the *concept*: dense vectors where geometry = semantics.

### Visualization in practice

- 2-D scatter with matplotlib after dimensionality reduction (PCA)
- UMAP/t-SNE for real corpora — clusters reveal topics without any labels
- [TensorFlow Embedding Projector](https://projector.tensorflow.org) to explore pretrained word embeddings interactively

## Tools

| Tool | Use |
|---|---|
| `tiktoken` | fast OpenAI-compatible BPE; count tokens for cost/context |
| `transformers` (AutoTokenizer) | load any model's tokenizer; chat templates, padding, special tokens |
| `tokenizers` | train your own BPE/WordPiece tokenizers |
| `numpy` | build one-hot / multi-hot vectors by hand |
| `matplotlib` + PCA/UMAP | visualize embedding spaces |
| [OpenAI Tokenizer UI](https://platform.openai.com/tokenizer) | paste text, see token boundaries live |

## Exercises

1. Encode `"The cost is $0.15 per 1M tokens 🙂"` with tiktoken. How many tokens, how many words? Which characters get merged?
2. Tokenize the same text with `bert-base-uncased` and `Qwen/Qwen2.5-0.5B` tokenizers. Explain the differences.
3. Pad a two-sentence batch with `padding=True` and verify `attention_mask`; then try `padding="max_length", max_length=16`.
4. Build multi-hot encodings for 10 movie genres and write a function `jaccard(a, b)` measuring genre overlap.
5. Print the chat template of `Qwen/Qwen2.5-0.5B-Instruct` for a 3-turn conversation. Which special tokens delimit each role?

## Pitfalls

- **Counting words instead of tokens** for cost/context estimates — always tokenize.
- **Different models, different tokenizers** — token counts are not portable across model families.
- **Stripping "weird" characters** before tokenization can silently destroy meaning (emoji, accents, Indic scripts).
- **`<PAD>` without attention mask** — the model attends to padding and results degrade mysteriously.

## Resources

- Karpathy, *Let's build the GPT Tokenizer* (YouTube) — the definitive BPE walkthrough
- Hugging Face NLP Course, ch. 2 & 6 (tokenizers)
- Jurafsky & Martin, *Speech and Language Processing*, ch. 2 (text basics) — free online
- OpenAI, *What are tokens and how do I count them?* (help center)
