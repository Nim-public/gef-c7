# 01.1 — LLM Limitations

> Subfolder index: [README.md](README.md) · Parent: [../01-rag-fundamentals.md](../01-rag-fundamentals.md)

---

## What you'll learn

- The five limitations demonstrated on a real model — each with a reproducible test
- Why fine-tuning fixes behavior but not facts (the rot mechanism)
- The provenance gap: why "it said so" isn't acceptable in enterprise

## 1. The five limitations, demonstrated

```python
from openai import OpenAI
client = OpenAI()

TESTS = {
    "cutoff":      "What is the latest version of Django?",
    "private":     "What is AcmeCloud's internal refund SLA?",
    "hallucination": "List the 5 authors of the Transformers paper.",
    "provenance":  "Which document states the 5-day refund window?",
    "window":      "Summarize all 400 pages of our employee handbook.",
}

for name, q in TESTS.items():
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content": q}])
    print(f"=== {name} ===\n{r.choices[0].message.content[:200]}\n")
```

Each test demonstrates one limitation on *your* model, *today*. The results become the motivation slide for RAG — evidence, not assertion (the W1-08 pattern applied to architecture).

## 2. Why fine-tuning doesn't fix facts

```python
# the rot mechanism, illustrated:
# Day 1:  fine-tune on "refund SLA = 5 days" (from the November policy)
# Day 30: policy changes to 3 days
# Day 31: the model still says 5 days — and you can't tell WHICH training
#         example taught it without tracing every gradient
```

Fine-tuning distributes facts across billions of weights: no provenance, no update path, no audit. RAG stores facts *once*, in a retrievable document — update the document, the answer updates (W3-05's argument, now with the mechanism).

## 3. The provenance gap

Enterprise answers need: who said it, where, when, with what authority. A closed-book LLM provides none. RAG's citation contract ([doc:id], W4-01) provides all of it — the property that makes RAG the enterprise default (W4-01 §5's table).

## Exercises

1. Run the five limitation tests on your model; document each failure with the exact output — the evidence file for your RAG motivation slide.
2. The rot experiment: fine-tune a small model on 20 "facts"; change 5 of them; re-test — quantify the stale-answer rate (the W3-05 Gekhman argument, reproduced).
3. Provenance audit: for 10 answers your current bot gives, check — can a user verify each claim? Count the verifiable fraction.
4. The window test: measure your model's context limit; compute what fraction of your corpus fits — the number that justifies retrieval over pasting.
5. Write the limitations slide: five limitations, each with your model's measured failure — the RAG motivation slide for the capstone pitch.

## Pitfalls

- **Confident hallucination as an edge case** — it's the *central* case; design for it, don't dismiss it
- **"Fine-tuning will fix it"** — the rot mechanism makes it worse over time; the fix is retrieval
- **Provenance skipped for internal tools** — internal users need audit trails too (compliance, debugging)
- **Testing only the failure modes you thought of** — run the battery on YOUR model; the surprising failures are the informative ones
- **Confusing knowledge cutoff with staleness** — the model may know old facts correctly; the failure is applying them to changed circumstances

## Resources

- W4-01 parent (the architecture), W3-05 (the levers), W16-01 (the eval versioning) — composed here
- Lewis et al., *RAG* — the original argument
- Gekhman et al., *Fine-Tuning on New Knowledge Encourages Hallucinations* — the rot evidence
