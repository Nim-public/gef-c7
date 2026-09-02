# 01 — Detection & Segmentation

> E4 index: [README.md](README.md)

**Core topics:** *Object detection (DETR, YOLO) and segmentation (SAM) — localization beyond CLIP.*

---

## What you'll learn

- Detection vs classification vs segmentation — output spaces and when each is the tool
- Zero-shot detection with DETR-class open-vocabulary models
- SAM: promptable segmentation (everything, no labels) and its RAG use
- Composing detection + VLM for grounded answers ("what and where")

## 1. The output spaces (why CLIP can't do this)

| Model family | Output | Question it answers |
|---|---|---|
| CLIP (W8-04) | whole-image ↔ text similarity | "is this a photo of X?" |
| **Detection** (DETR/YOLO) | boxes + classes + scores | "what objects are where?" |
| **Segmentation** (SAM) | pixel masks | "exact region of each object?" |
| VLM (W9-03 P3) | text about the image | "describe/explain" |

Detection = *localization + classification* per instance. The W8-04 weakness table (counting, fine differences) is exactly what detection solves: DETR counts, SAM delineates.

## 2. Detection with DETR (zero-shot classes via text? — trained classes, but transformers make it easy)

```python
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from PIL import Image

proc = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = AutoModelForObjectDetection.from_pretrained("facebook/detr-resnet-50")

img = Image.open("street.jpg")
inputs = proc(images=img, return_tensors="pt")
out = model(**inputs)
results = proc.post_process_object_detection(out, threshold=0.9)[0]
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    print(f"{model.config.id2label[label.item()]}: {score:.2f} at {[round(v,1) for v in box]}")
# 'car': 0.99 at [120.0, 144.1, 512.3, 401.2]
```

- Output: **boxes** `[x1, y1, x2, y2]` + class + score — the localization CLIP never gives (E3-02's "detection models for localization" note, now in hand)
- **Open-vocabulary detection** (text prompts as classes): OWL-ViT (`google/owlvit-base-patch32`) — CLIP-like text conditioning over detection:

```python
from transformers import Owlv2Processor, Owlv2ForObjectDetection

proc = Owlv2Processor.from_pretrained("google/owlv2-base-patch16-ensemble")
owl = Owlv2ForObjectDetection.from_pretrained("google/owlv2-base-patch16-ensemble")
inputs = proc(text=[["a mechanical keyboard", "a gaming mouse"]], images=img, return_tensors="pt")
out = owl(**inputs)
targets = proc.post_process_grounded_object_detection(out, input_ids=inputs.input_ids,
                                                      threshold=0.25)[0]
```

## 3. Segmentation with SAM (Segment Anything)

SAM segments *any* object given a prompt (point/box) — class-agnostic masks, no training:

```python
from segment_anything import sam_model_registry, SamPredictor   # pip install segment-anything

sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h.pth")   # or vit_b for CPU
pred = SamPredictor(sam)
pred.set_image(np.array(img))
masks, scores, _ = pred.predict(box=np.array([120, 144, 512, 401]))  # box from DETR!
```

The composition that matters: **DETR finds, SAM delineates** — detection gives the box, SAM gives the pixel mask, and a captioner/VLM (W8-04) names/attributes it. That triple is the backbone of product-catalog extraction, medical-image reference, and screenshot understanding.

`FastSAM`/`MobileSAM` variants trade quality for speed; SAM 2 extends to video (mask propagation across frames — the video-answering building block).

## 4. Detection + RAG (the W9 upgrade)

E4's RAG hook: localized assets enter the multimodal index with structure:

```python
# per detected object → a "region chunk" with crop + metadata
for det in results:
    crop = img.crop(det["box"])
    crop.save(f"data/crops/{img_id}_{det['label']}.png")
    index.add({"id": f"{img_id}:{det['label']}", "type": "region",
               "label": det["label"], "score": float(det["score"]),
               "image_path": crop_path, "source_image": img_id})
```

Now questions like "show me the monitor in product photos" retrieve *region* crops with bounding-box provenance — citation at pixel level (W4-01's contract, visual edition).

## Exercises

1. DETR on 5 capstone images: list detections with scores. Then OWL-ViT with 3 custom text classes — compare what each finds.
2. DETR→SAM composition: detect, then segment each box; save crops + masks. Visual check — do the masks isolate the objects?
3. Region-chunk RAG: index 20 region crops (§4) + their source image; ask "find photos containing a keyboard" — do region hits beat whole-image hits (W9-02)?
4. Counting probe: "how many keyboards?" answered by DETR count vs CLIP score vs VLM guess. Rank reliability (W8-04's weakness, now fixed — show it).
5. Threshold sweep: DETR `threshold` ∈ {0.3, 0.5, 0.7} on one cluttered image — precision/recall trade visible in one table.

## Pitfalls

- **Detection ≠ classification confidence** — a 0.55 box is often real; tune per domain, not per image
- **CLIP-style zero-shot expectations on DETR** — base DETR has fixed classes; use OWL-ViT for text-prompted classes
- **SAM masks without semantics** — masks are class-agnostic; you need DETR/VLM to name them
- **Small objects missed** — downscaling destroys them; tile large images (W1-04's PDF tiling lesson, vision edition)
- **Region crops without source linkage** — a crop without `source_image`+box metadata is an orphaned asset (W7-01 manifest rules)

## Resources

- Carion et al., *DETR* (End-to-End Object Detection with Transformers) — §1 + architecture figure
- Kirillov et al., *Segment Anything* — the promptable-segmentation paper
- HF task guides: [object detection](https://huggingface.co/docs/transformers/tasks/object_detection), [zero-shot object detection](https://huggingface.co/docs/transformers/tasks/zero_shot_object_detection)
- [SAM demo Space](https://huggingface.co/spaces/) (search "segment anything") — click-to-segment in browser
