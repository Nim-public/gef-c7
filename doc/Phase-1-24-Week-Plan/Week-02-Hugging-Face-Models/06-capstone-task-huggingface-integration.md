# 06 — Weekly Task: Integrate a Hugging Face Model into Your Capstone

> Week 2 index: [README.md](README.md) · **Due: before Week 3 (by 19 Sep)**

**Task (from the schedule):** *Incorporate Hugging Face models into your capstone project for a specific NLP, CV, or translation task.*

Last week you formalized scope; this week you prove the **model layer** is real: one Hugging Face model running in your capstone's code, doing one concrete job, evaluated on a handful of your own examples.

---

## 1. Deliverable

In your capstone repo, a `models/` module (or notebook) + a short `models/README.md` containing:

1. **Task choice** — exactly one NLP, CV, or translation task from your scope doc
2. **Model choice** — repo ID, license, params, why it (not the 3 alternatives you compared)
3. **Working code** — loads the model, runs on real sample inputs from your data
4. **Mini-eval** — 20+ examples, labeled pass/fail by you, one summary number
5. **Integration note** — where this sits in the capstone pipeline (what calls it, what consumes its output)

## 2. Choose your task (one — don't sprawl)

| If your capstone needs… | Task this week | File with how-to |
|---|---|---|
| Sentiment/intent/category on texts | classification (fine-tuned or zero-shot) | 02 |
| People/orgs/locations masked or extracted | NER (+ Week 1 regex) | 02 |
| Long docs condensed | summarization | 03 |
| Answers verifiable against source passages | extractive QA | 03 |
| Cross-language support | translation | 03 |
| Similar items / dedup / search-ish matching | sentence embeddings | 03 |
| Image tags/matching for a catalog | CLIP zero-shot image classification | 04 |
| Audio/video corpus made searchable | Whisper transcription | 04 |
| Fully-local inference requirement | SLM behind an OpenAI-compatible endpoint | 05 |

**Pick the one your scope doc's feasibility section flagged.** The point is retiring the biggest unknown in your plan.

## 3. Model selection protocol (do it in this order)

1. Hub filter: task → license (`apache-2.0`/`mit` preferred) → language → sort by downloads
2. Shortlist 3; note params, context/input limits, model-card limitations
3. Same 10 sample inputs through all 3 (the widgets + `pipeline`); eyeball
4. Pick the winner; run the 20-example mini-eval on it
5. Pin the revision (`revision=`) and record it in `models/README.md`

## 4. Mini-eval protocol (20 examples, 30 minutes)

```python
import json

samples = json.load(open("data/eval_sample.jsonl", encoding="utf-8"))  # your inputs + expected
results = [predict(s["input"]) for s in samples]
correct = sum(r == s["expected"] for r, s in zip(results, samples))
print(f"{correct}/{len(samples)} = {correct/len(samples):.0%}")
```

- Labeling "expected" by hand for 20 items is legitimate *and* reusable — this becomes the seed of your Week 16 eval suite
- Record failures: copy each miss into `eval_notes.md` with one line of "why"
- If pass-rate < your bar: try the other shortlisted model, a different label phrasing (zero-shot), or preprocessing — **before** concluding "AI can't do this"

## 5. Integration note — write the seam, not the app

The deliverable is a function with a clean interface, not a finished product:

```python
def classify_ticket(text: str) -> dict:
    """capstone: routes ticket. input: raw text. output: {label, score, model, revision}."""
    out = clf(text[:512])[0]
    return {"label": out["label"], "score": out["score"],
            "model": MODEL_ID, "revision": REVISION}
```

Record in the README: inputs/outputs, latency per call, failure behavior (what happens on empty text? 512-token overflow?), and the Week-4 hook (e.g., "these embeddings will seed the vector index").

## 6. Checklist

- [ ] One task, one model, one revision pinned
- [ ] License recorded; commercial use verified
- [ ] Runs on ≥20 real samples from *your* data
- [ ] Pass-rate computed; 3 failure modes written down
- [ ] Function signature documented for the team
- [ ] `models/README.md` states where this sits in the pipeline and what Week 3–4 will do with it

Bring your mini-eval results to Office Hours (17 Sep) — mentors will push you on failure modes and whether the chosen model can carry the whole capstone or just one stage of it.
