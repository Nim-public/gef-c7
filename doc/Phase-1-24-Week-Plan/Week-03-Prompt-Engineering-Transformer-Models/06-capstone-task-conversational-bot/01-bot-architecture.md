# 06.1 — Bot Architecture

> Subfolder index: [README.md](README.md) · Parent: [../06-capstone-task-conversational-bot.md](../06-capstone-task-conversational-bot.md)

---

## What you'll learn

- The ChatBot assembly: constitution, history ownership, trimming, usage logging
- The reply loop with the three failure paths
- The observability hooks from day one

## 1. The assembly

```python
from pathlib import Path
import json, time, tiktoken
from openai import OpenAI

client = OpenAI()
SYSTEM = Path("prompts/system.md").read_text(encoding="utf-8")

class ChatBot:
    def __init__(self, model="gpt-4o-mini", max_history_tokens=3000):
        self.messages = [{"role": "system", "content": SYSTEM}]
        self.model, self.budget = model, max_history_tokens
        self.enc = tiktoken.get_encoding("o200k_base")

    def reply(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        self._trim()
        resp = client.chat.completions.create(model=self.model, temperature=0.3,
                                              messages=self.messages)
        reply = resp.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        self._log(resp.usage)
        return reply

    def _trim(self):
        total = self._count()
        while total > self.budget and len(self.messages) > 2:
            total -= self._count([self.messages[1]])
            self.messages.pop(1)

    def _count(self, msgs=None):
        return sum(len(self.enc.encode(str(m["content"]))) for m in (msgs or self.messages))

    def _log(self, usage):
        with open("data/bot_runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "usage": usage.model_dump(),
                                "turns": len(self.messages)}) + "\n")
```

The assembly rules from W3-02: system at index 0 (never trimmed), trimming to budget, every call logged with usage. The `_log` hook is the W10-04 instrumentation — the file feeds W16-01's eval growth.

## 2. The failure paths

| Failure | Handling |
|---|---|
| provider error (429/5xx) | retry with backoff (W15-01), then a user-facing "try again" |
| content_filter finish | canned response, logged (W15-02) |
| empty user input | explicit "please say more" — never a model call |
| over-budget session | summarize-and-restart with user notice |

Each path is testable (file 03's battery) and each returns a *user-appropriate* message — never a stack trace.

## 3. The demo-readiness checklist

- [ ] 6+ turn coherent conversation (transcript committed)
- [ ] constitution adherence verified at turns 1, 10, 20
- [ ] trimming proven (token counts logged per turn)
- [ ] refusal + injection behaviors demonstrated
- [ ] usage/cost visible in the log

## Exercises

1. Add the four failure paths with tests; verify each user-facing message.
2. The observability upgrade: log per-turn token counts AND the running session cost — plot cost vs turns.
3. Persona persistence: 20-turn conversation; check tone consistency at turns 5/10/20 — re-anchor if drifted (W3-02 §2).
4. Multi-session: persist history to disk; resume the same conversation after restart — verify continuity.
5. The cost forecast: extrapolate your session cost curve to your capstone's expected traffic — the E8-03 ledger's first real row.

## Pitfalls

- **History in a global variable** — two users share one brain; scope per session (W10-02)
- **Trim boundary off-by-one** — popping the system message or the current turn
- **Unbounded logging** — the log is the product's memory; rotate it
- **Error paths untested** — the happy path always works in demos; the failure paths are the product
- **Temperature as a global constant** — different turns want different settings; make it per-call configurable

## Resources

- W3-02 (constitution), W15-01 (limits/retries), W10-04 (instrumentation) — composed here
- W11-01 (the SDK edition of this same bot) — the comparison target
