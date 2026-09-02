# 04 — RAG Chatbot + Responsible-AI Guardrails

> Week 5 index: [README.md](README.md)

**Session 2 topics:** *Building RAG chatbot · Responsible AI: Guardrails.*

---

## What you'll learn

- The RAG-chatbot assembly: Week 3's bot skeleton + Week 5's retriever
- The guardrail sandwich: input checks, generation constraints, output validation
- Which guardrails are cheap/always-on vs expensive/gated
- How "responsible AI" becomes concrete engineering, not a slide

## 1. Architecture: the bot you already built, plus retrieval

```
user turn ─► [input guardrails] ─► [query rewrite/expand] ─► retriever (W5-03 stack)
                                                                     │ top-5 + citations
             ┌───────────────────────────────────────────────────────┘
             ▼
   grounded generation (W4-01 prompt, W3-02 system constitution)
             ▼
   [output guardrails: citation check, schema, refusal detection] ─► user
```

The bot from Week 3's task already has: system prompt constitution, history trimming, tests. This week adds the retriever call per turn and the guardrail layers.

```python
def turn(bot: ChatBot, user_text: str) -> str:
    ok, reason = input_guards(user_text)          # §2
    if not ok:
        return reason                             # refuse *before* any model call
    hits = retriever(user_text, k=5)              # fused + reranked (W5-03)
    if not hits or hits[0]["rerank_score"] < THRESH:
        return "I don't have that information in my knowledge base."
    context = assemble_context(hits)              # W4-01
    answer = bot.reply_with_context(context, user_text)
    return output_guards(answer, hits)            # §3
```

## 2. Input guardrails (cheap, always-on)

| Guard | How | Catches |
|---|---|---|
| **Injection screening** | W3-02 battery + regex for "ignore previous/system prompt/exfiltrate" phrasing | naive hijacks |
| **Topic scope** | LLM classifier or the bot's own refusal (cheaper: classifier) | off-domain abuse |
| **PII minimization** | W2-02 NER + W1-02 regex *before* anything leaves the process | sending customer PII to APIs |
| **Length/rate caps** | max chars/turn, max turns/min | cost abuse, context stuffing |

Design rule: input guards must be *fast and dumb* (regex + one small classifier). Anything expensive goes post-retrieval.

## 3. Output guardrails: trust, then verify

The generation step is constrained by the prompt; the output step *verifies* the constraint held:

```python
CITATION_RE = re.compile(r"\[doc:[^\]]+\]")

def output_guards(answer: str, hits: list[dict]) -> str:
    cited_ids = set(CITATION_RE.findall(answer))
    valid_ids = {h["id"] for h in hits}
    if cited_ids - valid_ids:
        return regenerate_with_warning(answer, hits)   # cited a chunk we didn't give it
    if not cited_ids and needs_citations(answer):
        return "I found related material but can't confirm the specifics. " + \
               "Could you rephrase?"
    return answer
```

Additional output checks by application: JSON schema validation (production: *never* trust prose where you need structure), banned-content filter (toxicity/profanity classifier or API), refusal detection (did we *want* a refusal and get an answer?), and **groundedness spot-checks** (does the answer's entity set ⊆ context's? — a cheap programmatic faithfulness proxy).

## 4. Responsible AI, concretely

The session phrase maps to four engineering practices:

1. **Grounding & citations** — every factual claim traceable to a chunk (the citation contract is your audit trail)
2. **Refusal competence** — the bot must say "I don't know / not in my scope" *reliably*; test it (5 no-answer queries, file W4-01)
3. **Privacy** — PII scrubbing on input, permission-filtered retrieval (W5-03 prefilter), no secrets in context (W3-02)
4. **Human escalation** — low confidence (rerank score, logprobs) or explicit user ask → hand off to a human, don't bluff. Week 11 formalizes human-in-the-loop; the *hook* is a `confidence` field you compute today

Guardrails are products of *measurement*: log every guardrail trip (input rejected, citation missing, low-confidence escalation) as structured events — that log is your Week 16 eval dataset and your incident review source.

## Exercises

1. Assemble the full `turn()` pipeline on your Week 4 engine. Latency breakdown per stage — where does the p95 go? Can you stay under 3 s end-to-end?
2. Guardrail battery: 10 malicious/off-domain inputs (injection, competitor questions, PII-in, prompts inside documents). Record each trip vs pass. One miss? Fix or document.
3. Refusal reliability: 5 no-answer questions × 3 phrasings each. Does the "I don't have that information" escape fire 15/15? If not, which stage betrays you (retriever returning junk vs model ignoring the rule)?
4. Citation validator: regenerate 10 answers with `temperature=0.7` (instead of 0) and count invalid citations. Write the validator's regeneration policy (retry? strip? refuse?).
5. Confidence hook: combine rerank score + answer logprobs (W1-07) into one `confidence ∈ {low, med, high}`. Set the escalation threshold so that ~1 in 10 real questions escalates — justify the number.

## Pitfalls

- **Guardrails only on input** — outputs need equal treatment; the model is the least controllable component
- **Silent fallbacks** — a guardrail that quietly rewrites answers hides incidents; log everything
- **Over-blocking** — 30% input rejection is a broken product; track trip rates per guard
- **Citations as decoration** — if nothing validates them, they're hallucinated links with better formatting
- **Testing guards one at a time** — compose them; interactions (PII-scrub then retrieve then validate) are where bugs live

## Resources

- OpenAI & Anthropic safety best practices (moderation endpoints, refusal design)
- NeMo Guardrails / Guardrails-ai / `llm-guard` — open-source guardrail frameworks worth reading even if you hand-roll
- OWASP LLM Top 10 (W3-02's resource — the RAG-specific risks: LLM01 injection, LLM06 sensitive disclosure)
- Anthropic Engineering, *Reducing hallucinations* — grounding techniques aligned with this file
