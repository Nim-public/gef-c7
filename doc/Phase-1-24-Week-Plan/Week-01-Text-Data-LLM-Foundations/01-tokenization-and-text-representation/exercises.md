# Exercises — Tokenization & Text Representation

> Subfolder index: [README.md](README.md) · Parent: [../01-tokenization-and-text-representation.md](../01-tokenization-and-text-representation.md)

Expanded lab set for this subfolder. Each exercise lists the setup, the task, and a worked approach (not the full solution — write the code yourself, the approach keeps you honest). Use `data/corpus.txt` (any text ≥ 50 KB) as the shared corpus.

---

## E1 — Train and compare two BPE tokenizers

**Setup:** file 01.1's from-scratch trainer + the `tokenizers` library on the same corpus.

- Train toy BPE with 10, 50, and 200 merges; print the merge table after each run.
- Train `tokenizers` BPE with `vocab_size ∈ {500, 2000}`.
- On 50 held-out words, measure: average tokens/word, `<UNK>` count (toy), roundtrip validity (library).

**Worked approach:** reuse file 01.1 §2's loop; hold out words by shuffling and slicing *before* training. Expected result: toy-500 ≈ toy-2000 on common words, divergence on rare ones.

## E2 — Padding failure forensics

**Setup:** file 01.2's two-sentence batch. Task:

1. Compute mean last-hidden-state embeddings for the short sentence with and without an attention mask.
2. Measure cosine distance between the two.
3. Repeat with 5 sentences of increasing length ratio (1:2, 1:4, 1:8) — plot distance vs padding density.

**Worked approach:** distance grows with the fraction of padded positions attended to. Write down the padding-density number where *you* would call the result unusable.

## E3 — Encoding zoo comparison

**Task:** for 10 capstone-flavored strings (categories, multi-label genres, free text), produce encodings via `OneHotEncoder`, `MultiLabelBinarizer`, `CountVectorizer(binary=True)`, and a MiniLM embedding. For each: shape, memory (bytes), and whether two similar inputs have nonzero similarity.

**Worked approach:** one-hot/multi-hot → cosine ∈ {0, 1}; count vectors → small nonzero overlap; embeddings → graded similarity. Fill a 4×3 table (encoder × property) and state the rule: sparse for targets/small features, dense for similarity.

## E4 — Embedding geometry audit

**Task:** embed 30 sentences from your domain (10 per intended cluster); compute the full similarity matrix; then:

1. Report the strongest non-obvious pair and explain the encoder's grouping signal.
2. Project with PCA and UMAP; compare which plot matches your intended clusters.
3. Find the outlier (lowest max-similarity) and classify it: genuine novelty vs encoding artifact (emoji? mixed language? truncation?).

**Worked approach:** keep the plotting functions from file 01.4 §4; verify any 2-D cluster in the full 384-D space before believing it.

## E5 — Token-cost accountant

**Task:** build the `estimate_cost` utility (file 01.5 §4) and answer:

1. What does a 30-turn chat session cost if the full history is resent each turn? (Model the history growth: turn *k* has ~100 new tokens.)
2. How much does a 71% prefix-cache hit rate (W15-04) save on that session?
3. At what history length does trimming to the last 5 turns pay off in quality-neutral cost?

**Worked approach:** simulate the history growth with `tiktoken` counts; use o200k rates; produce a per-turn cost table. This is the week-1 seed of the E8-03 ledger.

## E6 — Roundtrip torture test

**Task:** build a 25-string edge suite (ZWSP, RTL marks, flag emoji ZWJ, ligatures, combined diacritics, mixed scripts, control chars) and run roundtrip + token-count checks across `tiktoken o200k`, Qwen's tokenizer, and DistilBERT's. Deliver a pass/fail table with the failure mechanism for each broken case.

**Worked approach:** the byte-level tokenizers roundtrip everything; DistilBERT's wordpiece may emit `[UNK]`. The interesting rows are the *near-misses* — decode roundtrips but token counts explode.

## Self-assessment

- Can you explain, without notes, why BPE needs pre-tokenization and byte-level fallback?
- Can you break batched inference silently by removing an attention mask — and detect it in the outputs?
- Can you predict, before measuring, whether a query will cost more tokens in Hindi than English — and by roughly how much?
