# Phase 3 — Advanced Extensions (Beyond the Official 16 Weeks)

> The official GEF C7 curriculum covers Weeks 0–16 (Weeks 17–24 of the program are the student capstone phase). This phase **extends beyond it** with 10 supplementary deep-dive weeks — the production/research topics practitioners need that the 16 weeks could not fit. Each week follows the same study-guide format as `doc/Phase-1-24-Week-Plan/`.

## The extension weeks

| # | Folder | Topic | Builds on |
|---|---|---|---|
| E1 | [Week-17-Advanced-Fine-Tuning-DPO-RLHF-Distillation](Week-17-Advanced-Fine-Tuning-DPO-RLHF-Distillation/) | DPO, RLHF pipeline, distillation, embedder/reranker fine-tuning | W16-04 LoRA |
| E2 | [Week-18-GraphRAG-Knowledge-Graphs-Long-Context](Week-18-GraphRAG-Knowledge-Graphs-Long-Context/) | Knowledge graphs, GraphRAG, long-context strategies | W4–6 RAG |
| E3 | [Week-19-Code-Web-Agents](Week-19-Code-Web-Agents/) | SWE-agent patterns, browser automation, computer use | W10–13 agents |
| E4 | [Week-20-Vision-Deep-Dive](Week-20-Vision-Deep-Dive-Detection-Document-AI/) | Detection/segmentation (SAM/DETR), document AI/OCR | W7–9 multimodal |
| E5 | [Week-21-Audio-Production](Week-21-Audio-Production-Diarization-TTS/) | Diarization, TTS/voice cloning, realtime voice in production | W8/W11 audio |
| E6 | [Week-22-Advanced-Inference-Decoding](Week-22-Advanced-Inference-Decoding/) | Speculative decoding, grammar-constrained output, GGUF ecosystem | W15-03 serving |
| E7 | [Week-23-Security-Red-Teaming](Week-23-Security-Red-Teaming/) | OWASP deep dive, jailbreak taxonomy, red-team automation | W3-02/W5-04 |
| E8 | [Week-24-LLMOps-Scale](Week-24-LLMOps-Scale/) | Registries, prompt CI/CD, A/B + shadow, cost management, OTel | W15 |
| E9 | [Week-25-Memory-Long-Term-Agents](Week-25-Memory-Long-Term-Agents/) | Memory architectures, semantic caching, persistent memory | W10-02 |
| E10 | [Week-26-Specialization-Benchmark-Literacy](Week-26-Specialization-Benchmark-Literacy/) | Benchmark literacy, interpretability basics, research workflow | everything |

## How to use this phase

- **Pick by need, not order** — each week is self-contained; the "Builds on" column tells you the prerequisites to skim.
- Every week follows the W1–16 format: index README → topic files → practice build, with runnable examples, exercises, pitfalls, and resources.
- Framework APIs were verified against current docs where noted; re-verify before production use (APIs move faster than course content).
- These weeks are **supplementary** — the official program's W17–24 capstone phase is the student's project work; treat an extension week as parallel study when the capstone touches the same topic (e.g., E7 while hardening capstone security).
