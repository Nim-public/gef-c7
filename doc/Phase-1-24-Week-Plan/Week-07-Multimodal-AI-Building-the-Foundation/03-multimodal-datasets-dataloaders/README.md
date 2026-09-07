# Deep-Dive: Multimodal Datasets & DataLoaders

Parent overview: [`../03-multimodal-datasets-dataloaders.md`](../03-multimodal-datasets-dataloaders.md)

The overview introduced Dataset classes and `collate_fn`. This subfolder is
the working edition: a Hub dataset tour with real load calls, custom Dataset
patterns that avoid the four classic traps, DataLoader tuning with measured
throughput, and video frame sampling inside `__getitem__` without killing
your workers.

## File map

| File | What it covers |
|---|---|
| [`01-dataset-tour.md`](01-dataset-tour.md) | COCO, Flickr30k, VQA, AudioCaps, MSR-VTT — load calls and gotchas |
| [`02-custom-dataset-classes.md`](02-custom-dataset-classes.md) | Lazy decode, dict returns, the four classic traps |
| [`03-dataloader-tuning.md`](03-dataloader-tuning.md) | Workers, pinning, prefetch, batch shapes — measured |
| [`04-video-in-dataset.md`](04-video-in-dataset.md) | Frame sampling inside `__getitem__`, worker-safe decode |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-dataset-tour.md` — know what exists before building your own.
2. `02-custom-dataset-classes.md` — the patterns you will copy.
3. `03-dataloader-tuning.md` — make it fast, then keep it correct.
4. `04-video-in-dataset.md` — the hard case, done carefully.

## Prerequisites

- [`../02-modality-processing-pipelines/`](../02-modality-processing-pipelines/) —
  these pipelines are what your Dataset classes will call.
- Week 04 (embedding pipelines) for why throughput matters.
