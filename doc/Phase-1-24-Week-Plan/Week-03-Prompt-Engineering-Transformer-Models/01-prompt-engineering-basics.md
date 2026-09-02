# 01 — Prompt Engineering Basics

> Week 3 index: [README.md](README.md)

**Session 1 topic:** *Prompt Engineering basics — zero shot, few-shot, chain of thought, prompt chaining, meta prompting, multimodal prompting, and variables in prompts — Python f-strings.*

---

## What you'll learn

- The four core techniques (zero-shot, few-shot, CoT, chaining) and the cost/benefit of each
- Meta prompting and multimodal prompting
- Prompt variables and templating with Python f-strings
- A personal habit: every prompt is a versioned, tested artifact

All examples use the OpenAI-compatible client from Week 1 (file 07); swap `base_url` for any provider or Ollama.

## 1. Zero-shot: ask, with constraints

Zero-shot = instruction only, no examples. It works when the task is common and the instruction is precise. The skill is **being specific about format, role, and boundaries**:

```python
from openai import OpenAI
client = OpenAI()
MODEL = "gpt-4o-mini"

def ask(prompt, system="You are a precise assistant."):
    return client.chat.completions.create(
        model=MODEL, temperature=0,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
    ).choices[0].message.content

print(ask(
    "Classify this support message as BILLING, TECHNICAL, or ACCOUNT. "
    "Reply with exactly one word.\n\n"
    "Message: \"I was charged twice for my subscription this month.\""
))
```

Weak vs strong zero-shot, same task:

```text
Weak:    "Tell me about this ticket: <text>"
Strong:  "You are a support triager. Classify the ticket below into exactly
          one category: BILLING | TECHNICAL | ACCOUNT.
          Rules: If it mentions charges/refunds -> BILLING. If login/permissions -> ACCOUNT.
          Output JSON: {"category": "...", "confidence": "low|medium|high"}.
          If none fit, output {"category": "OTHER"}.

          Ticket: <text>"
```

The strong version fixes format (parseable), removes ambiguity (tie-break rules), and defines failure behavior. **Specificity is the technique.**

## 2. Few-shot: show, don't tell

Add worked examples to pin down format and edge-case behavior:

```python
FEW_SHOT = """Classify each ticket into BILLING, TECHNICAL, or ACCOUNT.

Ticket: "My card was charged after I cancelled."        -> BILLING
Ticket: "App crashes when I upload a photo."            -> TECHNICAL
Ticket: "I want to change my email address."            -> ACCOUNT
Ticket: "Reset link expired in 5 minutes."              -> ACCOUNT
Ticket: "Refund shows pending for 10 days."             -> BILLING

Ticket: "{ticket}"                                      ->"""

print(ask(FEW_SHOT.format(ticket="I cannot upload my invoice to the portal.")))
```

Guidelines:

- 2–5 examples is the sweet spot; more examples = more tokens + diminishing returns
- Examples must be **diverse and cover your edge cases** (include the tricky ones, not just easy wins)
- **Order matters less than you'd hope** but recency helps — put the hardest example near the end
- Examples teach *format* faster than they teach *reasoning* — don't expect 5 examples to add knowledge the model lacks

## 3. Chain of thought: buy reasoning with tokens

Asking the model to reason step-by-step before answering improves accuracy on math, logic, and multi-step classification:

```python
cot_prompt = """Classify the ticket. Think step by step:
1. What does the customer actually want?
2. Which system/component is involved?
3. Which category matches? Output the category on the last line as CATEGORY: <name>

Ticket: "I cancelled last week but my card still shows a pending charge."
"""
print(ask(cot_prompt))
```

- Works because generation conditions on prior tokens — the model "shows its work" and conditions its final answer on that reasoning
- **Cost:** reasoning tokens are billed like any output (file W1-07). Newer models reason natively (`reasoning_effort` param) — for them, explicit CoT prompts are often redundant
- Use CoT for: multi-constraint decisions, math, scoring rubrics. Skip for: simple extraction, format conversion (pure overhead)
- Alternative: hide the reasoning — ask for `{"reasoning": "...", "answer": "..."}` JSON and only surface the answer

## 4. Prompt chaining: pipelines of prompts

One giant prompt doing 5 jobs is brittle. Chain small, single-purpose prompts where each step's output feeds the next:

