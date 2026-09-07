# 03.1 — Summarization

> Subfolder index: [README.md](README.md) · Parent: [../03-nlp-tasks.md](../03-nlp-tasks.md)

---

## What you'll learn

- Abstractive summarization with encoder-decoder models — controls and their effects
- The chunk-map-reduce pattern for long documents
- Faithfulness verification: entity/number checks against the source
- Compression-format selection (abstractive vs extractive) by use case

## 1. The generation controls

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

article = """..."""    # your source document

summary = summarizer(article, max_length=60, min_length=20,
                     do_sample=False)[0]["summary_text"]
```

| Control | Effect | Trap |
|---|---|---|
| `max_length` / `min_length` | summary size in tokens | hitting `max_length` mid-sentence; EOS should end it first |
| `do_sample=False` | greedy, deterministic | required for eval comparability (W15-03) |
| `num_beams` | beam search breadth | 4–8 improves fluency, costs time |
| `repetition_penalty` | penalizes repeated n-grams | too high → ungrammatical output |

Input cap reality: BART-family handles ~1024 tokens — longer documents need the §2 pattern, or silent truncation eats your conclusion (check `len(tok(article)["input_ids"])` first).

## 2. Chunk-map-reduce for long documents

```python
def summarize_long(text: str, chunker, summarizer, final_max=150) -> str:
    chunks = chunker(text, size=900)                    # W4-02's chunker, overlap 0
    partials = [summarizer(c, max_length=100, min_length=30,
                           do_sample=False)[0]["summary_text"] for c in chunks]
    joined = " ".join(partials)
    return summarizer(joined, max_length=final_max, min_length=50,
                      do_sample=False)[0]["summary_text"]
```

Map-reduce: summarize each chunk (map), then summarize the summaries (reduce). Preserves coverage of long documents at the cost of detail per section — and a second summarization call. Variants: **refine** (feed each summary + next chunk iteratively — keeps chronology) and **hierarchical** (chunk → section summaries → section-of-sections — W13-01's recursive idea).

## 3. Faithfulness verification (the hallucination check)

Abstractive models *invent* — the verification makes it visible:

```python
import re

def check_faithfulness(summary: str, source: str) -> dict:
    issues = []
    # numbers must appear in the source
    for num in re.findall(r"\b\d[\d,.]*\b", summary):
        if num.replace(",", "") not in source.replace(",", ""):
            issues.append(f"number {num} not in source")
    # named entities must appear (crude but effective)
    for cap in re.findall(r"\b[A-Z][a-z]{2,}\b", summary):
        if cap not in source:
            issues.append(f"entity '{cap}' not in source")
    return {"issues": issues, "faithful": not issues}

print(check_faithfulness(summary, article))
```

The checks are deliberately crude — they catch the common failure (invented numbers/names) without an LLM judge. For deeper checks: NLI-based entailment scoring (W2-02's zero-shot mechanism: "premise: source / hypothesis: summary sentence") or the Ragas faithfulness metric (W5-05) — the same idea at different rigor.

## 4. Abstractive vs extractive — the selection table

| | Abstractive | Extractive |
|---|---|---|
| compression | high (new sentences) | limited (original sentences kept) |
| hallucination | possible | none (verbatim) |
| fluency | natural | can be disjointed |
| verification | needs checks (§3) | trivially faithful |
| compliance/legal use | risky | **required** |

Selection rule: extractive where the wording is the contract (legal, medical, compliance); abstractive where the *gist* is the product (briefings, digests). Hybrids exist: extract first, abstract the extraction.

## Exercises

1. Control sweep: same document, `max_length` ∈ {40, 80, 150} × `num_beams` ∈ {1, 4, 8} — 9 summaries, ranked by a judge (you); identify the control that matters most.
2. Map-reduce vs whole-doc: 20k-token article — chunk-map-reduce vs naive truncation at 1024. What does truncation silently destroy? (Check the conclusion.)
3. Faithfulness audit: run `check_faithfulness` on 10 summaries; classify each issue (invented number / wrong entity / unsupported claim) — the taxonomy of summarization failure.
4. Extract-vs-abstract: same document both ways; which preserves the *numbers* exactly? (The compliance-selection rule, demonstrated.)
5. Refine variant: implement iterative refinement (summary + next chunk → new summary) — compare against map-reduce on a chronological document.

## Pitfalls

- **Silent truncation before summarization** — the model never saw your conclusion; check token counts first (W1-01's accounting)
- **Invented numbers** — the most damaging summarization failure; verify numerically (§3) on every production summary
- **Beam search without length control** — beams can produce overly long or short outputs; pair with length penalties
- **Map-reduce losing cross-chunk references** — "as mentioned above" dangles; hierarchical patterns or entity-aware merging help
- **Comparing summaries without a reference protocol** — blind ranking with a fixed rubric, or you're measuring taste

## Resources

- HF [summarization task guide](https://huggingface.co/docs/transformers/tasks/summarization) — models and controls
- Zhang et al. on entropy-based extractive summarization; the LEAD baseline (why "first 3 sentences" is strong)
- W1-04 (chunking inputs), W2-06 (eval discipline), W5-05 (faithfulness metric) — composed here
