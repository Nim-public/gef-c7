# 03 — Vision Agents: Composing Detection, OCR & VLMs

> E4 index: [README.md](README.md)

**Core topic:** *Document/product agents that compose detection + OCR + VLM steps — W13-04's graph, vision edition.*

---

## What you'll learn

- The vision-agent graph: perceive (detect/OCR) → decide (route by content) → extract → verify → cite
- Tool design for vision steps (typed, verifiable, pixel-aware — W10-02 rules)
- Verification as graph nodes (the W12-04 numeric check, vision edition)
- A document-processing agent over your capstone's document types

## 1. The graph (W13-01's pattern, vision tools)

```
START ─► classify_page ─┬─► ocr_extract ─► field_verify ─► END
                        ├─► detect_objects ─► describe_regions ─► END
                        └─► vlm_full_answer ─► END
```

State:

```python
class VisionState(TypedDict):
    image_path: str
    page_type: str                       # invoice | form | photo | screenshot | chart
    ocr_text: str
    fields: dict                         # extracted fields with boxes
    detections: list[dict]               # boxes + labels (file 01)
    answer: str
    citations: list[str]
    log: Annotated[list[str], lambda a, b: a + [b]]
```

Nodes wrap your E4-01/02 functions as typed tools (W10-02):

```python
def classify_page(state):
    r = vlm_classify(state["image_path"],
                     labels=["invoice", "form", "photo", "screenshot", "chart"])  # W2-04 CLIP or VLM
    return {"page_type": r["label"], "log": [f"classified={r['label']} ({r['confidence']:.2f})"]}

def ocr_extract(state):
    page = ocr_page(Image.open(state["image_path"]))           # file 02 §2
    fields = vlm_extract_fields(state["image_path"], page_type=state["page_type"])  # file 02 §3
    fields = verify_fields(fields, page["words"])              # §2 numeric/text check
    return {"ocr_text": page["text"], "fields": fields,
            "citations": [f"{state['image_path']}#{f}" for f in fields],
            "log": [f"ocr {len(page['words'])} words, {len(fields)} fields"]}
```

## 2. Routing by content (the conditional edges)

```python
def route_by_type(state) -> str:
    return {"invoice": "ocr_extract", "form": "ocr_extract",
            "photo": "detect_objects", "screenshot": "detect_objects",
            "chart": "vlm_full_answer"}[state["page_type"]]
```

The W6-04/W14-04 routing pattern with vision classes — and the same *route accuracy* metric applies (log `page_type` decisions; measure against hand labels).

## 3. Verification as a node (the auditability layer)

```python
def field_verify(state):
    issues = []
    for name, val in state["fields"].items():
        if isinstance(val, (int, float)) or has_digits(str(val)):
            if not digits_supported(str(val), state["ocr_text"]):   # W12-04 §3
                issues.append(f"{name}={val} not found in OCR text")
    return {"log": [f"field_verify: {len(issues)} unsupported fields"], "issues": issues}
```

Verified fields carry their OCR/box provenance into the citation layer; unverifiable fields get flagged in the answer ("total not confidently extracted — please check page 1").

## 4. The multi-image case (documents, not pages)

Multi-page invoices/contracts = a graph over pages: `per_page → merge_fields → conflict_check` (two pages with different totals → flag, don't average). The merge node is where W13-04's team patterns apply: per-page extraction (parallel nodes) → merge node → conflict gate → answer.

## Exercises

1. Build the graph over 10 mixed images (3 invoices, 3 photos, 2 screenshots, 2 charts); print each node path.
2. Misclassification drill: an invoice that looks like a form — which route fires, and does the extraction still work? Harden `classify_page`.
3. Field-verify stress: 5 fields with OCR noise (₹/., confusion) — tune `digits_supported` until the check catches them without false-flagging clean fields.
4. Multi-page merge: a 3-page invoice with a corrected total on page 3 — implement `conflict_check` and produce the flagged answer.
5. Cost table: classify + OCR + VLM-extract per image — tokens and $ per document; compare with pure-VLM (no OCR) extraction cost (W9-03's P3 economics).

## Pitfalls

- **VLM route as the default for everything** — OCR+rules is cheaper and deterministic where it works (file 02's table); route, don't flatten
- **`fields` dict without provenance** — extraction without boxes/confidence breaks citations (file 02's contract)
- **classify confidence ignored** — a 0.4 "invoice" guess routes garbage; low-confidence → a `vlm_full_answer` fallback arm (W5-04 escalation)
- **Log field as decoration** — the `log` reducer is your audit trail (W13-03); write decision reasons into it, not just events
- **Vision steps without image validation** — corrupt/zero-byte images crash nodes mid-graph; validate at classify (W7-02's post-preprocessing check)

## Resources

- LangGraph docs (W13-01) — the graph skeleton; this file changes only the nodes
- W9-03 (pattern table), W14-04 (routing), W12-04 (numeric grounding) — composed here
- HF [image-to-text](https://huggingface.co/docs/transformers/tasks/image_captioning) + VLM quickstarts — the perceive tools
- [docling](https://github.com/DS4SD/docling) (file 02) — the layout layer for gnarly pages
