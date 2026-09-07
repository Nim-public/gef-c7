# 01.2 — Special Tokens & Attention Masks

> Subfolder index: [README.md](README.md) · Parent: [../01-tokenization-and-text-representation.md](../01-tokenization-and-text-representation.md)

---

## What you'll learn

- Special tokens as *protocol*, not vocabulary
- Padding + attention masks: the pair that must never be separated
- Padding strategies (longest vs max_length vs quantized) and their memory implications
- Chat templates: how system/user/assistant turns become token sequences

## 1. Special tokens as protocol

Each reserved token carries meaning the model was trained on:

| Token | Meaning | Where it matters |
|---|---|---|
| `<PAD>` | "ignore this position" | batched inference/training |
| `<EOS>` / `</s>` / `<|endoftext|>` | sequence ends | stopping generation (file W1-07) |
| `<CLS>` | sentence summary slot | BERT-style classification |
| `<SEP>` | segment boundary | question/passage pairs |
| `<UNK>` | out-of-vocabulary | word/char models only |
| `<|im_start|>`, `<|im_end|>` | speaker-turn delimiters | chat templates (Qwen, etc.) |

Critical property: these are **fixed ids** learned during pre-training. Using the wrong model's special tokens (`<CLS>` on a GPT-style decoder) is a silent bug — the model has never seen it in that role.

## 2. Padding + attention masks — the pair that must never be separated

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
batch = tok(["short", "a much longer sentence with several more words in it"],
            padding=True, return_tensors="pt")

print(batch["input_ids"])
# [[ 101,  2722,  102,    0,    0,    0, ...],
#  [ 101,  1037,  2400, ...,  102,    0,    0]]
print(batch["attention_mask"])
# [[1, 1, 1, 0, 0, 0],
#  [1, 1, 1, 1, 1, 1, ...]]
```

The mask is what tells attention *"the zeros are filler — never look there."* Demonstrating the failure on purpose:

```python
import torch
from transformers import AutoModel

model = AutoModel.from_pretrained("distilbert/distilbert-base-uncased")
ids = batch["input_ids"]

with_mask = model(input_ids=ids, attention_mask=batch["attention_mask"]).last_hidden_state
no_mask   = model(input_ids=ids)                       # mask defaults to all-ones!

# the short sentence's embedding now includes attention TO padding tokens:
print(not torch.allclose(with_mask[0, 0], no_mask[0, 0]))    # True — outputs differ
```

The mask-less run *silently* produces different embeddings for the short sentence — the exact bug class that degrades RAG embeddings when batches are padded carelessly (file W4-03's context).

### Padding strategies

| Strategy | Behavior | Use |
|---|---|---|
| `padding=True` (longest in batch) | pad to batch max | training/inference default |
| `padding="max_length"` + `max_length` | fixed width | consistent shapes; wasted compute |
| `padding="longest"` | same as True | — |

Sweep the three on a batch with mixed lengths and measure: tensor shape, attention-mask density, inference time. Fixed-width padding with `max_length=512` on a batch of 8-token inputs wastes ~95% of positions.

## 3. Chat templates — turns become tokens

Instruct models expect their special-token dialogue format. The tokenizer's chat template renders it:

```python
messages = [
    {"role": "system", "content": "You are concise."},
    {"role": "user", "content": "What is RAG?"},
    {"role": "assistant", "content": "Retrieval-Augmented Generation."},
    {"role": "user", "content": "Why use it?"},
]

rendered = tok.apply_chat_template(messages, tokenize=False)
print(rendered)
# <|im_start|>system\nYou are concise.<|im_end|>\n
# <|im_start|>user\nWhat is RAG?<|im_end|>\n
# <|im_start|>assistant\nRAG is Retrieval-Augmented...<|im_end|>
```

This is the *actual* input the model sees — the W1-07 API's `messages` list is sugar over this rendering. Two consequences:

1. **Prompt templates differ per model family** — the same `messages` produce different tokens on Qwen vs Llama; switching models changes the exact token stream (and therefore behavior at the margins).
2. **Generation stops at the assistant's `<|im_end|>`** — that special token is the stop signal (W1-07's `finish_reason`).

## 4. Special tokens in your own data

When building fine-tuning or eval data (W16-03), never hand-insert special tokens — use the tokenizer's methods:

```python
ids_with_specials = tok("Hello <PAD> world", add_special_tokens=False)["input_ids"]
# "<PAD>" here is just TEXT — four subword tokens, not the PAD token id!
real_pad_id = tok.pad_token_id
```

String `<PAD>` ≠ the reserved id. The framework `padding=True` path is the only safe way to create padding.

## Exercises

1. Print `input_ids` and `attention_mask` for three mixed-length sentences; verify mask sums equal un-padded lengths.
2. Compare padding strategies: time tokenization of 100 mixed-length texts with `padding=True` vs `padding="max_length", max_length=128`. Report tensor sizes and time.
3. Render the same 4-turn conversation with two model families' templates (Qwen + Mistral). List the structural differences (delimiters, system handling, newline conventions).
4. Prove the mask-less failure: compute mean embeddings for the short sentence with and without a mask; measure cosine distance between them.
5. Tokenize 20 texts containing emoji/accents; verify decode(encode(x)) == x for all. Find one that breaks and explain.

## Pitfalls

- **Separating padding from masks** — the mask is part of the padding operation, not an afterthought
- **Hand-writing special tokens in data** — `<PAD>` as literal text trains the model on the *string*, not the protocol
- **Cross-model template assumptions** — Qwen's `<|im_start|>` means nothing to Llama-2's `[INST]` format
- **`token_type_ids` confusion** — some models (BERT) need them for segment pairs; check the model card's expected inputs
- **Padding side** — encoders pad right; some decoders pad left for generation — wrong side shifts positions

## Resources

- HF [padding & truncation guide](https://huggingface.co/docs/transformers/pad_truncation)
- HF [chat templating](https://huggingface.co/docs/transformers/chat_templating) — template language reference
- Qwen2.5 model card — the `<|im_start|>`/`<|im_end|>` convention in context
- W1-01 (parent), W16-03 (template consistency in fine-tuning) — the dependent topics
