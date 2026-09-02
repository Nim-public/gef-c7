# Week 1 — Text Data & LLM Foundations: Study Guide

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 5 Sep, 7–10 PM IST (Session 1) · Sun 6 Sep, 7–10 PM IST (Session 2) · Office Hours Thu 10 Sep, 7–8 PM IST

**Weekly task:** [08-capstone-task-formalize-scope.md](08-capstone-task-formalize-scope.md)

---

## Why this week matters

Every later topic — RAG (Weeks 4–6), multimodal AI (Weeks 7–9), agents (Weeks 10–14) — rests on the same stack of ideas introduced here:

```
raw text ──► strings/regex ──► tokens ──► IDs ──► vectors (embeddings)
                                                    │
structured data (pandas) ─────────────────────────►  ML model  ──► prediction / generation
files (CSV/JSON/PDF) & web crawls ──► datasets ──────┘
```

If you can move text between these representations fluently, everything downstream is just new model architectures on top.

## What you will be able to do after this week

- [ ] Explain word vs character vs subword tokenization and why LLMs use subword (BPE)
- [ ] Read and write special tokens (`<PAD>`, `<EOS>`, `<CLS>`, `<UNK>`) and attention masks
- [ ] Manipulate and clean text with Python strings, f-strings, and regex
- [ ] Build one-hot / multi-label encodings and explain their limits
- [ ] Load text into embeddings and visualize similarity in 2D
- [ ] Select, filter, aggregate, and join tabular data with pandas
- [ ] Extract text from CSV, JSON, JSONL, and PDF files; crawl web pages politely
- [ ] Define ML tasks (classification / regression / generation) and train a classic model with scikit-learn
- [ ] Trace the line from neural networks → transformers → pre-trained vs instruction-tuned LLMs
- [ ] Call a chat-completions API: multi-turn history, temperature/sampling, log probabilities
- [ ] Formalize a capstone project scope with explicit data requirements and feasibility checks

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-tokenization-and-text-representation.md](01-tokenization-and-text-representation.md) | Tokenization, special tokens, encodings, embeddings | 3–4 h |
| 2 | [02-string-manipulation-and-regex.md](02-string-manipulation-and-regex.md) | Strings, f-strings, Unicode, regex for cleaning | 2–3 h |
| 3 | [03-pandas-structured-data.md](03-pandas-structured-data.md) | Selection, filtering, aggregation, joins | 3–4 h |
| 4 | [04-file-handling-and-web-crawling.md](04-file-handling-and-web-crawling.md) | CSV / JSON / PDF, polite web crawling | 2–3 h |
| 5 | [05-ml-fundamentals.md](05-ml-fundamentals.md) | ML tasks, losses, metrics, scikit-learn | 3 h |
| 6 | [06-from-neural-networks-to-llms.md](06-from-neural-networks-to-llms.md) | NNs → transformers → pre-training vs instruction tuning | 3–4 h |
| 7 | [07-llm-concepts-and-demos.md](07-llm-concepts-and-demos.md) | Chat completions, sampling, logprobs, RLHF | 3 h |
| 8 | [08-capstone-task-formalize-scope.md](08-capstone-task-formalize-scope.md) | Formalize capstone scope (weekly task) | 2 h |

** rhythm:** watch/attend the session first, then do the matching file's hands-on parts the same day. Bring blockers to Thursday Office Hours.

## Environment setup (carry-over from Base Camp 1)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install pandas scikit-learn matplotlib jupyter
pip install tiktoken transformers
pip install requests beautifulsoup4 pypdf pdfplumber
pip install openai python-dotenv
```

- `transformers` needs a backend; PyTorch CPU is enough for this week: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Put API keys in a `.env` file (never commit it): `OPENAI_API_KEY=sk-...`
- Models run locally this week are small (≤ 0.5 B params) so a laptop without GPU is fine.

## Self-check before Week 2

1. Why does `len(text.split())` not equal `len(encoding.encode(text))`?
2. What breaks if you pad a batch without an attention mask?
3. When would you use `merge(how="left")` instead of `how="inner")`?
4. A model answers a factual question wrongly but confidently — which week-1 concept explains this, and which later-week technique fixes it?
5. What does `logprobs=True` give you that plain text output does not?
