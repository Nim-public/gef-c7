# 07 — LLM Concepts & Demos: Chat, Sampling, Logprobs, Alignment

> Week 1 index: [README.md](README.md)

**Session 2 topic:** *LLM Concepts & Demos: Chat completions, multi-turn chats, temperature & sampling, log probabilities, autoregressive generation, pre-training, fine-tuning, RLHF alignment.*

---

## What you'll learn

- The chat-completions call: messages, roles, and why state is *your* job
- Multi-turn conversations as list management
- Sampling controls: temperature, top_p, max tokens, stop sequences
- What log probabilities are and three real uses for them
- How pre-training → SFT → RLHF shapes model behavior
- Practical demos runnable on any OpenAI-compatible endpoint

## 0. Setup

```powershell
pip install openai tiktoken python-dotenv
```

```python
# .env  (never commit this file)
# OPENAI_API_KEY=sk-...
```

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()      # reads OPENAI_API_KEY from the environment

MODEL = "gpt-4o-mini"  # any chat model on your endpoint
```

Every OpenAI-compatible provider (Azure OpenAI, OpenRouter, Together, local Ollama/LM Studio) speaks this same shape — only `base_url` and model names change.

## 1. Chat completions: stateless by design

```python
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a concise teaching assistant."},
        {"role": "user", "content": "Explain temperature in one paragraph."},
    ],
)
print(resp.choices[0].message.content)
print(resp.usage)     # prompt_tokens / completion_tokens — billable truth
```

Three roles:

| Role | Meaning |
|---|---|
| `system` / `developer` | standing instructions: persona, rules, format |
| `user` | the human's turn |
| `assistant` | the model's previous turns |

**The server remembers nothing.** "Multi-turn" means *you* resend the whole conversation every call:

```python
history = [
    {"role": "system", "content": "You are a concise teaching assistant."},
    {"role": "user", "content": "What is tokenization?"},
]

def chat(user_msg: str) -> str:
    history.append({"role": "user", "content": user_msg})
    resp = client.chat.completions.create(model=MODEL, messages=history)
    reply = resp.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply

print(chat("Explain it in 2 sentences."))
print(chat("Now give one example."))     # model 'remembers' — because we resent history
```

Practical consequences you'll manage all program long:

- **Context window is shared** by history + new input + output → trim/summarize old turns in long chats
- **Cost grows quadratically-ish** with conversation length (every call re-pays for all prior tokens) → prompt caching exists for this (Week 15)
- History is just a list — you can inject, edit, or drop turns programmatically (that's what agent frameworks do)

## 2. Sampling controls

The model outputs a **probability distribution over the next token**. Sampling settings shape the pick:

| Parameter | What it does | Typical use |
|---|---|---|
| `temperature` | flattens (→1) or sharpens (→0) the distribution | 0–0.3 factual/extraction; 0.7–1 creative |
| `top_p` | nucleus: sample only from tokens covering p probability mass | keep 0.9–1; tune *either* temp or top_p |
| `max_tokens` / `max_completion_tokens` | hard output cap | always set in production |
| `stop` | stop sequences | cut output at `\n\n`, `Observation:` |
| `seed` | best-effort reproducibility | debugging/evals |
| `n` | number of completions | generating variants |

**Demo: temperature comparison**

```python
question = "Give one creative name for a vector-database startup."

for temp in (0.0, 0.7, 1.2):
    outs = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=temp, n=3,
    )
    print(temp, "->", [c.message.content.strip()[:40] for c in outs.choices])
```

At 0 the three outputs converge (near-deterministic — good for evals); at 1.2 they diverge wildly. **Production default: low temperature unless you can measure that creativity helps.**

## 3. Log probabilities

`logprobs=True` returns the model's per-token confidence; `top_logprobs=k` adds the top-k alternatives per position.

```python
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Is 17 prime? Answer yes or no."}],
    logprobs=True,
    top_logprobs=5,
)
content = resp.choices[0].logprobs.content
for tok in content[:4]:
    print(f"{tok.token!r:10} logprob={tok.logprob:.3f}  prob={2.718281828 ** tok.logprob:.4f}")
    for alt in tok.top_logprobs:
        print(f"    alt {alt.token!r:10} prob={2.718281828 ** alt.logprob:.4f}")
