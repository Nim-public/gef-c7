# 05 — The Six Levers: Pre-training, RLHF, RAG, Agents, Optimization, Fine-tuning

> Week 3 index: [README.md](README.md)

**Session 2 topic (revision):** *Differences Between Techniques — Pre-training, RLHF / Making an Instruct Model, RAG, Agents/Tools, Optimisation Techniques and Fine-Tuning & Distillation.*

---

## What you'll learn

One decision framework for the question you'll be asked in every capstone review: **"why not just fine-tune?"** — by understanding what each of the six techniques actually changes, what it costs, and when it's the right lever.

## 1. What each technique changes

The same question underlies all six: *the model gave a wrong answer — which part of the stack do you fix?*

```
                    ┌─ knowledge ─┐  ┌─ behavior ─┐  ┌─ output ─┐
pre-training        │█████████████│  │            │  │          │   new foundation model
RLHF / instruct     │             │  │████████████│  │          │   helpful assistant format
RAG                 │████████     │  │  (steered) │  │          │   facts it never had
agents/tools        │  (fetched)  │  │  (steered) │  │██████    │   actions, real data
optimization        │             │  │            │  │██████████│   speed/cost of same quality
fine-tuning         │████         │  │████████    │  │          │   style, format, narrow skills
distillation        │             │  │            │  │          │   small model imitates big
```

| Lever | Mechanism | Changes | Cost | Latency to change |
|---|---|---|---|---|
| **Pre-training** | next-token on trillions of tokens | knowledge, language ability | $M–$B, cluster of GPUs | months |
| **RLHF / instruct tuning** | SFT demos + preference rankings | persona, helpfulness, refusals | $100k+ (labs) | months |
| **RAG** | retrieve documents into context | *facts available at ask-time* | engineering effort | **minutes** (add a doc) |
| **Agents/tools** | LLM calls tools, loops on results | *capabilities* — read/write, compute | engineering effort | days |
| **Optimization** | caching, batching, routing, quantization | same quality, cheaper/faster | eng + infra | days |
| **Fine-tuning** | gradient updates on your examples | style, format, narrow skill | $10–$10k, hours–days | days |
| **Distillation** | train small model on big model's outputs | capability density per dollar | moderate | weeks |

## 2. The confusions this table kills

### "RAG vs fine-tuning" — they fix different problems

- Model says *"our refund policy is 30 days"* but your policy is 5 days → **RAG**. Fine-tuning teaches facts poorly and they *rot* — policy changed yesterday; your fine-tune is already wrong.
- Model answers correctly but in the wrong format, wrong persona, ignores your JSON schema → **fine-tuning** (or better prompting — try that first!).
- Rule: **new/numerous/changing facts → RAG. Stable style/format/behavior → fine-tuning.** They compose (Week 16 does both).

### "RLHF vs prompt engineering"

Same target (behavior), opposite costs. RLHF rewires the weights — that's *why* the model refuses things, hedges, and follows your system prompt at all (file 07, Week 1). Prompt engineering steers the already-aligned model. You will never run RLHF; you benefit from it every call.

### "Agents vs RAG"

RAG is one *pattern* an agent can use: retrieve → ground → answer, fixed pipeline. An agent (Weeks 10–14) *decides at runtime* which tools to call, in what order, looping until done — retrieval might be tool #3 of 5. RAG = reliable pipeline; agents = flexible but less predictable. Scope doc (Week 1) should already say which your capstone needs.

### "Optimization" is not model quality

Same model, same answers — cheaper/faster. The Week 15 catalog, previewed: prompt caching, KV cache, continuous batching (vLLM/SGLang), routing easy prompts to small models (RouteLLM-style), quantization. A 10× cost cut with identical outputs beats a 2% quality gain from a bigger model.

### "Distillation" is fine-tuning's cousin

Train a small model to imitate a large teacher (outputs, not weights). You get ~90% of the capability at ~10% of the serving cost. Also the honest description of many "small" open models: they were distilled from bigger ones.

## 3. A decision procedure for your capstone

Ask, in order:

1. **Does the needed knowledge change often, or live in your documents?** → RAG (Weeks 4–6)
2. **Does the task need actions on real systems** (DBs, files, APIs)? → agents/tools (Weeks 10–14)
3. **Is the model's default style/format/behavior off?** → prompt engineering first (this week), fine-tune only if prompting plateaus (Week 16)
4. **Is it too slow/expensive at volume?** → optimization (Week 15), then distillation (Week 16)
5. **Is the task truly impossible without new general knowledge?** → you're a lab; you're not doing this. (Nobody in this program picks lever 1.)

The default path for 90% of enterprise projects — and likely yours: **good prompting → RAG → agents → optimize → maybe fine-tune.** In that order, each only if the previous plateaued.

## 4. One worked case

*"Capstone: assistant answering questions over 5,000 internal PDFs, must cite sources, budget ₹0 GPU."*

- Knowledge lives in PDFs, changes monthly → **RAG** (not fine-tuning — see above)
- Answers must follow a citation format → **prompting** (system prompt + few-shot output contract, file 02)
- Users ask "compare policy A with B" → later add **agent** layer: multi-retrieve, synthesize (Week 13)
- P95 latency 12s, too slow → **optimization**: cache system prompt, route chit-chat to an SLM (Week 15)
- Tone must match company voice across 4 document types → **fine-tune** a small model on 500 styled answers, only if prompting failed (Week 16)

## Exercises

1. For your own capstone scope doc, fill the six-row table: which levers apply, which you've ruled out, and why — one line each. This becomes part of your mentor pitch.
2. Fine-tune-the-facts trap: write down an example where fine-tuning on your documents would silently fail six months later. What would RAG do instead?
3. Take one bad model output from your Week 2 mini-eval. Diagnose: knowledge gap, behavior gap, or output-format gap? Which lever fixes it?
4. Argue the opposite: find one capstone scenario where fine-tuning beats RAG (hint: style transfer over 50k examples; no facts involved).
5. Cost sketch: prompting+RAG (per-query retrieval+API) vs fine-tuned SLM (flat serving cost) at 1M queries/month, 2k tokens each. Where's the crossover?

## Resources

- Lewis et al., *RAG* (2020) — the original argument for retrieval over parametric memory
- Ouyang et al., *InstructGPT* — the RLHF/SFT story in one paper (file W1-07's source)
- Anthropic & OpenAI fine-tuning guides — what vendors expect you to fine-tune *for*
- Gekhman et al., *Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?* — the evidence behind "facts → RAG"
- [Prompting vs RAG vs fine-tuning decision guides](https://www.anthropic.com/engineering) (several posts under Anthropic Engineering)
