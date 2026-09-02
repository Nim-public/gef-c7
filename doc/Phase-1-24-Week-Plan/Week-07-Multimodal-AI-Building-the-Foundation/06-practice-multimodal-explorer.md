# 06 — Practice: Multimodal Dataset Explorer & Alignment Audit

> Week 7 index: [README.md](README.md) · **Due: before Week 8 (by 24 Oct)**

*(No formal task row in the schedule for Week 7 — this practice build is the recommended hands-on. It directly feeds Week 9's multimodal RAG and your capstone's multimodal scope.)*

---

## 1. Deliverable

```
multimodal/
  explorer.py            # CLI or Gradio dataset explorer
  alignment.py           # manifest builder + validation + report (file 04)
  manifest.jsonl         # your aligned dataset records
  validation_report.jsonl
  README.md              # findings: modality inventory, validation stats, metrics demo
```

Demo: explore a real multimodal dataset (Flickr30k slice or your capstone's media), audit alignment, and show one BLEU + one CLIPScore evaluation.

## 2. Part A — Dataset explorer

Load either `nlphuji/flickr30k` (500-sample slice) or your own media manifest, then present per modality:

- **Inventory table**: count, formats, sizes (dimensions/duration), modes/encodings found (file 02's audit)
- **Sample viewer**: Gradio `gr.Gallery`/`gr.Image` + captions side by side (10 samples)
- **Text stats**: caption length distribution, unique-word coverage

This is Week 1's profiling habit, extended to media.

## 3. Part B — Alignment audit

Run the file 04 pipeline over your manifest:

1. Reference resolution (try-open every asset; fingerprint each)
2. Pairing validation (≥1 caption per image; caption length floor; duration checks if audio)
3. Missing-data report: rows dropped per reason code (flagged, not silent)
4. Output: `aligned.jsonl` + `validation_report.jsonl` + stats block

Numbers to capture in `README.md`: assets in → pairs ok → dropped (with top 3 failure codes).

## 4. Part C — Metrics mini-run (file 05 in action)

- **BLEU**: 10 generated vs reference captions (BLIP captions or hand-written variants); report BLEU-1/4 and one *analysis sentence per mismatch* (synonym? missing detail?)
- **CLIPScore**: same 10 pairs; correlate your intuition with the scores; find one pair where CLIPScore and BLEU disagree — explain why both matter
- **Retrieval R@k** (stretch): 20 images × their captions through CLIP → R@1/5/10 + MedR using file 05's `retrieval_metrics`

## 5. Capstone integration (write into README)

1. **Modality inventory** (file 01 ex. 1): what exists today, volumes, formats
2. **First multimodal target**: which modality adds most value to your RAG, and which Week 9 pattern (caption-then-index vs CLIP joint vs VLM) you're aiming for
3. **Alignment risks** found in Part B that would block Week 9

## 6. Rubric

- [ ] Explorer runs on a real dataset (not toy arrays); sample viewer works
- [ ] Alignment pipeline produces both output files with stats
- [ ] Missing-data policy table present (per modality)
- [ ] BLEU + CLIPScore computed on the same 10 pairs with analysis
- [ ] Capstone section: modality inventory + chosen Week 9 pattern
- [ ] All media referenced by manifest paths — zero media files in git

Bring the validation stats to Office Hours (22 Oct): the interesting discussion is always in the *dropped rows* — each one is a Week 9 pipeline edge case in disguise.