```

What this buys you (all used later in the program):

1. **Confidence signal** — low probability of the emitted answer = candidate for "I'm not sure" routing or human review
2. **Zero-shot classification without a classifier** — compare the model's probability of `"Positive"` vs `"Negative"` (vs training a model like file 05)
3. **Guardrails & routing** — branch on whether the top tokens form a valid enum value (Weeks 5, 11)

Caveats: probabilities are post-sampling-recipe, calibrated only loosely; some endpoints don't expose them. **Demo: logprob zero-shot classifier**

```python
def classify_zero_shot(text: str) -> dict:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Classify sentiment. Answer with exactly one word: Positive or Negative."},
            {"role": "user", "content": text},
        ],
        temperature=0,
        logprobs=True,
        top_logprobs=5,
    )
    toks = resp.choices[0].logprobs.content
    for t in toks:
        words = {a.token: 2.718281828 ** a.logprob for a in t.top_logprobs}
        if "Positive" in words or "Negative" in words:
            return {k: v for k, v in words.items() if k in ("Positive", "Negative")}
    return {}

print(classify_zero_shot("The battery life is amazing but the screen scratches easily."))
```

## 4. Autoregressive generation — the loop, made visible

The API hides it, but generation is a loop (file 06):

```
tokens = tokenize(prompt)
while not done:
    next_id  = argmax-ish(sample(model(tokens)))     # one distribution, one pick
    tokens.append(next_id)
    done = next_id == EOS or len(tokens) >= max_tokens
return detokenize(tokens)
```

Consequences worth knowing now:

- **Errors compound**: one bad token poisons the context for all later tokens
- **Cost scales with output length**: each new token re-runs the model over the whole sequence (KV caching makes this cheap in compute, but you still pay per token)
- **Streaming exists** to hide latency: `stream=True` yields chunks as they're generated — used in every chat UI

```python
stream = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Count from 1 to 10."}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

## 5. Pre-training → SFT → RLHF: where the behavior comes from

| Stage | Data | Signal | Produces |
|---|---|---|---|
| **Pre-training** | trillions of tokens of web/code | next-token cross-entropy | base model: knowledge + fluency (file 06) |
| **Supervised fine-tuning (SFT)** | ~10⁴–10⁶ curated (instruction → answer) demos | same loss, on assistant turns only | instruction follower |
| **Preference tuning (RLHF / DPO)** | human (or AI) rankings between candidate answers | reward model / preference loss | helpful, safe, refusal-calibrated assistant |

Why you care at the application layer:

- The assistant persona lives in post-training — a strong `system` message *steers* it but doesn't rebuild it
- Alignment is why models refuse, hedge, and moralize; prompt design (Week 3) and guardrails (Week 5) work *with* or *around* it
- "Fine-tuning" in Week 16 = doing SFT/LoRA on *your* data; the mechanism you saw in file 05/06 is identical

## Exercises

1. Build a terminal chat loop: read input, append to history, print replies; add `/reset`, and print `resp.usage` after each call. Watch token cost grow with turns.
2. Generate one summary at temperatures 0, 0.5, 1.0 (n=5 each). Rate output consistency; pick a default for a production summarizer and justify it.
3. Extend the zero-shot classifier to 4 classes (positive/negative/mixed/other) using top-logprob comparisons. Where does it break?
4. Estimate cost: tokenize a 10-turn chat history with tiktoken and compute price at your endpoint's $/1M-token rates. Then halve history with a summary and recompute.
5. Write `truncate_history(messages, max_tokens)` that keeps the system message + most recent turns under a token budget.

## Pitfalls

- **Forgetting you must resend history** — "the model forgot" almost always means the client dropped turns
- **Temperature 1 everywhere** — creative variance in data pipelines is a bug source
- **Trusting logprobs as calibrated confidence** — treat as a weak signal, validate empirically
- **`max_tokens` hits silently** — check `finish_reason == "length"`, not just empty content
- **Secrets in code** — keys in env vars/`.env`, never in git

## Resources

- [OpenAI API reference — Chat Completions](https://platform.openai.com/docs/api-reference/chat) (logprobs, sampling params)
- OpenAI Cookbook: *How to use log probabilities*, *Handling rate limits*
- Hugging Face blog: *Illustrating RLHF* / *RLHF book (summarized)*
- Karpathy, *Intro to Large Language Models* (1h talk) — the cleanest stage-setting video
