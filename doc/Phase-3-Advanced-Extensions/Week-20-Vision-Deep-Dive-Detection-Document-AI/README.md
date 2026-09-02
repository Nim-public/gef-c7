# Extension E4 — Vision Deep Dive: Detection, Segmentation & Document AI

> Extensions overview: [../README.md](../README.md)

**Builds on:** W7–9 (multimodal stack) · W8-01 (CNN/ViT encoders)

**Practice build:** [04-practice-vision-pipeline.md](04-practice-vision-pipeline.md)

---

## Why this extension matters

W7–9 treated images mostly as *retrievable assets* (embed → find → caption). This week adds the precision layer: **localization** (where is it — detection/segmentation) and **document intelligence** (reading structured text from images — OCR, tables, forms). These turn the multimodal RAG from "find similar images" into "extract exact data from this document and cite the field."

## What you will be able to do after this week

- [ ] Run zero-shot and trained object detection (DETR/YOLO) and segmentation (SAM)
- [ ] Choose detection vs captioning vs VLM per question (W9-03's pattern table, precision edition)
- [ ] Build an OCR→structure pipeline (Tesseract/docling) with layout awareness
- [ ] Answer document questions (DocVQA-style) with field-level citations
- [ ] Extend your W9 multimodal index with localized, structured extraction

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-detection-segmentation.md](01-detection-segmentation.md) | DETR/YOLO detection, SAM segmentation | 3 h |
| 2 | [02-document-ai.md](02-document-ai.md) | OCR, layout, tables, DocVQA | 3 h |
| 3 | [03-vision-agents.md](03-vision-agents.md) | Composing detection+OCR+VLM into document agents | 2–3 h |
| 4 | [04-practice-vision-pipeline.md](04-practice-vision-pipeline.md) | Document → structured index pipeline (practice) | 4 h |

## Environment setup

```powershell
pip install transformers pillow torch torchvision
pip install pytesseract pdfplumber docling      # OCR/doc layer (tesseract binary required)
```

## Self-check before E5

1. "How many people are in this photo?" — CLIP fails (W8-04), DETR doesn't. Why, in one sentence about the output spaces?
2. Your OCR pipeline misreads "₹45,000" as "45.000". Where in the document pipeline does a numeric-validation hook belong (W6-03's lesson)?
3. SAM segments everything but names nothing — what does it need from another model to be useful in RAG?
4. Which of your capstone's images contain *structured* data (tables/forms/screenshots) vs *scenes*? Different pipelines — which for which?
5. Field-level citations for a form extraction: what metadata must the extraction record keep (W7-01's manifest rules)?
