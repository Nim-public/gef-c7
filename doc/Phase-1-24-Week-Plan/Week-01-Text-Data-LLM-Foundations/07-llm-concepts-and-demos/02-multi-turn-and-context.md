# 07.2 — Multi-Turn & Context Management

> Subfolder index: [README.md](README.md) · Parent: [../07-llm-concepts-and-demos.md](../07-llm-concepts-and-demos.md)

---

## What you'll learn

- History as state you own — trimming, summarization, re-injection
- Per-session cost curves: why long chats get expensive quadratically
- The context-management toolkit (the W10-05 fitter, chat edition)

## 1. Why cost grows super-linearly

Each call resends the full history:

```python
# turn k: input tokens ≈ base + Σ(history lengths so far) + new turn
# total session input ≈ Σ over turns  →  quadratic-ish in conversation length
```

With 100-token turns and no trimming, a 20-turn session re-sends ~200k cumulative input tokens — most of it repeated history. The fixes: trimming, summarization, and (server-side) prefix caching (W15-04).

## 2. The three memory operations

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")

def count(messages) -> int:
    return sum(len(enc.encode(str(m.get("content", "")))) for m in messages)

def trim(messages, budget=3000, keep_system=True):
    """Drop oldest non-system turns until under budget."""
    while count(messages) > budget and len(messages) > (2 if keep_system else 0):
        messages.pop(1 if keep_system else 0)
    return messages

def summarize_older(messages, keep_last=4):
    """Replace all but the last few turns with a compressed recap."""
    old, recent = messages[:-keep_last], messages[-keep_last:]
    recap = client.chat.completions.create(model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content":
                   f"Summarize this conversation for context continuity:\n"
                   f"{json.dumps(old, default=str)[:8000]}"}]).choices[0].message.content
    return [{"role": "system", "content": SYSTEM},
            {"role": "system", "content": f"Conversation so far: {recap}"}] + recent
```

Trimming loses information; summarization keeps the gist at the cost of one extra call; re-injection pins critical facts (user id, decisions) so they survive both. The three compose: trim aggressively, summarize the middle, re-inject the essentials.

## 3. Re-injection (what must never be trimmed away)

| Fact | Strategy |
|---|---|
| user's account id / key decisions | re-inject into every user turn's header |
| active task state | scratchpad (W10-02), always included |
| preferences | core memory (E9-01), part of system |
| everything else | summarizable |

```python
def user_turn(question, context_facts):
    header = "Known context: " + "; ".join(context_facts) if context_facts else ""
    return f"{header}\n\n{question}" if header else question
```

## 4. The session cost curve (measure it)

```python
import matplotlib.pyplot as plt

costs = []
for k in range(1, 21):
    msgs = build_history(k)                     # k turns of ~100 tokens each
    costs.append(count(msgs) * PRICES["in"] / 1e6)
plt.plot(range(1, 21), costs); plt.xlabel("turn"); plt.ylabel("cumulative $ input")
```

The curve you'll see is the argument for trimming: without management, cost/turn grows linearly and cumulative cost quadratically. With trimming at a fixed budget, it plateaus.

## Exercises

1. Build the 3-operation toolkit; run a 30-turn simulated chat (scripted turns) with each strategy alone — plot final context size and information retention (can the agent still answer turn-3 facts?).
2. Retention probe: after trimming, ask about a fact from a dropped turn — measure how often the agent invents vs admits (W5-04's refusal discipline).
3. Summarization quality: compare the recap against the original 16 turns with a checklist (names, decisions, numbers) — what does summarization reliably lose?
4. Cost curve: plot cumulative cost for raw / trimmed / summarized strategies over 30 turns (E8-03's ledger, week-1 edition).
5. Hybrid design: trim + summarize + re-inject the top-5 facts — measure retention vs the other strategies at the same budget.

## Pitfalls

- **Trimming the system prompt** — the constitution vanishes; always keep index 0 (the code above guards it)
- **Summarizing away commitments** — "I'll send the report Friday" is a fact, not flavor; extract commitments before compressing
- **Unbounded session ids** — every session grows a record; expire old sessions (E9's decay)
- **Assuming the model remembers the summary** — the recap is context, not memory; test retrieval from it
- **Cost measured only per call** — cumulative session cost is what the user pays; track it per session id (E8-03)

## Resources

- W1-07 parent, W10-02/05 (memory + budgets), W15-04 (prefix caching — why stable prefixes matter) — composed here
- E9 (memory tiers) — the full system this file's operations belong to
