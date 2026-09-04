# 01.1 — Tokenization Strategies & BPE From Scratch

> Subfolder index: [README.md](README.md) · Parent: [../01-tokenization-and-text-representation.md](../01-tokenization-and-text-representation.md)

---

## What you'll learn

- The trade-off triangle: vocabulary size ↔ sequence length ↔ unseen-word handling
- BPE's merge loop implemented from scratch, step by step, on your own corpus
- How real tokenizers differ from the toy version (pre-tokenization, byte-level, special handling)
- How to measure OOV behavior and segmentation quality

## 1. The three strategies, with measured consequences

```python
text = "Unbelievable! LLMs read tokens, not words."

word_tokens = text.split()          # 6 tokens — huge vocab, no OOV handling
char_tokens = list(text)            # 36 tokens — tiny vocab, very long sequences
```

The consequence table, made concrete on a 1M-word corpus:

| Strategy | Vocab size | Avg tokens/word | "antidisestablishmentarianism" |
|---|---|---|---|
| Word | 500k+ | ~1.3 (with punct splits) | `<UNK>` — information destroyed |
| Character | ~100 | ~29 | fine, but 29 positions of attention cost |
| Subword (BPE) | 30–50k | ~4–6 | split into known morphemes |

**Rule you can derive:** OOV count grows with vocabulary sparsity; sequence cost grows inversely. BPE sits at the knee of both curves.

## 2. BPE from scratch — the merge loop

Minimal, faithful implementation (training on a small corpus):

```python
from collections import Counter

def get_pair_stats(corpus: list[list[str]]) -> Counter:
    stats = Counter()
    for word in corpus:
        for a, b in zip(word, word[1:]):
            stats[(a, b)] += 1
    return stats

def merge(corpus: list[list[str]], pair: tuple, new_symbol: str) -> list[list[str]]:
    merged = []
    for word in corpus:
        out, i = [], 0
        while i < len(word):
            if i < len(word) - 1 and (word[i], word[i+1]) == pair:
                out.append(new_symbol); i += 2       # skip both parts
            else:
                out.append(word[i]); i += 1
        merged.append(out)
    return merged

# corpus: words as symbol lists, end-of-word marker "</w>" appended
corpus = [list(w) + ["</w>"] for w in "low lower lowest newest widest".split() for _ in range(2)]

vocab_merges = []
for i in range(10):
    stats = get_pair_stats(corpus)
    if not stats: break
    best, count = stats.most_common(1)[0]
    corpus = merge(corpus, best, best[0] + best[1])
    vocab_merges.append((best, count))
    print(f"merge {i+1:2d}: {best} -> {best[0]+best[1]}  (count {count})")
```

What to observe while it runs: the first merges are frequency-driven character pairs; later merges become whole words (`low` + `</w>`); rare words never merge — they stay multi-token. That *is* the subword property.

## 3. Real tokenizers add three things the toy lacks

```python
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders

tok = Tokenizer(models.BPE())
tok.pre_tokenizer = pre_tokenizers.Whitespace()        # (1) pre-tokenization
tok.decoder = decoders.BPEDecoder()
trainer = trainers.BpeTrainer(vocab_size=500, special_tokens=["<PAD>", "<EOS>", "<UNK>"])
tok.train_from_directory(["data/corpus.txt"], trainer)

enc = tok.encode("Unbelievable! LLMs read tokens.")
print(enc.tokens)                                      # decode-able back to text
```

1. **Pre-tokenization** — real BPE never merges across spaces/punctuation; the toy above can. This is why `"cat"` and `"cat!"` tokenize differently.
2. **Byte-level fallback** — GPT-style tokenizers operate on *bytes*, so any Unicode string is representable with zero `<UNK>` (W1-01's parent claim, now the mechanism).
3. **Learned merges with counts** — production vocabularies are 30k–200k merges; `vocab_size=500` shows the mechanics in seconds.

## 4. Measuring segmentation quality

Two quick metrics on a sample of your corpus:

```python
def morpheme_score(enc, words: list[str]) -> float:
    """Average tokens per word — lower is better for common words."""
    total = sum(len(enc.encode(w)) for w in words)
    return total / len(words)

common = ["the", "and", "refund", "payment", "invoice"]
rare   = ["antidisestablishmentarianism", "Kubernetes", "GPT-4o-mini"]
print("common:", morpheme_score(enc, common))     # ~1.0 — whole words
print("rare:", morpheme_score(enc, rare))         # 2–5 — decomposed
```

Also verify **reversibility**: `enc.decode(enc.encode(text)) == text` must hold for *any* string including emoji and accented text (byte-level guarantees this; word-level does not).

## Exercises

1. Train BPE with `vocab_size=200` and `vocab_size=2000` on the same corpus; compare average tokens/word on held-out text. Plot both curves.
2. Feed the toy trainer a corpus where one word appears 100× more often than others — show its merge order becomes a single token early (frequency-driven behavior).
3. Tokenize `"退款政策"` (Chinese) and `"naïve café"` with a byte-level vs character-level tokenizer — explain why byte-level never emits `<UNK>`.
4. Compute the OOV rate: for 200 held-out words, how many produce `<UNK>` under (a) a word-level tokenizer built from your corpus, (b) BPE? Table it.
5. Estimate context cost: encode 10 of your capstone prompts with `tiktoken` — report tokens vs words and the implied cost at your provider's rate.

## Pitfalls

- **Merging across word boundaries** (no pre-tokenizer) — tokens like `"the_cat"` make retrieval matches impossible
- **Vocabulary too small for the domain** — domain jargon explodes into fragments; measure tokens/word on *your* text
- **Assuming token boundaries align with words** — `" reimbursed"` often starts with a space token; string matching on decoded tokens fails
- **Case sensitivity** — BPE learns `"The"` and `"the"` separately unless lowercasing; doubles effective vocabulary

## Resources

- Sennrich et al., *Neural Machine Translation of Rare Words with Subword Units* (2016) — the original BPE-for-NMT paper
- Karpathy, *Let's build the GPT Tokenizer* (YouTube) — builds exactly the §2 toy to production quality
- Hugging Face [tokenizers docs](https://huggingface.co/docs/tokenizers/index) — trainers, pre-tokenizers, decoders
- Jurafsky & Martin, *Speech and Language Processing*, ch. 2 — BPE and the subword landscape
