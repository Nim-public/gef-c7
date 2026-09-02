# 04 — Practice: Document-to-Knowledge Pipeline

> E4 index: [README.md](README.md) · **Due: before E5**

*(Practice build — a document-processing pipeline that turns a pile of documents/images into a structured, cited, searchable knowledge base — the vision edition of your W9 multimodal RAG.)*

---

## 1. Deliverable

```
docai/
  pipeline.py            # the E4-03 graph: classify → route → extract → verify → index
  ocr.py                 # Tesseract + confidence filtering (file 02 §2)
  extractors.py          # VLM field-extraction contracts (file 02 §3)
  detection.py           # DETR/OWL-ViT + SAM composition (file 01)
  index.py               # three-store indexing: chunks + fields + region crops (file 02 §5)
  eval/
    extraction_cases.jsonl   # 15 documents (5 invoices/forms, 5 photos, 5 mixed)
    results.md               # field accuracy, detection precision, citation coverage
  README.md              # decisions, failure modes, W9-02 integration
```

Demo: one invoice → extracted fields with field-level citations; one photo → detected regions → region-crop retrieval; one multi-page document → merged, conflict-flagged extraction.

## 2. Requirements (graded)

### Pipeline
- [ ] E4-03 graph running over ≥15 documents; node paths logged
- [ ] OCR with confidence filtering + VLM extraction contracts (nulls honored)
- [ ] `field_verify` + `qa_check` nodes active (W12-04 numeric check, vision edition)

### Indexing (file 02 §5)
- [ ] Three-store indexing working: text chunks (W4-05 harness-compatible), structured fields (SQLite, W6), region crops (W9-02 multimodal index)
- [ ] Field-level citations demonstrated: `[doc, page, field, conf, box]`

### Evaluation
- [ ] Field-level accuracy on 5 labeled invoices/forms (per-field, not per-doc)
- [ ] Detection precision on 10 photos (3 planted/verified objects each)
- [ ] End-to-end QA: 10 document questions answered with citations; Ragas faithfulness spot-check (W5-05)

## 3. Rubric

| Area | Weight |
|---|---|
| Graph pipeline (routing, extraction, verification nodes) | 30% |
| Three-store indexing with field-level citations | 25% |
| Evaluation (field accuracy, detection precision, QA faithfulness) | 25% |
| README (decisions, costs, failure modes) | 10% |
| Demo (three flagship document types) | 10% |

## 4. README sections (answer explicitly)

1. **Routing table**: page types → routes → measured route accuracy (E4-03 §2)
2. **Extraction quality**: per-field accuracy on labeled docs; the top-3 failure fields and their causes (OCR noise? layout? model?)
3. **Cost ledger**: OCR vs VLM-extract per page; where the pipeline uses which and why (file 02 §3's table with your numbers)
4. **W9-02 integration**: how region crops + field records enter the existing multimodal index — and what changed in the retrieval contract
5. **E5 bridge**: one *audio* analog in your capstone (call recordings? meeting notes?) — would the same graph pattern (classify → extract → verify → index) apply? (One paragraph — E5 answers it.)

## 5. Stretch (pick one)

- Batch mode: 50-document ingestion with resumable checkpoints (W4-05) + a progress Gradio page (W9-01)
- Chart understanding: route `chart` pages to a VLM with a data-extraction contract; validate extracted series against the rendered chart pixels (E4-01 detection on bars)
- DocVQA comparison: your pipeline vs a Donut/DocVQA-class model on 10 questions — accuracy and citation quality

Bring the extraction-quality table to your next mentor session: "document AI with field-level citations" is one of the strongest capstone demo stories in this program — the table is what makes it a claim instead of a wish.
