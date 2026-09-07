# 04.2 — PDF Extraction

> Subfolder index: [README.md](README.md) · Parent: [../04-file-handling-and-web-crawling.md](../04-file-handling-and-web-crawling.md)

---

## What you'll learn

- The three PDF layers and the decision tree between them
- pypdf and pdfplumber hands-on, with quality auditing
- OCR as the fallback layer (Tesseract) and when it's required
- The extraction quality audit (how you *know* it worked)

## 1. The three layers

| Layer | Tool class | Handles | Fails on |
|---|---|---|---|
| **Text-layer extraction** | pypdf | born-digital PDFs | scans, complex layout order |
| **Layout parsing** | pdfplumber, docling | multi-column, tables, coordinates | heavy design layouts |
| **OCR** | Tesseract, cloud OCR | scanned images | quality of scan; needs preprocessing |

Decision test first: does `pypdf` extract real sentences? If output is empty/garbage → it's a scan → OCR tier. If text exists but order is scrambled → layout tier.

## 2. pypdf — the text layer

```python
from pypdf import PdfReader

reader = PdfReader("data/handbook.pdf")
print(len(reader.pages), "pages, metadata:", reader.metadata)

for i, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    print(f"page {i+1}: {len(text)} chars")
```

The `or ""` matters: some pages (pure images) return `None`/empty — treat as "no text layer" signals, not empty documents (file 02's audit builds on this).

## 3. pdfplumber — layout awareness

```python
import pdfplumber

with pdfplumber.open("data/invoice.pdf") as pdf:
    page = pdf.pages[0]
    print(page.extract_text())                 # reading-order text
    for t in page.extract_tables():            # table structure!
        for row in t: print(row)
    print(page.extract_words()[:5])            # word boxes: text + x0,y0,x1,y1
```

What layout parsing buys over pypdf: **word coordinates** (field-level citations, W20-02), **table structure** (cells, not soup), and column-aware reading order. Cost: slower per page; use pypdf for bulk text, pdfplumber where structure matters.

## 4. OCR — the image tier

```python
import pytesseract
from PIL import Image, ImageOps

def ocr_image(img: Image.Image) -> dict:
    img = ImageOps.grayscale(img)
    img = img.resize((img.width * 2, img.height * 2))   # upscale helps small text
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    words = [{"text": w, "conf": int(c), "box": [l, t, wd, h]}
             for w, c, l, t, wd, h in zip(data["text"], data["conf"],
                                          data["left"], data["top"],
                                          data["width"], data["height"])
             if w.strip() and int(c) > 40]
    return {"text": pytesseract.image_to_string(img), "words": words}
```

Preprocessing decides OCR quality: grayscale, upscale 2×, threshold low-contrast scans, deskew (E4-02's pipeline). Confidence filtering (`conf > 40`) removes garbage tokens — the audit then measures the garbage rate per page type (E4-02 ex. 1).

## 5. The quality audit (how you know it worked)

```python
def audit_extraction(pages: list[str]) -> dict:
    lengths = [len(t) for t in pages]
    garbage = sum(1 for t in pages if len(t) < 50)
    return {"pages": len(pages), "median_chars": sorted(lengths)[len(lengths)//2],
            "empty_or_tiny": garbage, "empty_rate": garbage / max(len(pages), 1)}
```

Plus the manual check that never goes away: open the PDF and the extracted text side by side for 3 random pages (W1-04's eyeball rule). Numbers + eyeballs = the extraction quality story in your capstone README.

## Exercises

1. Three-layer decision drill: 6 PDFs (digital, scanned, mixed, table-heavy, multi-column, corrupted) — route each through the decision tree; report which layer each needed.
2. Extraction audit: run pypdf on 20 pages; build the audit dict (§5); flag pages below 200 chars for manual review — what fraction needs OCR?
3. Table extraction: pdfplumber on a table-heavy page — reconstruct the table as markdown (W7-01's serialization); compare against the visual original.
4. OCR preprocessing sweep: grayscale / upscale / threshold / deskew on one bad scan — OCR quality (word count + spot accuracy) per variant.
5. Provenance indexing: extract with word boxes; store every word with page+bbox metadata (W20-02's schema); answer "where on page 2 is the total?" from the index.

## Pitfalls

- **Trusting extraction blindly** — reordered columns and dropped hyphens are invisible without the side-by-side audit
- **OCR on low-resolution scans** — 150 dpi garbage in, garbage out; upscale + threshold first (E4-02's sweep)
- **Page-level text order** — extractors emit blocks in internal order, not reading order; layout tier or box-sorting fixes it
- **Encrypted/permission-restricted PDFs** — extraction may silently return empty; check `reader.is_encrypted`
- **Ignoring PDF metadata** — title/author/creation date are free metadata for the manifest (W7-01)

## Resources

- [pypdf docs](https://pypdf.readthedocs.io/) · [pdfplumber docs](https://github.com/jsvine/pdfplumber) — the two extraction layers
- [pytesseract](https://pypi.org/project/pytesseract/) + Tesseract [language data](https://github.com/tesseract-ocr/tessdata)
- E4-02 (document AI) — the full document pipeline this file feeds
- W1-04 parent, W7-01 (manifests), W20-02 (field citations) — composed here
