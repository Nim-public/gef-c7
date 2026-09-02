# 02 — Document AI: OCR, Layout & Structured Extraction

> E4 index: [README.md](README.md)

**Core topics:** *OCR pipelines, layout awareness, table extraction, DocVQA — reading structured text from images.*

---

## What you'll learn

- The document pipeline: rasterize → OCR/layout → structure → index (W1-04's PDF layer, vision edition)
- Tesseract vs VLM-based extraction — the trade
- Table and form extraction with layout awareness
- Field-level citations for document QA (the extraction metadata contract)

## 1. The document pipeline

```
PDF/image ─► rasterize pages ─► [OCR: text + boxes] ─► [layout: headings, tables, reading order]
         ─► structured records (per section/table/field, with page+bbox metadata)
         ─► index: text chunks + region crops (W9-02) + structured fields (W6-style)
```

W1-04 flagged scanned PDFs as the RAG blind spot; this file is the fix.

## 2. OCR: Tesseract (boxes included)

```powershell
pip install pytesseract pillow    # + install the Tesseract binary for your OS
```

```python
import pytesseract
from PIL import Image, ImageOps

def ocr_page(img: Image.Image) -> dict:
    img = ImageOps.exif_transpose(img).convert("L")     # W7-02's preprocessing rules
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    words = []
    for i, txt in enumerate(data["text"]):
        if txt.strip() and int(data["conf"][i]) > 40:   # confidence filter
            words.append({"text": txt, "conf": int(data["conf"][i]),
                          "box": [data["left"][i], data["top"][i],
                                  data["width"][i], data["height"][i]]})
    return {"text": pytesseract.image_to_string(img), "words": words}
```

The `words` list with boxes is what enables **field-level citations**: every extracted value knows its pixel location. Preprocess for accuracy: 300+ DPI, grayscale, deskew (`Image.rotate` with `expand`), thresholding for low-contrast scans.

## 3. VLM-based extraction (the modern alternative)

For complex layouts, a VLM (Qwen-VL-class, W9-03 P3) with a strict extraction contract often beats OCR+rules:

```python
EXTRACT = """Extract every field from this invoice image as strict JSON:
{"invoice_no": "", "date": "YYYY-MM-DD", "vendor": "", "total": {"amount": 0, "currency": ""},
"line_items": [{"description": "", "qty": 0, "price": 0}]}
Rules: copy values EXACTLY as printed; use null for anything not visible; no invented fields."""

resp = client.chat.completions.create(
    model=MODEL, temperature=0,
    messages=[{"role": "user", "content": [
        {"type": "text", "text": EXTRACT},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]}])
invoice = json.loads(resp.choices[0].message.content)
```

| Approach | Wins | Loses |
|---|---|---|
| **Tesseract + rules** | cheap, deterministic, pixel boxes, offline | messy layouts, handwriting, multi-column order |
| **VLM extraction** | layout-agnostic, forms/handwriting, semantic fields | cost per page, hallucinated fields, no pixel boxes (unless model provides) |
| **Specialized DocAI** (docling, Azure Document Intelligence) | tables/layout at production quality | service dependency |

Production shape: OCR + layout for the *corpus* (bulk, cheap), VLM for *field extraction on demand* — with the numbers-supported check (W12-04) verifying extracted values against OCR text.

## 4. Tables and forms

- **pdfplumber** (W1-04) for born-digital PDFs — `extract_tables()` with cell coordinates
- **docling** (IBM, open-source) — layout model → structured export (tables, reading order) for gnarly PDFs
- Tables become: markdown chunk (W7-01's whole-table rule) + per-cell records with coordinates when field-level citation matters

DocVQA-style QA ("what's the invoice total?") then answers from the extracted fields with *field-level citations*: `"₹45,000 [invoice.pdf p.1 total, conf 0.93]"`.

## 5. Indexing extracted documents

```python
records = []
for page in pages:
    records.append({"id": f"{doc}::p{page.n}::text", "type": "page_text",
                    "text": page.ocr_text, "source": doc, "page": page.n})
    for f_name, f_val, f_box in page.fields:
        records.append({"id": f"{doc}::p{page.n}::{f_name}", "type": "field",
                        "text": f"{f_name}: {f_val}", "source": doc,
                        "page": page.n, "box": f_box})
# → text chunks to the vector index; structured fields to SQLite (W6); crops to the multimodal index (W9-02)
```

One document, three store entries, all joined by the same id prefix — the W6-02 coexistence map, document edition.

## Exercises

1. OCR 5 pages (3 clean, 1 low-contrast, 1 rotated) — build the confidence histogram; set your rejection threshold; report the garbage-word rate per page type.
2. Invoice extraction A/B: Tesseract+rules vs VLM contract (§3) on 5 invoices — field-level accuracy per field. Which fields does each miss?
3. Field-citation demo: "what's the total on invoice X?" answered with `[page, field, conf]` — build the metadata path end to end.
4. Table round-trip: extract a table via pdfplumber; render it back to markdown; compare against the original — what silently changed (merged cells? footers)?
5. Numeric validation hook: run `numbers_supported` (W12-04) over extracted totals vs OCR words — catch the "45.000 vs ₹45,000" class of error.

## Pitfalls

- **OCR without confidence filtering** — garbage tokens pollute the index; the `conf > 40` filter is the floor, not the ceiling
- **VLM field hallucination** — models invent plausible invoice fields; `null`-for-invisible rules + verification against OCR text
- **Currency/locale mangling** — "45.000" (European) vs "45,000" (Indian/US); normalize with the locale recorded in metadata
- **Multi-column reading order** — naive OCR interleaves columns; layout-aware tools (docling) or box-ordering logic required
- **Extraction without page/box metadata** — field-level citations impossible; the metadata contract is the feature

## Resources

- [Tesseract docs](https://tesseract-ocr.github.io/) + pytesseract API — the OCR engine
- [docling](https://github.com/DS4SD/docling) — layout-aware document parsing
- HF [DocVQA](https://huggingface.co/datasets/lmms-lab/DocVQA) + Donut-class models — end-to-end document understanding
- W1-04 (PDF baseline), W12-04 (numeric grounding), W7-01 (metadata) — composed here
