# Tokenization & Loaders — Templates, Truncation Audits

**What you'll learn:** the seams where formatted data becomes training
tensors: the chat template application, truncation policy, and the
audit that catches the mangling before the GPU does.

## 1. The template application

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("pinned-model-id")

def tokenize_record(record: dict, max_len: int = 2048):
    full = tok.apply_chat_template(record["messages"],
                                   tokenize=True, add_generation_prompt=False)
    labels = mask_prompts(full, record)     # mask everything before the
    return {"input_ids": full[:max_len],    # final assistant turn
            "labels": labels[:max_len]}
```

| Seam | Failure | Audit |
|---|---|---|
| chat template | wrong special tokens | decode round-trip test |
| masking | loss on prompts | label-coverage check |
| truncation | the answer's tail (citations!) cut | tail-preservation check |

Three seams, three audits — the tokenizer is where formatted data
silently mangles. The decode round-trip is the master audit: decode the
tokenized record and diff against the source text.

## 2. Truncation policy — protect the answer's tail

```python
def truncate_protect_tail(ids: list[int], max_len: int,
                          tail_tokens: int = 300) -> list[int]:
    if len(ids) <= max_len:
        return ids
    head = ids[: max_len - tail_tokens]     # keep the prompt's head
    tail = ids[-tail_tokens:]               # keep the answer's tail
    return head + [tok.eos_token_id] + tail
```

| Truncation | What dies | Verdict |
|---|---|---|
| head-truncate | the system prompt | never |
| tail-truncate | the citations | never — they are the behavior |
| middle-out (head+tail) | the middle context | the honest option |

Citations live at the answer's *end* — naive tail-truncation deletes
exactly the behavior you are teaching. The middle-out policy with a
protected tail is the default; the audit asserts the citation tokens
survive every truncation.

## 3. The loader audit (the four checks)

```python
def audit_loader(loader, tok, n: int = 20):
    for batch in loader.take(n):
        for rec in batch["input_ids"]:
            text = tok.decode(rec)
            assert "###" not in text            # template leakage check
            assert text.count("<|im_start|>") == expected  # structure
            assert tail_intact(rec)             # citations survive
```

| Check | Catches |
|---|---|
| decode round-trip | template/masking bugs |
| structure count | wrong template applied |
| tail integrity | truncation killing citations |
| length distribution | max_len misconfigurations |

The loader audit runs before every training run — five minutes of
checking against hours of training on mangled data.

## Exercises

1. Apply the chat template to 20 records; decode and diff; the
   round-trip must be lossless.
2. Masking drill: visualize the labels for one record; verify only the
   final assistant turn carries loss.
3. Truncation drill: force truncation on a long record; the audit
   asserts the citation tokens survive — the tail-protection rule,
   tested.