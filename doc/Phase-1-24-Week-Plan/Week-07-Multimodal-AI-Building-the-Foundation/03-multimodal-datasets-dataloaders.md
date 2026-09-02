# 03 — Multimodal Datasets & DataLoaders

> Week 7 index: [README.md](README.md)

**Session 2 topics:** *Popular Multimodal Datasets Exploration: Efficient Data Loading, Text Preprocessing, Video Frame Processing, Custom Dataset Classes, DataLoader Configuration.*

---

## What you'll learn

- The landmark multimodal datasets (what each is *for*)
- Streaming/lazy loading so media never explodes your RAM
- Custom `Dataset` classes returning clean dicts, with `collate_fn` for variable-length data
- `DataLoader` configuration: workers, pinning, batching — and profiling it

## 1. The dataset tour

| Dataset | Modalities | Scale | Use |
|---|---|---|---|
| **COCO Captions** | image ↔ 5 captions | 330k images | captioning benchmark, detection |
| **Flickr30k** | image ↔ captions | 31k | captioning/retrieval, smaller/faster |
| **VQAv2** | image + question → answer | 265k | visual question answering |
| **AudioCaps / Clotho** | audio ↔ captions | ~50k/6k clips | audio captioning/retrieval |
| **LAION-5B** | image-text (web) | 5B pairs | CLIP-style pretraining (noisy!) |
| **MSVD / MSR-VTT** | video ↔ text | 80k/10k clips | video-text retrieval, captioning |
| **LibriSpeech** | audio ↔ transcripts | 960h | ASR training/eval |
| **WIT / Multi30k** | image ↔ multilingual text | 33k–10M | cross-lingual retrieval |

 HF wrapper: `load_dataset("HuggingFaceM4/COCO", split="train", streaming=True)` — the **viewer** on the Hub is the fastest way to inspect schema + samples before committing to a download.

```python
from datasets import load_dataset

ds = load_dataset("nlphuji/flickr30k", split="test[:500]")   # small slice
ds.features                                                  # image decodes lazily
ex = ds[0]
ex["image"].size, ex["caption"][0]
```

`datasets` stores media as Arrow + lazy-decodes images/audio only on access — a 50 GB image dataset streams over a 16 GB laptop (with `streaming=True` it doesn't even download fully).

## 2. Custom Dataset classes

The contract: `__init__` (paths/manifest), `__len__`, `__getitem__` (one sample as a dict of tensors). Build it on the manifest pattern from file 01:

```python
import json
import torch
from torch.utils.data import Dataset
from PIL import Image, ImageOps

class ImageCaptionDataset(Dataset):
    def __init__(self, manifest_path: str, processor, max_text=64, train=False):
        self.rows = [json.loads(l) for l in open(manifest_path, encoding="utf-8")]
        self.processor, self.max_text, self.train = processor, max_text, train

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        row = self.rows[idx]
        img = Image.open(row["image_path"])
        img = ImageOps.exif_transpose(img).convert("RGB")
        caption = row["captions"][0].lower().strip()      # text preprocessing lives here
        out = self.processor(images=img, text=caption,
                             truncation=True, max_length=self.max_text,
                             return_tensors="pt")
        return {**{k: v.squeeze(0) for k, v in out.items()}, "id": row["id"]}
```

Design rules that matter at scale:

- **Lazy decoding** — open/decode inside `__getitem__`, never in `__init__` (10k PIL objects = OOM)
- **Do preprocessing per-sample, not pre-baked**, unless disk I/O is the bottleneck (then cache processed tensors with a version tag)
- **Dicts, not tuples** — downstream code stays readable; keys = modality names

## 3. Variable lengths and `collate_fn`

Images resize to a fixed shape; text does not. Collation is where you resolve that:

```python
from torch.nn.utils.rnn import pad_sequence

def collate(batch):
    input_ids = pad_sequence([b["input_ids"] for b in batch],
                             batch_first=True, padding_value=0)
    attention_mask = pad_sequence([b["attention_mask"] for b in batch],
                                  batch_first=True, padding_value=0)
    pixel_values = torch.stack([b["pixel_values"] for b in batch])
    return {"input_ids": input_ids, "attention_mask": attention_mask,
            "pixel_values": pixel_values, "ids": [b["id"] for b in batch]}
```

This is the Week 1 padding/attention-mask lesson (file 01-03), now at dataset level: padding without masks = attention on garbage.

## 4. DataLoader configuration

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset, batch_size=32, shuffle=True,        # shuffle=False + deterministic for eval
    num_workers=4,                                # decode in parallel processes
    pin_memory=True,                              # faster CPU→GPU copies (GPU only)
    collate_fn=collate, persistent_workers=True,
)
```

| Knob | Effect | Guidance |
|---|---|---|
| `batch_size` | memory ↑, throughput ↑ to a point | largest that fits; watch OOM |
| `num_workers` | parallel decode | 2–8; 0 makes decode the bottleneck |
| `pin_memory` | faster H2D copies | GPU only |
| `shuffle` | train yes / eval no | eval needs order for metrics |
| `prefetch_factor` | workers queue depth | tune when GPU starves |

**Profile, don't guess**: if GPU util < 50%, the loader is the bottleneck — raise workers, cache decoded tensors, or resize images once at ingest (store `224px` derivatives).

## 5. Video frame processing inside a Dataset

```python
class VideoTextDataset(Dataset):
    def __getitem__(self, idx):
        row = self.rows[idx]
        frames = sample_frames(row["video_path"], n_frames=8)   # file 02 §4
        feats = torch.stack([torch.from_numpy(f) for f in frames])
        return {"video": feats, "text": row["caption"], "id": row["id"]}
```

Decode cost dominates: sample *fewer frames* (8–16), cache sampled frames to disk as tensors on first pass, and keep videos out of git (manifest + path pattern, always).

## Exercises

1. Stream 200 Flickr30k samples; profile: decode time vs total step time with `num_workers=0, 2, 4`. Where's the plateau?
2. Write `collate` + a `Dataset` over your own manifest (file 01 exercise 2); batch 16 and assert every tensor's shape and every id's uniqueness.
3. Video: build `VideoTextDataset` over 5 short clips; report per-sample decode time and RAM high-water (psutil). Would `batch_size=32` fit your RAM? Show the math.
4. Text preprocessing slice: distribution of caption lengths in Flickr30k; set `max_text` to cover 95% — what truncation rate do you accept and why?
5. Cache experiment: convert 100 images to preprocessed tensors once, then compare epoch time (raw decode vs cached). When does pre-caching pay off?

## Pitfalls

- **Decoding in `__init__`** — OOM at 10k items; decode lazily in `__getitem__`
- **`num_workers>0` with lambdas/closures** — pickling errors; keep datasets picklable (plain classes, paths)
- **Random augs in eval loaders** — nondeterministic metrics; a separate eval transform set
- **Forgetting `pin_memory`/GPU device transfers per batch** — `.to("cuda", non_blocking=True)` in the loop
- **Media in git** — manifests yes, bytes no

## Resources

- PyTorch [Datasets & DataLoader guide](https://pytorch.org/tutorials/beginner/basics/data_tutorial.html) + [Writing custom datasets](https://pytorch.org/tutorials/recipes/recipes/custom_dataset_transforms_loader.html)
- HF [datasets streaming](https://huggingface.co/docs/datasets/stream) + [process](https://huggingface.co/docs/datasets/process) docs
- HF Course ch. 5 (the datasets library deep dive)
- decord / torchvision.io for faster video decode — read once you outgrow OpenCV
