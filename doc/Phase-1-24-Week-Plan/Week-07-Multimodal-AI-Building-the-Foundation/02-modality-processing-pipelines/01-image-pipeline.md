# Image Pipeline — Load / EXIF / Convert / Normalize, with Parity Checks

**What you'll learn:** the five-stage image pipeline, and the parity check
that proves your hand-rolled preprocessing matches the model's processor.

## 1. The five stages, and what silently fails in each

| Stage | Operation | Silent failure mode |
|---|---|---|
| Load | `Image.open` (lazy) | decompression-bomb guard off; 12-bit TIFFs decode wrong |
| Orient | `ImageOps.exif_transpose` | phone photos sideways; orientation tag then stripped |
| Convert | `.convert("RGB")` | RGBA/P cropped or pasted with black bg instead of white |
| Resize | bicubic to processor size | your library's filter ≠ PIL's (OpenCV defaults differ) |
| Normalize | mean/std per model | ImageNet stats applied to a CLIP-specific model |

```python
from PIL import Image, ImageOps

def load_for_model(path: str, size: int = 224) -> "Image.Image":
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)          # orientation, then tag is moot
    img = img.convert("RGB")                    # flatten alpha onto black; paste
    img = img.resize((size, size), Image.BICUBIC)  # explicit filter, always
    return img
```

The alpha channel is the sneakiest: a transparent logo PNG flattened with
`.convert("RGB")` becomes black-on-black. If your corpus has logos/screenshots,
flatten onto white explicitly:

```python
def flatten_rgb(img, bg=(255, 255, 255)):
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        base = Image.new("RGB", img.size, bg)
        base.paste(img, mask=img.split()[-1])   # alpha as mask
        return base
    return img.convert("RGB")
```

## 2. Processor parity: prove your pipeline ≡ the model's

You will batch-process outside the processor (faster, parallel) — but only
legitimately if the output matches. The parity test:

```python
import numpy as np
from transformers import CLIPProcessor, CLIPModel

proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def parity_check(path: str) -> float:
    img = load_for_model(path)                       # your pipeline
    theirs = proc(images=img, return_tensors="pt")["pixel_values"][0]
    # hand-rolled equivalent:
    import torchvision.transforms.functional as TF  # or manual math
    mean = np.array([0.48145466, 0.4578275, 0.40821073])
    std  = np.array([0.26862954, 0.26130258, 0.27577711])
    arr = (np.asarray(img, dtype=np.float32) / 255.0 - mean) / std
    mine = np.transpose(arr, (2, 0, 1))              # HWC -> CHW
    return float(np.abs(mine - theirs.numpy()).max())

# Pass: max abs diff < 1e-4. Fail: your resize filter or mean/std is wrong.
```

Run the parity check **once per (model, pipeline) pair** in CI-style, then
trust the fast path. CLIP's mean/std are *not* ImageNet's — this single
constant is the most common multimodal bug in student repos.

## 3. Batch preprocessing with progress + failure quarantine

```python
from pathlib import Path
import pandas as pd

def batch_process(manifest: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    fails = []
    for row in manifest[manifest.modality == "image"].itertuples():
        src = Path(row.rel_path)
        dst = out_dir / f"{row.unit_id}.jpg"
        try:
            load_for_model(str(src)).save(dst, quality=90)
        except Exception as e:               # corrupt file? partial download?
            fails.append({"unit_id": row.unit_id, "error": repr(e)})
    report = pd.DataFrame(fails)
    report.to_parquet("data/manifests/preprocess-failures.parquet")
    return report
```

Quarantine, never crash: one corrupt JPEG must not cost you the batch, but
must appear in a report you actually read before indexing.

## Exercises

1. Run `parity_check` on five images with (a) your pipeline, (b) the same
   but with ImageNet mean/std. Report both max-diffs; explain the failure.
2. Extend `load_for_model` to preserve aspect ratio: resize shortest side to
   224 then center-crop. Re-run parity — does the processor agree? (Read the
   processor's `image_processor` config to check its `do_center_crop`.)
3. Take three screenshots with dark mode UI. Compare `flatten_rgb` white vs
   black backgrounds by encoding both with CLIP and ranking against the text
   "dark mode user interface". Which background wins, and why does that
   matter for scans of printed pages?

## Pitfalls

- `resize` without an explicit filter — PIL versions changed defaults (bicubic vs nearest).
- Parity check on one image only — aspect-ratio-dependent bugs hide in portrait shots.
- Saving processed JPEGs at quality 60 to "save space" — you are training/encoding on compression artifacts you injected.

## Resources

- CLIP preprocessing constants: `openai/clip-vit-base-patch32` `preprocessor_config.json` on the Hub.
- PIL documentation: `ImageOps.exif_transpose`, `Image.resize` resampling filters.
