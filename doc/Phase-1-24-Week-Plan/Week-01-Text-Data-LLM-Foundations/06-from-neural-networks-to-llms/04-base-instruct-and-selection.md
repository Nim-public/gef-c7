# 06.4 — Base vs Instruct & Model Selection

> Subfolder index: [README.md](README.md) · Parent: [../06-from-neural-networks-to-llms.md](../06-from-neural-networks-to-llms.md)

---

## What you'll learn

- The base-vs-instruct behavior difference — run as a controlled experiment
- Model selection as a repeatable protocol (card reading → shortlist → harness → pin)
- The model-card fields that matter for each selection decision

## 1. The controlled experiment

Same architecture, same size — different post-training:

```python
from transformers import pipeline

base = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B")
instruct = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")

prompt = "What is RAG in AI?"
print("BASE:", base(prompt, max_new_tokens=80)[0]["generated_text"])
print("INSTRUCT:", instruct(prompt, max_new_tokens=80)[0]["generated_text"])
```

Expected behavior difference:

| Aspect | Base | Instruct |
|---|---|---|
| continues text like autocomplete | ✅ | reframes as an answer |
| may ask itself questions | ✅ | no |
| follows "answer in one paragraph" | ignores it | complies |
| stops when done | rambles until token cap | emits end-of-turn token |

The mechanism (W16-03/04 + W1-07): SFT + preference tuning taught the instruct model the *assistant format* and the stopping behavior. Base models are next-token machines — magnificent autocomplete, terrible assistants.

The base model's legitimate uses: further training research, style imitation via few-shot, distillation data generation (E1-03). None of them are "answering user questions."

## 2. The behavior lab (run it, don't trust the table)

```python
QUESTIONS = [
    ("factual", "What is RAG in AI?"),
    ("instruction", "List 3 uses for vector databases."),
    ("stopping", "Tell me about pandas. Stop after two sentences."),
    ("format", "Reply with JSON: {\"answer\": string}"),
]

for kind, q in QUESTIONS:
    for name, pipe in [("base", base), ("instruct", instruct)]:
        out = pipe(q, max_new_tokens=100, do_sample=False)[0]["generated_text"]
        print(f"{name:9} {kind:12} -> {out[-100:]!r}")
```

Four behavior dimensions probed: factuality, instruction-following, stopping, format compliance. Score each cell pass/fail by hand — the completed grid *is* the base-vs-instruct difference, on your prompts.

## 3. Model selection protocol (W2-01's, deepened)

1. **Card reading** — license, size, context window, known limitations
2. **Shortlist 3** — same family/size class, different post-training
3. **Behavior grid** — §2's four dimensions on your prompts
4. **Harness run** — the W4-05/W11-06 eval on held-out cases
5. **Pin** — revision, tokenizer, template; record in the manifest (E8-01)

The checklist per model card:

| Field | Question |
|---|---|
| License | commercial use allowed? attribution needed? |
| Parameters | memory math (fp16 ≈ 2 B/param) |
| Context window | ≥ your longest prompt? |
| Training data note | domain coverage hints |
| Known limitations | what will it fail at? |
| Chat template | compatible with your serving path? |

## 4. The routing implication (W15-04 preview)

The behavior grid feeds the router: classes where instruct-0.5B passes → SLM path; classes where it fails → frontier. The grid *is* the router's training data, collected cheaply — and re-run whenever you consider a model swap (E8-01's registry keeps both candidates pinned).

## Exercises

1. Behavior grid: 4 question types × base/instruct × 3 temperatures — complete the 24-cell pass/fail grid; note the temperature sensitivity differences.
2. Card-to-reality: pick a model card claim ("follows instructions well"); design the 10-case test that would verify it; run it.
3. Stopping behavior: measure how many tokens each model burns on "Tell me about pandas. Stop after two sentences." — quantify the stopping difference.
4. Template sensitivity: same question, rendered with Qwen's template vs Mistral's — on an instruct model, compare answers. What changed?
5. Write the selection decision for your capstone: model, revision, template — with the behavior grid attached as evidence.

## Pitfalls

- **Base model in an application** — it will ramble; the failure looks like "the model is dumb" but it's a selection bug
- **Template mismatch** — rendering an instruct model's prompt without its chat template degrades it to near-base behavior
- **Size worship** — a 0.5B with the right post-training beats a 7B base on assistant tasks (file 04's experiment)
- **Sampling settings ignored in comparisons** — `do_sample=True` on one arm and greedy on the other invalidates the grid (W15-03's freeze rule)
- **Revision drift after selection** — the model updates upstream and behavior shifts; pin the revision or re-run the grid (W2-01)

## Resources

- Qwen2.5 model cards (base vs instruct) — the post-training deltas documented
- W16-03/04 (how the instruct behavior is trained), W2-01 (cards), W15-04 (routing) — composed here
- [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) — shortlist generator, with the E10-01 caveats