```python
def summarize(ticket):
    return ask(f"Summarize this ticket in 2 sentences:\n\n{ticket}")

def classify(summary):
    return ask(f"Classify in one word (BILLING|TECHNICAL|ACCOUNT):\n\n{summary}")

def draft_reply(summary, category):
    return ask(f"You are a support agent. Write a 3-sentence reply for this "
               f"{category} ticket:\n\n{summary}")

summary = summarize(ticket)
reply = draft_reply(summary, classify(summary))
```

Benefits: each link is independently testable/swappable (different model per step!), failures are localizable, intermediate outputs are inspectable. Costs: latency stacks, and errors propagate — validate at the seams (is the classification actually one of the three?). LangChain/LangGraph (Weeks 13–14) formalize exactly this pattern.

## 5. Meta prompting: prompts that write prompts

Use the model to generate/improve prompts — draft, critique, rewrite loop:

```python
improve = ask(f"""You are a prompt engineer. Improve this prompt for a support
triage task. Requirements: output strict JSON, handle empty input, handle
non-English text. Return only the new prompt.

Current prompt: {my_prompt}
Recent failures: {failure_notes}""")
```

- The critique pass is the valuable one: "list 5 ways this prompt could be misunderstood" routinely surfaces real bugs
- Guard against drift: generated prompts go through the same test suite as hand-written ones (file 02)

## 6. Multimodal prompting

Text prompts plus images (and later audio) in one message — same structure, mixed content:

```python
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "This is a screenshot of an error dialog. "
                                     "Extract: app name, error code, suggested fix."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ],
    }],
)
```

Prompt principles don't change — be explicit about what to extract and the output format — but add image-specific instructions: "read all text in the image", "if the image contains no error dialog, reply NO_DIALOG". Full multimodal work is Weeks 7–9; today, know the shape.

## 7. Variables: prompts as parameterized functions

Week 1's f-strings are your templating engine. Three hygiene rules:

```python
def triage_prompt(ticket: str, categories: list[str], few_shot: str) -> str:
    return f"""Classify the support ticket.

Categories: {', '.join(categories)}
Rules: exactly one category; if ambiguous, choose ACCOUNT and set confidence=low.
{few_shot}

Return JSON: {{"category": "<one of {categories}>", "confidence": "low|medium|high"}}

Ticket:
{ticket!r}
"""
```

1. **Escape braces** in literal JSON examples (`{{` `}}`) — silent bugs otherwise
2. **Delimit untrusted content** (`{ticket!r}`, or wrap in `<ticket>...</ticket>`) — see file 02 on injection
3. **Validate after render** — assert the prompt still fits the context budget and contains no `None`

When templates outgrow f-strings (dynamic few-shot selection, partial templates), that's Week 14's LangChain `PromptTemplate` — same concepts, more machinery.

## Exercises

1. Take Week 2's ticket-classification mini-eval (20 examples). Write zero-shot, few-shot, and CoT versions; score all three. Report accuracy vs token cost per version.
2. Build a 3-link chain: summarize → extract action items (JSON list) → draft email. Break step 2 deliberately (bad JSON out) and add validation+retry at that seam.
3. Meta prompt: have the model critique your best triage prompt ("5 ways this could be misunderstood"), apply 2 suggestions, re-run the eval. Did it improve?
4. Multimodal: screenshot any app error dialog; prompt for structured extraction. Test with a *non-dialog* image — does it hallucinate fields?
5. Make `triage_prompt` crash-safe: empty ticket, 10k-char ticket, and a ticket containing `{{category}}` — what happens to each today, and what should happen?

## Pitfalls

- **Vague instructions** ("be helpful") vs operational ones (rules + format + fallback)
- **Examples that all share one quirk** — the model learns the quirk, not the task
- **CoT everywhere** — token bloat on tasks that don't need it
- **Chains without seam validation** — one malformed JSON poisons every downstream step
- **`{}` collisions in f-strings** — JSON examples inside f-strings need doubled braces
- **One prompt, five jobs** — split it

## Resources

- OpenAI, [Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) — the six strategies
- Anthropic, [Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) — XML-tag structuring ideas
- Wei et al., *Chain-of-Thought Prompting* (2022) — the original paper
- [LangChain hub prompts](https://smith.langchain.com/hub) — read production prompts for common tasks
