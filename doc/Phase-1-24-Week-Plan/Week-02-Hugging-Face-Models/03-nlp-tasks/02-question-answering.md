# 03.2 — Question Answering

> Subfolder index: [README.md](README.md) · Parent: [../03-nlp-tasks.md](../03-nlp-tasks.md)

---

## What you'll learn

- Extractive QA: span prediction with scores and offsets — the auditable answer
- Generative QA: reading comprehension with synthesis
- The closed-book vs open-book distinction (the RAG seed)
- Score thresholds and the "no answer in passage" problem

## 1. Extractive QA — spans with provenance

```python
from transformers import pipeline

qa = pipeline("question-answering", model="distilbert/distilbert-base-cased-distilled-squad")

passage = """RAG combines a retriever that searches a knowledge base with a generator
that conditions its answer on the retrieved passages. Retrieval grounds the model
in facts it was never trained on and enables citations."""

out = qa(question="What grounds the model in facts?", context=passage,
         top_k=3)                                            # top-3 spans!
print(out)
# [{'score': 0.79, 'start': 143, 'end': 164, 'answer': 'the retrieved passages'}, ...]
```

What makes extractive QA production-grade:

- **`start`/`end` offsets** — highlight the answer in the UI; cite the exact position
- **`score`** — confidence to threshold on (low score → "not found in this passage")
- **`top_k`** — multiple candidate spans for review
- **`handle_impossible_answer=True`** — some models can return an empty span for unanswerable questions

## 2. The passage problem (and the threshold)

```python
irrelevant = "The weather in Paris is mild in spring."
out = qa(question="What grounds the model?", context=irrelevant)
# a "confident" span from an irrelevant passage — garbage in, confident garbage out

SOLUTION: score threshold + retrieval quality upstream (W4) — the QA model
 trusts the passage; the retriever must earn that trust.
```

The threshold calibration: run 20 (question, wrong-passage) pairs and record the score distribution — the "wrong passage" scores cluster below some value. Set the threshold above the 95th percentile of that cluster. This is the extractive-QA version of W4-03's distance elbow.

## 3. Generative QA — synthesis over spans

```python
from transformers import pipeline

gen_qa = pipeline("text2text-generation", model="google/flan-t5-base")

prompt = f"Answer the question using only this context.\n\nContext: {passage}\n\nQuestion: What grounds the model in facts?"
print(gen_qa(prompt, max_new_tokens=50)[0]["generated_text"])
# 'the retrieved passages' — synthesized into a sentence
```

| | Extractive | Generative |
|---|---|---|
| answer form | exact span | natural sentence |
| citations | offsets directly | needs alignment work |
| synthesis across passages | no | yes |
| hallucination | no | yes — measure (W5-05 faithfulness) |
| multi-passage reasoning | no | yes |

Selection: extraction when the wording must be exact and auditable; generation when the answer must synthesize. The W12-04 analytics agent and W1-07 chat both use generation — with the grounding contract (W4-01) as the hallucination defense.

## 4. The retrieval sandwich (the RAG seed)

Both QA models answer **given** a passage. The system question — who finds the passage? — is the whole RAG architecture (W4):

```
closed-book (LLM from memory)  ← hallucination-prone, stale
open-book extractive (this file) ← correct, but needs the right passage
open-book + retriever (W4 RAG)  ← finds the passage automatically
open-book + generative + retriever ← the full RAG pattern (W4-01)
```

Each step up the ladder adds retrieval quality requirements — and each is testable with the same QA evals.

## Exercises

1. Score calibration: 20 (question, correct-passage) and 20 (question, wrong-passage) pairs — plot the two score distributions; set the threshold at the separation point.
2. Span-verification: for 10 answers, assert `passage[start:end] == answer` — the offsets invariant (W2-03's roundtrip discipline, QA edition).
3. Multi-passage synthesis: 3 passages, one question requiring two of them — extractive fails, generative succeeds? Demonstrate.
4. The impossibility probe: `handle_impossible_answer` on SQuAD-2-style models vs a question with no answer in the passage — compare behaviors across 3 models.
5. Cost/quality table: extractive vs generative vs closed-book LLM on 20 questions — accuracy, citations, latency, cost. The QA decision table for your capstone.

## Pitfalls

- **QA without retrieval** — the passage IS the answer's source; garbage passage = confident garbage span (§2)
- **Generative QA without the grounding contract** — "answer from context only" must be in the prompt AND verified (W4-01's faithfulness checks)
- **`top_k=1` hiding better candidates** — review top-3 during development; the score gap tells you about ambiguity
- **Token limits on long contexts** — BERT-class QA caps at ~512 tokens; chunk the passage (W4-02) and answer per chunk
- **Assuming generative QA cites** — it doesn't unless you build the alignment (answer spans → source verification)

## Resources

- HF [question answering task guide](https://huggingface.co/docs/transformers/tasks/question_answering) — extractive and generative
- [SQuAD 2.0](https://rajpurkar.github.io/SQuAD-explorer/) — the unanswerable-question benchmark (§2's threshold source)
- W4-01 (the RAG contract this file seeds), W6-04 (structured QA analog)
