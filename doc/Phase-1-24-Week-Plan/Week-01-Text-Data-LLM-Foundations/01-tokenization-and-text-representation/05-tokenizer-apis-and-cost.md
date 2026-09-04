# 01.5 — Tokenizer APIs & Cost Accounting

> Subfolder index: [README.md](README.md) · Parent: [../01-tokenization-and-text-representation.md](../01-tokenization-and-text-representation.md)

---

## What you'll learn

- tiktoken vs HF tokenizers vs the OpenAI Tokenizer UI — when each is the right tool
- Model-family tokenization differences and their cost implications
- Multilingual and emoji edge cases, measured
- A reusable token-cost accountant for any prompt (the W15-05 ledger's counting layer)

## 1. The three tools and their roles

| Tool | Use | Model match |
|---|---|---|
| **tiktoken** | fast OpenAI-family BPE; cost/context estimates | OpenAI models (o200k_base, cl100k_base) |
| **HF tokenizers / AutoTokenizer** | the *actual* tokenizer of any open model | exact per-model fidelity |
| **OpenAI Tokenizer UI** | zero-setup visual checks | OpenAI models |

Rule: **token counts are model-family-specific.** The same text yields different counts on Qwen vs GPT vs Mistral — because vocabularies and merge tables differ. Never mix counts across families in budgets (W15-05's ledger pins the model per row for exactly this reason).

```python
import tiktoken

enc_o200k = tiktoken.get_encoding("o200k_base")     # gpt-4o family
enc_cl100k = tiktoken.get_encoding("cl100k_base")   # older OpenAI models

text = "The refund window is 5 business days."
print(len(enc_o200k.encode(text)), len(enc_cl100k.encode(text)))   # differ!
```

Or by model name: `tiktoken.encoding_for_model("gpt-4o-mini")`.

## 2. Model-family differences, measured

```python
from transformers import AutoTokenizer

samples = ["Hello world", "naïve café résumé", "🙂🙂🙂", "नमस्ते दुनिया", "def f(x): return x*2"]
qwen = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
bert = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")

for s in samples:
    print(f"{len(qwen.encode(s)):3d} qwen | {len(bert.encode(s)):3d} bert | {s!r}")
```

Typical findings: multilingual text costs far more tokens on English-centric tokenizers (each Devanagari character may be 2–3 tokens); emoji are 2–4 tokens each; code tokenizes densely on code-tuned vocabularies. **Cost implication:** multilingual support changes your token budgets and price projections (E8-03's forecast inputs).

## 3. Multilingual & emoji edge cases

```python
edge = ["café", "naïve", "🙂", "🇮🇳", "नमस्ते", "ﬁnance"]     # note the ligature ﬁ

for s in edge:
    ids = enc_o200k.encode(s)
    print(f"{s!r:14} -> {len(ids)} tokens, roundtrip ok={enc_o200k.decode(ids) == s}")
```

- **NFKC normalization** (W1-02) changes the input *before* tokenization — "ﬁnance" (ligature) vs "finance" tokenize differently; pick a policy and apply it consistently at ingest (W4-05)
- **Flag emoji** are two regional-indicator code points — often 2+ tokens and sometimes split weirdly
- **Zero-width characters** (ZWSP, RTL marks) are invisible but tokenized — strip them in cleaning (W1-02's `clean_text`)

## 4. The token-cost accountant

```python
from dataclasses import dataclass

@dataclass
class TokenCost:
    model: str
    in_rate: float      # $ per 1M input tokens
    out_rate: float     # $ per 1M output tokens

def count_tokens(texts: list[str], enc) -> int:
    return sum(len(enc.encode(t)) for t in texts)

def estimate_cost(prompt: str, expected_out: int, enc, rates) -> float:
    n_in = count_tokens([prompt], enc)
    return n_in * rates["in"] / 1e6 + expected_out * rates["out"] / 1e6

rates = {"in": 0.15, "out": 0.60}
prompt = "Answer using the context: ..." + ("x" * 6000)
print(f"${estimate_cost(prompt, 400, enc_o200k, rates):.4f}")
```

Use it three ways (all appear later in the program):

1. **Per-call accounting** — log `usage` from real responses (W10-04) and reconcile against these estimates
2. **Context budgeting** — `fit_context` needs exact token counts (W10-05)
3. **Eval cost planning** — a 100-case eval × N variants costs N× the estimate; know before running (W16-01)

## 5. Roundtrip and equivalence checks (the QA layer)

```python
for s in edge + samples:
    ids = enc_o200k.encode(s)
    assert enc_o200k.decode(ids) == s, f"roundtrip broken: {s!r}"
```

Also verify **cross-tokenizer roundtrip parity**: decode-with-A(encode-with-B(text)) generally *differs* — that's the tokenizer lock-in (W4-03's "same model" rule stated as a test).

## Exercises

1. Token-cost table: 10 of your capstone prompts across `o200k_base` and Qwen's tokenizer — counts, % difference, $ at two providers' rates.
2. Multilingual inflation: 5 English questions + their Hindi translations — token ratio; then translate the *corpus* instead and re-measure. Which direction is cheaper for retrieval (W4)?
3. Edge-case suite: 20 strings (emoji ZWJ sequences, RTL text, zero-width chars, ligatures, combined diacritics) — verify roundtrips on 3 tokenizers; document any failure.
4. Build `estimate_cost` into your W1-07 chat loop — print a running session cost after each turn (W15-05's ledger, week-1 edition).
5. Truncation-aware prompting: given a 4k-token context budget, write `fit_prompt(template, context, max_total)` using exact counts — and prove with `len(enc.encode(...))`.

## Pitfalls

- **Wrong encoding for the model family** — `cl100k_base` counts for a Qwen deployment are fiction; match encoding to deployment (E8-01's manifest pins tokenizers too)
- **Silent `max_tokens` truncation** — estimate completion length before calls, or read `finish_reason` (W1-07)
- **Assuming spaces are free** — leading spaces are part of tokens (`" world"` ≠ `"world"`); prompt formatting changes counts
- **Normalizing then tokenizing inconsistently** — NFKC before some calls and not others shifts counts between identical requests (W1-02's determinism rule)
- **Unicode normalization destroying meaning** — `NFKC` on `"①"` → `"1"`; apply selectively per field

## Resources

- [tiktoken](https://github.com/openai/tiktoken) — encodings, `encoding_for_model`
- HF [AutoTokenizer docs](https://huggingface.co/docs/transformers/main_classes/tokenizer) — chat templates, special tokens
- [OpenAI Tokenizer UI](https://platform.openai.com/tokenizer) — visual verification
- W1-01 (parent), W10-05 (budgets), E8-03 (ledger) — the counting consumers
