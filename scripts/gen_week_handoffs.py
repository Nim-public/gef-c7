#!/usr/bin/env python3
"""Generate handoff.md for every week folder (core W1-16 + extensions E1-E10).

Each handoff.md briefs a fresh agent session to expand every NN-*.md topic file
into its own subfolder containing multiple, more detailed files.

Usage:
    py scripts/gen_week_handoffs.py            # write/refresh all handoffs
    py scripts/gen_week_handoffs.py --dry-run  # show plan without writing
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN_ROOTS = [ROOT / "doc" / "Phase-1-24-Week-Plan",
              ROOT / "doc" / "Phase-3-Advanced-Extensions"]

# ---------------------------------------------------------------------------
# Per-file expansion plans: week-folder-name -> {topic-file: [expansion bullets]}
# Bullets are expansion directions; the next session turns each group of
# bullets into the deep-dive files of the subfolder.
# ---------------------------------------------------------------------------

PLANS = {
 # ---------------------------- CORE: WEEK 01 -------------------------------
 "Week-01-Text-Data-LLM-Foundations": {
  "01-tokenization-and-text-representation.md": [
   "Word vs character vs subword tokenization — with a from-scratch BPE trainer, merge visualizations, and vocabulary-size experiments",
   "Special tokens & attention masks — padding strategies, chat templates, per-model differences, padding-without-mask failure demos",
   "One-hot / multi-label encodings — sklearn encoders, sparse-vector problems, where embeddings must replace them",
   "Embeddings & similarity visualization — cosine vs dot vs L2, PCA/UMAP on a real corpus, toy-vector geometry labs",
   "Tokenizer API deep-dive — tiktoken vs HF tokenizers vs tokenizers-lib, cost accounting, multilingual/emoji edge cases",
  ],
  "02-string-manipulation-and-regex.md": [
   "String methods mastery lab — immutability, slicing, split/join pipelines, Counter-based corpus analysis with edge cases",
   "f-strings as prompt templating — formatting specs, nested templates, escaping rules, a render_prompt utility",
   "Unicode deep dive — code points vs bytes, NFC/NFKC, normalization bugs, multilingual cleaning pipeline",
   "Regex fundamentals — the four re functions, 20 worked patterns, greedy vs lazy, compile/VERBOSE",
   "Regex applied — PII extraction, cleaning pipelines, sentence-aware chunk splitting, validation guardrails",
  ],
  "03-pandas-structured-data.md": [
   "DataFrames from zero — Series/dtypes, loading, the first-look ritual, memory basics",
   "Selection & indexing — loc/iloc/at/iat, chained-indexing traps, copy-on-write",
   "Filtering & vectorization — boolean masks, isin/between/str, query(), vectorized column creation",
   "Aggregation — groupby mechanics, named agg, pivot_table, crosstab, time resampling",
   "Joins — merge kinds, validate, suffixes, concat; the join sanity-check ritual",
   "Missing data & dtypes — dropna/fillna policies, dtype surprises, mini-project with tests",
  ],
  "04-file-handling-and-web-crawling.md": [
   "File I/O done right — pathlib, encoding, globbing, corpus manifests",
   "CSV deep dive — dialects, dtypes, chunked streaming, when CSV is the wrong format",
   "JSON & JSONL — nesting, json_normalize, append-friendly datasets, round-trip losses",
   "PDF extraction — pypdf vs pdfplumber vs OCR, layout traps, quality auditing",
   "Web crawling — requests+BS4 loop, robots/ethics, retries/backoff, caching raw HTML",
   "End-to-end corpus builder — crawl → clean → JSONL → pandas project",
  ],
  "05-ml-fundamentals.md": [
   "The ML definition — features/labels/examples, the f(x;θ) loop with diagrams",
   "Task taxonomy — classification/regression/generation, losses per task, worked examples",
   "Gradient descent from scratch — the 12-line loop, LR sweeps, convergence behavior",
   "Evaluation discipline — splits, stratification, metric selection, confusion matrices by hand",
   "Text classification hands-on — TF-IDF ticket router, error analysis, baseline discipline",
   "Overfitting/underfitting — diagnosis plots, regularization, the test-set rules",
  ],
  "06-from-neural-networks-to-llms.md": [
   "Neural network mechanics — neurons, activations, parameter counting in PyTorch",
   "The training loop traced — forward/loss/backward/step on a real model",
   "Embeddings as learned representations — from one-hot to semantic space",
   "The Transformer at 10,000 ft — attention, context window, encoder vs decoder",
   "Pre-training vs instruction tuning — behavior comparison labs",
   "Model selection — reading cards, size/memory math, license checks",
  ],
  "07-llm-concepts-and-demos.md": [
   "Chat completions deep dive — roles, usage accounting, cost per call",
   "Multi-turn state management — history lists, trimming, summarization, cost growth",
   "Sampling controls — temperature/top_p/max_tokens experiments with plots",
   "Log probabilities — confidence, zero-shot classification, routing signals",
   "Streaming & autoregressive generation — the token loop made visible",
   "Pre-training → SFT → RLHF — what each stage changes, with demos",
  ],
  "08-capstone-task-formalize-scope.md": [
   "Scope document workshop — template walkthrough with a fully worked example",
   "Data requirements deep dive — sources, volume, licensing, PII, label needs",
   "Feasibility analysis — checks, red flags, go/no-go decisions",
   "Dataset sourcing lab — HF/Kaggle/gov/crawling hands-on with licensing notes",
   "Mentor-pitch preparation — the 5-slide version of the scope",
  ],
 },
 # ---------------------------- CORE: WEEK 02 -------------------------------
 "Week-02-Hugging-Face-Models": {
  "01-huggingface-platform.md": [
   "Hub anatomy — models/datasets/spaces, discovery filters, trending signals",
   "Model-card critical reading — license/data/limitations checklist applied to 3 models",
   "huggingface_hub programmatic access — download, cache, pin revisions, auth",
   "Datasets library — load/stream/process, memory-mapped large data",
   "Spaces — study, fork, publish a Gradio demo",
  ],
  "02-ready-to-use-models.md": [
   "pipeline() anatomy — tokenizer+model+postprocess, batching, device placement",
   "Sentiment analysis — score semantics, domain shift, the sanity-test protocol",
   "NER — token classification, aggregation, PII masking composition",
   "Zero-shot classification — NLI mechanics, hypothesis templates, label wording",
   "Encoder vs LLM-API decision framework — latency/cost/determinism benchmarks",
  ],
  "03-nlp-tasks.md": [
   "Summarization — BART family, length controls, chunk-map-reduce for long docs",
   "Extractive QA — spans, scores, the retrieval sandwich",
   "Generative QA — text2text, hallucination measurement",
   "Translation — MarianMT/NLLB, back-translation quality checks",
   "Sentence embeddings — similarity, dedup, semantic search patterns",
  ],
  "04-modern-models.md": [
   "CLIP — zero-shot classification and raw embeddings for retrieval",
   "Whisper — model tiers, timestamps, translation, telephony audio",
   "Local LLM generation — chat templates, max_new_tokens, small-model roster",
   "Diffusion — pipeline components, guidance/steps/seeds",
   "Hardware planning — params→GB math, quantization preview, tier routing",
  ],
  "05-small-language-models.md": [
   "SLM landscape — Qwen/Llama/Phi/Gemma/SmolLM families and licenses",
   "Local serving — transformers vs Ollama vs LM Studio, OpenAI-compatible endpoints",
   "Quantization basics — 4-bit trade-offs, GGUF previews",
   "SLM vs API decision table — cost/latency/privacy measurements",
  ],
  "06-capstone-task-huggingface-integration.md": [
   "Task selection — the matrix applied to your capstone",
   "Model selection protocol — shortlist, widget tests, pinning",
   "Mini-eval design — 20 examples, pass criteria, failure notes",
   "Integration seam — function contracts and pipeline position",
  ],
 },
 # ---------------------------- CORE: WEEK 03 -------------------------------
 "Week-03-Prompt-Engineering-Transformer-Models": {
  "01-prompt-engineering-basics.md": [
   "Zero-shot precision — format/role/boundary contracts, weak-vs-strong rewrites",
   "Few-shot design — example selection, ordering, diversity, token budget",
   "Chain-of-thought — reasoning tokens, cost math, hidden-CoT JSON pattern",
   "Prompt chaining — pipelines, seam validation, retry design",
   "Meta prompting — critique loops, generated prompts under test",
   "Multimodal prompting — image+text contracts, no-dialog fallbacks",
   "Variables & templating — f-string hygiene, escaping, validation",
  ],
  "02-system-prompts-testing-injection.md": [
   "System prompt anatomy — the 7 sections with a full worked constitution",
   "Multi-turn engineering — Chat class, trimming, re-injection patterns",
   "Studying production prompts — component classification exercise",
   "Prompt assembly & management — files, git, render assertions",
   "Testing prompts — pytest batteries, determinism, flakiness notes",
   "Prompt injection — families, layered defenses, bypass catalog",
  ],
  "03-neural-network-training.md": [
   "Weights/biases/activations — by-hand forward pass, parameter counting",
   "Loss functions — MSE/cross-entropy with worked numbers",
   "Backpropagation — chain rule through a 2-layer net, autograd verification",
   "Optimizers — SGD→momentum→Adam experiments and diagnosis",
   "LR schedules & stability — warmup, clipping, spike diagnosis",
  ],
  "04-transformer-step-by-step.md": [
   "Pipeline orientation — text→tokens→embeddings→blocks→logits",
   "Self-attention by hand — Q/K/V on 4 tokens, scaled dot-product",
   "Causal masking — decoder vs encoder behavior",
   "Multi-head attention & the block — residuals, FFN, layer norm",
   "Reading a real model — architecture print walkthrough, param reconciliation",
  ],
  "05-techniques-comparison.md": [
   "The six levers — what each changes, costs, and when to pull",
   "RAG vs fine-tuning — fact-rot case studies",
   "Routing vs agentic — decision boundaries",
   "Optimization catalog — caching/batching/routing preview",
   "Capstone decision memo — levers chosen with reasons",
  ],
  "06-capstone-task-conversational-bot.md": [
   "Bot architecture — ChatBot class, trimming, usage logging",
   "Constitution design — sections, leak-testing, iteration",
   "Translation designs — cascade vs native, trade analysis",
   "Test battery — pytest with injection/off-domain/empty cases",
   "Demo & rubric — transcript, refusal, escalation evidence",
  ],
 },
 # ---------------------------- CORE: WEEK 04 -------------------------------
 "Week-04-Building-the-Retrieval-Foundation": {
  "01-rag-fundamentals.md": [
   "LLM limitations taxonomy — cutoff, private data, hallucination, provenance, window",
   "The two pipelines — ingestion and query, component responsibilities",
   "Grounded generation — the citation/insufficiency prompt contract",
   "RAG vs alternatives — when fine-tuning/prompting/long-context win",
   "Insufficiency testing — the no-answer battery",
  ],
  "02-chunking-strategies.md": [
   "Fixed-size chunking — implementation, overlap math, failure modes",
   "Recursive splitting — separators, tuning, langchain splitters",
   "Structure-aware chunking — markdown headers, tables, code",
   "Size/overlap sweeps — the hit-rate methodology on your corpus",
   "Metadata design — ids, sources, permissions, freshness",
  ],
  "03-embeddings-vector-databases.md": [
   "Brute-force baseline — numpy search and its limits",
   "FAISS flat — exact search as eval ground truth",
   "FAISS IVF — nlist/nprobe, recall-vs-speed sweeps",
   "LanceDB — tables, metadata filters, prefilter security",
   "Metric choice — cosine/L2/IP and normalization discipline",
  ],
  "04-search-keyword-vs-semantic.md": [
   "BM25 mechanics — scoring, tokenization, rank_bm25 hands-on",
   "Semantic search — embeddings, nearest neighbors, thresholds",
   "Evaluation harness — 25 queries, hit-rate@k design",
   "RRF hybrid fusion — implementation, k-sensitivity",
   "Failure taxonomy — identifiers, paraphrase, negation cases",
  ],
  "05-capstone-task-search-engine.md": [
   "Ingestion engineering — resumable, incremental, dedup-safe",
   "Search service design — hybrid+filters+thresholds behind one function",
   "Eval set construction — the 25-query methodology",
   "Failure analysis — categories, diagnoses, fixes",
  ],
 },
 # ---------------------------- CORE: WEEK 05 -------------------------------
 "Week-05-Advanced-Retrieval-Evaluations-Chatbots": {
  "01-advanced-chunking.md": [
   "Semantic chunking — similarity boundaries, threshold calibration",
   "Content-aware chunking — tables, Q&A pairs, code blocks",
   "Contextual headers — section-path prepending, measured uplift",
   "Measurement — harness comparisons, when NOT to upgrade",
  ],
  "02-embedding-models.md": [
   "Dense landscape — MiniLM/mpnet/E5/BGE characteristics",
   "API embedders — OpenAI/Cohere pricing and egress trade-offs",
   "Sparse models — ELSER and learned-term expansion",
   "Prefix requirements — E5/BGE pitfalls, measured impact",
   "The bake-off — shared harness, per-model tables",
  ],
  "03-hybrid-filtering-fusion-reranking.md": [
   "Metadata filtering — prefilter vs postfilter, permission patterns",
   "RAG fusion — multi-query expansion, dedup, noise guards",
   "Cross-encoder reranking — two-stage retrieval, latency math",
   "Reference architecture — staged pipeline with ablations",
  ],
  "04-rag-chatbot-guardrails.md": [
   "Chatbot assembly — retriever + bot integration per turn",
   "Input guardrails — screening, PII, caps, trip logging",
   "Output guardrails — citation validation, refusals, regeneration",
   "Responsible AI — grounding, escalation, privacy layers",
  ],
  "05-response-evaluation-explanations.md": [
   "Ragas four metrics — definitions and diagnosis table",
   "Local runs — dataset construction from logs",
   "Slice-level analysis — per route/doc type",
   "Explanation levels — citations → transparency → self-checks",
  ],
  "06-capstone-task-rag-chatbot.md": [
   "Assembly — turn() pipeline with per-stage latency",
   "Eval slices — per-route Ragas tables",
   "Safety battery — injection/off-domain/PII through the graph",
   "Failure analysis — worst trajectories dissected",
  ],
 },
 # ---------------------------- CORE: WEEK 06 -------------------------------
 "Week-06-RAG-for-Tabular-Data": {
  "01-rdbms-sql-fundamentals.md": [
   "Relational modeling — tables, keys, constraints with justification",
   "SQL families — DDL/DML/DQL hands-on in SQLite",
   "Joins — inner/left with zero-match cases, COALESCE patterns",
   "Aggregation — groupby/having/subqueries/CTEs, 8-query ladder",
   "pandas↔SQL bridge — read_sql/to_sql workflows",
  ],
  "02-database-choices.md": [
   "SQLite vs MySQL vs Postgres — decision heuristics and dialect diffs",
   "Storage coexistence — relational + vector + graph map",
   "Read-only safety — users, modes, allow-lists",
   "Environment ladder — dev/staging/prod data policies",
  ],
  "03-rag-over-structured-data.md": [
   "Schema prompts — generated-from-DB, dialect rules, date grounding",
   "Validation layers — allow-lists, read-only, row caps",
   "Repair loops — error feedback retries",
   "Result formatting — grounded answers with SQL audit lines",
  ],
  "04-csv-json-hybrid-retrieval.md": [
   "The decision tree — SQL vs paste vs hybrid per data shape",
   "Row serialization — row-major text, summary chunks",
   "Router design — rules then zero-shot then agent",
   "Cross-store joins — ids linking chunks and rows",
  ],
  "05-capstone-task-structured-retrieval.md": [
   "Schema and ingestion — constraints, synthetic data discipline",
   "Text2SQL eval — gold-SQL methodology",
   "Router implementation — rules+classifier, logged decisions",
   "Safety battery — write-probe, multi-statement, PII probes",
  ],
 },
 # ---------------------------- CORE: WEEK 07 -------------------------------
 "Week-07-Multimodal-AI-Building-the-Foundation": {
  "01-multimodal-ai-landscape.md": [
   "Modality comparison — representation, cost, tasks, model families",
   "Representation levels — raw/processed/embeddings storage strategy",
   "Metadata handling — manifests, EXIF, provenance, permissions",
   "The modality gap — bridges overview and capstone inventory",
  ],
  "02-modality-processing-pipelines.md": [
   "Image pipeline — load/EXIF/convert/normalize, processor parity checks",
   "Audio pipeline — resample, mel spectrograms, whisper features",
   "Video pipeline — frame sampling, decode costs, keyframes",
   "Preprocessing determinism — seeded augs, validation-by-eye",
  ],
  "03-multimodal-datasets-dataloaders.md": [
   "Dataset tour — COCO/Flickr/VQA/AudioCaps/video sets on the Hub",
   "Custom Dataset classes — lazy decode, dicts, collate functions",
   "DataLoader tuning — workers, pinning, batch shapes",
   "Video-in-dataset — frame sampling inside __getitem__",
  ],
  "04-data-alignment-synchronization.md": [
   "Temporal alignment — subtitles↔frames↔audio on one clock",
   "Cross-modal validation — automated integrity checks",
   "Missing-data policies — drop/impute/flag tables",
   "Alignment pipeline — manifests, versioning, reports",
  ],
  "05-evaluation-metrics-benchmarks.md": [
   "BLEU by hand — n-gram precision, brevity penalty, clipping",
   "CLIPScore — semantic caption evaluation implementation",
   "Retrieval metrics — R@1/5/10, MedR, both directions",
   "Benchmark tour — COCO/VQA/AudioCaps/MSR-VTT mapping",
  ],
  "06-practice-multimodal-explorer.md": [
   "Explorer build — dataset stats and Gradio viewer",
   "Alignment audit — validation report generation",
   "Metrics demo — BLEU + CLIPScore on real pairs",
   "Capstone modality inventory — scope integration",
  ],
 },
 # ---------------------------- CORE: WEEK 08 -------------------------------
 "Week-08-Encoding-Modalities-Real-World-Architectures": {
  "01-encoding-text-images.md": [
   "Text encoder template — tokens→embeddings→pooled vectors",
   "CNN mechanics — convolution/pooling/receptive fields by hand",
   "ViT — patches as tokens, token-count math, position embeddings",
   "CNN vs ViT — inductive bias, data hunger, compute trade-offs",
  ],
  "02-encoding-audio-video.md": [
   "Spectrograms — STFT/mel/log with librosa labs",
   "Raw-audio encoders — wav2vec2/HuBERT frame embeddings",
   "RNNs — LSTM/GRU sequence encoding and limits",
   "Video — frame pooling, 3D CNNs, tubelet tokens",
  ],
  "03-modality-fusion.md": [
   "Early fusion — concat classifiers and missing-modality ablations",
   "Intermediate fusion — cross-attention mechanics and maps",
   "Late fusion — ensembles, calibration, graceful degradation",
   "The LLaVA projection pattern — vision into LLM context",
  ],
  "04-clip-blip-architectures.md": [
   "CLIP loss — the N×N matrix by hand and in code",
   "Zero-shot classification — prompt ensembles, logit reading",
   "BLIP objectives — ITC/ITM/LM and capabilities",
   "Decision guide — CLIP vs BLIP vs VLM per job",
  ],
  "05-diffusion-architectures.md": [
   "Forward/reverse processes — noise schedules by hand",
   "Latent diffusion — VAE, U-Net/DiT, cross-attention conditioning",
   "Pipeline anatomy — components, knobs, safety checker",
   "Deterministic generation — seeds, steps, guidance sweeps",
  ],
  "06-practice-encoding-lab.md": [
   "Geometry comparison — ResNet vs ViT on your domain",
   "CLIP matrix + retrieval metrics on your pairs",
   "Fusion ablation experiments — missing-modality robustness",
   "Encoder decision note — capstone integration",
  ],
 },
 # ---------------------------- CORE: WEEK 09 -------------------------------
 "Week-09-RAG-with-Image-Video-Audio": {
  "01-gradio-multimodal-apps.md": [
   "Gradio model — Interface/Blocks/events/queue",
   "Food image generator — diffusion app with controls",
   "Product cataloger — CLIP+BLIP+SQLite composition",
   "Deployment — local/Spaces/behind-API patterns",
  ],
  "02-lancedb-multimodal.md": [
   "Multi-vector tables — text+image columns, per-column search",
   "IVF-PQ — product quantization mechanics and knobs",
   "Recall/speed sweeps — nprobe/refine against flat",
   "Native hybrid search — FTS+vector RRF",
  ],
  "03-multimodal-rag-patterns.md": [
   "Traditional RAG review — the contract restated",
   "Pattern 1 — caption-then-index trade-offs",
   "Pattern 2 — unified embedding spaces",
   "Pattern 3 — VLM generation economics",
   "Pattern selection — the routing table",
  ],
  "04-end-to-end-multimodal-rag.md": [
   "Ingestion — captions+embeddings+region chunks to LanceDB",
   "Hybrid retrieval — cross-space fusion with filters",
   "VLM generation — image-grounded cited answers",
   "Cost/latency ledger — per-stage measurement",
  ],
  "05-practice-multimodal-rag.md": [
   "Corpus prep — manifests, captions, crops",
   "Three-store indexing — chunks/fields/crops",
   "Router + safety battery — cross-server injection",
   "Eval tables — retrieval + Ragas + latency",
  ],
 },
 # ---------------------------- CORE: WEEK 10 -------------------------------
 "Week-10-Introduction-to-Agentic-AI-MCP": {
  "01-agents-foundations.md": [
   "Agent definition — loop, tools, memory, control-flow transfer",
   "Hand-rolled ReAct loop — the 50-line implementation traced",
   "Demo trajectories — single-tool, multi-tool, impossible",
   "When NOT to use agents — the pipeline boundary",
  ],
  "02-tools-and-memory.md": [
   "Function-calling protocol — schema→decision→execute→observe",
   "ToolRegistry — jsonschema validation, error contracts",
   "Memory taxonomy — history/scratchpad/episodic/semantic",
   "Context budgeting — truncation, compression, per-layer costs",
  ],
  "03-mcp-servers-fastmcp.md": [
   "MCP architecture — hosts/clients/servers/transports",
   "FastMCP server — tools/resources/prompts from decorators",
   "Client batteries — deterministic tests + real-LLM paths",
   "Capstone tool surface — read-only-first design",
  ],
  "04-measuring-agents-patterns.md": [
   "Trajectory instrumentation — logs, tokens, steps per run",
   "Three-dimension metrics — success/efficiency/process",
   "HITL gates — approval design and rates",
   "LLM-as-judge — trajectory scoring and calibration",
  ],
  "05-prompt-context-engineering-agentic.md": [
   "Agentic constitution — the 7-rule system prompt",
   "Observation formatting — errors as instructive prompts",
   "Context fitter — priorities, truncation, paging",
   "Failure phrasing — A/B measured rewording",
  ],
  "06-practice-first-mcp-agent.md": [
   "Agent assembly — loop + registry + MCP tools",
   "Eval set design — 10 tasks with expected routes",
   "Red-team battery integration — injection through tools",
   "Metrics table — the W10-04 harness output",
  ],
 },
 # ---------------------------- CORE: WEEK 11 -------------------------------
 "Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK": {
  "01-agents-sdk-quickstart.md": [
   "SDK anatomy — Agent/Runner/RunResult fields",
   "Loop mechanics — the 4 documented steps, max_turns",
   "Structured output_type — Pydantic final answers",
   "Sessions — SQLite persistence across turns",
   "Tracing — spans, dashboards, local export",
  ],
  "02-tools-handoffs-guardrails.md": [
   "function_tool — schemas from signatures, gating with is_enabled",
   "Handoffs — control transfer, descriptions, last_agent",
   "Input guardrails — tripwires, judge-agents, exceptions",
   "Output guardrails — citation/schema validation",
   "The W3-02 battery mechanized as pytest",
  ],
  "03-multi-agent-orchestration.md": [
   "Handoff pattern — router→specialist topology",
   "Chaining — sequential refinement with typed outputs",
   "Delegation — manager with agents-as-tools",
   "State passing — context, outputs, summaries",
   "Anti-patterns — ping-pong, spirals, bloat",
  ],
  "04-voice-agents.md": [
   "Cascade stack — STT→agent→TTS with budget table",
   "Turn-taking — VAD, endpointing, barge-in",
   "Minimal demo — push-to-talk implementation",
   "Realtime vs cascade — decision and costs",
  ],
  "05-observability-eval-agents.md": [
   "Trace/span model — generation/tool/handoff spans",
   "Replay debugging — failed-run root cause workflow",
   "Export to harness — merged W10-04+trace rows",
   "Regression suites — trajectory assertions",
  ],
  "06-practice-agents-sdk-capstone.md": [
   "Port methodology — W10 agent to SDK primitives",
   "Comparison table — same cases, both implementations",
   "Trace debugging — planted failure root cause",
   "Verdict — lines saved vs capabilities gained",
  ],
 },
 # ---------------------------- CORE: WEEK 12 -------------------------------
 "Week-12-Building-AI-Agents-with-phiData-Agno": {
  "01-agno-introduction.md": [
   "Agno agent structure — model/instructions/tools/knowledge fields",
   "Playground — UI, run history, tool inspection",
   "Framework mapping — W10/W11/W12 completion table",
   "phiData→Agno migration — imports and API notes",
  ],
  "02-knowledge-and-databases.md": [
   "Knowledge bases — LanceDB integration, hybrid search type",
   "Ingestion by source — PDF/CSV/JSON/RDBMS paths",
   "Grounding rules — instructions, insufficiency battery",
   "Dual-pipeline design — knowledge vs SQL tool selection",
  ],
  "03-custom-tools-toolkits.md": [
   "Function tools — schemas from hints and docstrings",
   "Toolkit classes — grouping, scoping, per-task flags",
   "Advanced data tools — charts, schema, verification",
   "Toolkit testing — the client battery toolkit edition",
  ],
  "04-analytics-agent-financial.md": [
   "Prebuilt finance toolkits — YFinance usage and limits",
   "Analytics over your tables — guarded SQL composition",
   "Numeric-hallucination defenses — verification hooks",
   "Reasoning display — audit trails in answers",
  ],
  "05-agentic-rag-with-phidata.md": [
   "Fixed vs agentic RAG — the decision analysis",
   "Three-power agent — toolkit routing design",
   "Route accuracy — measurement vs W6-04 router",
   "Cost/quality trade — token and latency tables",
  ],
  "06-capstone-task-crewai-workflow.md": [
   "CrewAI essentials — roles/tasks/crew/process",
   "Role design — least-privilege specialist split",
   "Process choice — sequential vs hierarchical measured",
   "Comparison vs W11 — same cases table",
  ],
 },
 # ---------------------------- CORE: WEEK 13 -------------------------------
 "Week-13-Building-AI-Agents-with-LangGraph": {
  "01-langgraph-foundations.md": [
   "State design — TypedDict, Pydantic, reducers",
   "Nodes and edges — normal and conditional wiring",
   "Cycles and bounds — retry counters, exit conditions",
   "Invoke/stream/inspect — execution path reading",
  ],
  "02-project-story-generator.md": [
   "Story state — chapters, world, options",
   "The WAIT pattern — human choice pausing",
   "Choice application — world JSON updates with fallback",
   "Transferable pattern — interactive flows generally",
  ],
  "03-project-support-ticket-router.md": [
   "Classification node — structured outputs, reasoning",
   "Escalation edges — urgency gating first",
   "KB/data nodes — W9/W6 capstone integration",
   "Three-way router comparison — rules/handoffs/graph",
  ],
  "04-team-agents-codegen-loop.md": [
   "Self-repair graph — plan/write/test/debug cycle",
   "Sandbox discipline — subprocess/container hardening",
   "Supervisor topology — routing workers",
   "Team vs single — measured A/B",
  ],
  "05-capstone-task-phidata-agent.md": [
   "Agno assembly — toolkits+knowledge in one agent",
   "15 data-intensive cases — design and gold answers",
   "Numeric grounding — verification nodes",
   "Comparison vs W11 — same-case tables",
  ],
  "06-checkpointing-human-in-loop.md": [
   "Checkpointers — threads, durability, storage choice",
   "interrupt_before — approval design and resumes",
   "State editing — human corrections mid-run",
   "Time travel — replay and fork debugging",
  ],
 },
 # ---------------------------- CORE: WEEK 14 -------------------------------
 "Week-14-Advanced-AI-Workflows-with-LangChain-MCP": {
  "01-langchain-foundations.md": [
   "Prompt templates — versioned, validated, file-loaded",
   "LCEL composition — pipelines, streaming, fallbacks/retries",
   "Structured output — Pydantic-validated chains",
   "create_agent — the modern agent API mapped",
  ],
  "02-project-csv-analyzer.md": [
   "Tool surface — profile/pandas/chart with guards",
   "Sandbox discipline — restricted eval, malicious probes",
   "Four features — chat/summary/analyze/visualize wiring",
   "Numeric grounding — numbers_supported checks",
  ],
  "03-project-code-review-agent.md": [
   "Deterministic scan layer — AST/ruff findings",
   "LLM review layer — structured Finding models",
   "Report generation — deterministic severity sort",
   "Diff-aware review — full-file context, line hints",
  ],
  "04-agentic-rag-langchain.md": [
   "Three-source routing — vector/SQL/web agent",
   "Decomposition — sub-question generation",
   "Self-improving loops — logs to eval sets",
   "Graph parity — W13-01 equivalence testing",
  ],
  "05-workflow-assistant-mcp.md": [
   "MCP adapter — multi-server client configuration",
   "Scope containment — paths, tokens, allow-lists",
   "Smart automation — gated cross-server chains",
   "Cross-server injection testing",
  ],
  "06-practice-langchain-mcp.md": [
   "Framework verdict — the 5-framework table",
   "Tool budget and topology decisions",
   "Four pillars end-to-end demos",
   "Regression and safety integration",
  ],
 },
 # ---------------------------- CORE: WEEK 15 -------------------------------
 "Week-15-Production-Grade-Agent-Reliability-Performance-Optimization": {
  "01-reliability-limits-retries-tests.md": [
   "RunBudget — turns/tokens/time/spend aborts",
   "Retry policies — tenacity backoff, budgets, circuit breakers",
   "User contracts — exception→message handler maps",
   "Test pyramid — stubbed unit, contract, integration, soak",
  ],
  "02-tracing-guardrails-langsmith.md": [
   "LangSmith setup — automatic tracing, projects",
   "Datasets & evaluations — hosted regression runs",
   "Platform guardrails — moderation/PII layering",
   "Trace hygiene — PII scrubbing, retention, sampling",
  ],
  "03-inference-optimization.md": [
   "KV cache — prefill/decode memory math",
   "Continuous batching — throughput mechanics",
   "vLLM/SGLang serving — knobs and benchmarks",
   "Serving quantization — AWQ/FP8 trade-offs",
  ],
  "04-prompt-caching-and-routing.md": [
   "Prefix structuring — the stable/variable order rule",
   "Cache verification — cached_tokens in billing",
   "Model routing — rules→classifier→RouteLLM",
   "Threshold calibration — misroute costs both ways",
  ],
  "05-practice-production-hardening.md": [
   "Baseline measurement — W14-06 numbers",
   "Reliability layer — budgets/retries/handlers live",
   "Optimization ledger — attributed improvements",
   "Before/after table — p95, $/task, quality",
  ],
 },
 # ---------------------------- CORE: WEEK 16 -------------------------------
 "Week-16-Evals-and-Fine-Tuning": {
  "01-eval-strategy-ragas.md": [
   "Ragas revision — four metrics, diagnosis patterns",
   "Slice analysis — per route/doc-type tables",
   "Offline vs online — golden sets and live signals",
   "Dataset versioning — immutable, changelog, held-out slices",
  ],
  "02-synthetic-data.md": [
   "Seed expansion — paraphrase/variation generation",
   "Persona grids — coverage cells and weights",
   "Adversarial generation — red-team data at scale",
   "Validation — labels, diversity, leakage, distribution",
  ],
  "03-fine-tuning-fundamentals.md": [
   "SFT data — formatting, masking, distribution matching",
   "Tokenization & loaders — templates, truncation audits",
   "Training loop — args, schedules, checkpoints, best-pick",
   "Overfitting diagnosis — eval-during-train discipline",
  ],
  "04-lora-qlora.md": [
   "LoRA math — low-rank delta, parameter counting",
   "Adapter config — targets, r, alpha, dropout",
   "QLoRA — 4-bit base training on one GPU",
   "Parity checks — merged vs adapter serving",
  ],
  "05-capstone-task-llamaindex-retrieval.md": [
   "LlamaIndex essentials — readers/nodes/index/query engine",
   "Settings pinning — embedder/chunker, not defaults",
   "Shared-interface comparison — both engines, one harness",
   "Ship/adopt/reject decision — evidence-based",
  ],
  "06-capstone-prep-demo-day.md": [
   "Architecture freeze — 1:1 checklist",
   "Sprint roadmap — W17-24 exit artifacts",
   "Demo-day assets — script, metrics, fallback",
   "Version 1.0 definition — the five bars",
  ],
 },
 # ---------------------------- EXT: E1 / WEEK 17 ---------------------------
 "Week-17-Advanced-Fine-Tuning-DPO-RLHF-Distillation": {
  "01-dpo-preference-optimization.md": [
   "Preference data — formats, sources, content-parallel rules",
   "DPO loss — the closed form, β behavior, by-hand example",
   "TRL DPOTrainer — LoRA single-GPU runs and curves",
   "Variants — IPO/robust/KTO when data is noisy/unpaired",
   "Parity evals — win-rate + general non-regression",
  ],
  "02-rlhf-pipeline.md": [
   "Reward models — BT loss, scoring uses, failure modes",
   "PPO mechanics — four models, clipping, KL penalties",
   "GRPO — group baselines, verifiable rewards",
   "Best-of-N reranking — RM-scored serving pattern",
   "The alignment flywheel — logs to pairs to updates",
  ],
  "03-distillation.md": [
   "Sequence-level KD — teacher data generation at scale",
   "Filtering — the gate everyone skips, drop analysis",
   "Non-transfer list — reasoning/robustness/calibration gaps",
   "On-policy distillation — student rollouts corrected",
   "Break-even analysis — API vs distilled serving",
  ],
  "04-embedding-reranker-finetuning.md": [
   "Domain pairs — logs, synthetic, hard-negative mining",
   "MNRL training — batch negatives, LR, epochs",
   "Cross-encoder training — LLM-judged labels",
   "Re-indexing — migration discipline and parity",
  ],
  "05-practice-alignment-lab.md": [
   "Lab assembly — DPO+RM+distill+retrieval in one repo",
   "Preference eval — win-rate methodology",
   "Version register — artifacts and lineage",
   "Verdicts — measured alignment gains and costs",
  ],
 },
 # ---------------------------- EXT: E2 / WEEK 18 ---------------------------
 "Week-18-GraphRAG-Knowledge-Graphs-Long-Context": {
  "01-knowledge-graphs-rag.md": [
   "KG primitives — entities/relations/evidence fields",
   "Schema-guided extraction — prompts, JSON contracts",
   "Entity resolution — alias maps, merge passes",
   "Graph operations — neighborhood, multi-hop, co-occurrence",
  ],
  "02-graphrag-implementation.md": [
   "Communities — Leiden detection and sizing",
   "Community summaries — constrained map generation",
   "Global search — map-reduce over summaries",
   "Local search — entity-anchored retrieval",
   "Cost ledger — index-time vs query-time trade",
  ],
  "03-long-context-strategies.md": [
   "Lost in the middle — position-effect experiments",
   "RAG vs paste — the decision framework",
   "Compression — extractive/abstractive/LLMLingua",
   "Hybrid placement — rerank→expand→fit budgets",
  ],
  "04-hybrid-architecture.md": [
   "Four-arm router — rules→classifier→agent levels",
   "Cross-store normalization — one result shape",
   "RRF fusion — heterogeneous ranked lists",
   "Unified citations — doc/graph/sql formats",
   "Conflict resolution — when stores disagree",
  ],
  "05-practice-graphrag.md": [
   "Extraction over your corpus — evidence audits",
   "Communities and summaries — build and constrain",
   "15 graph-shaped eval cases — design and run",
   "Cost verdict — when GraphRAG pays off",
  ],
 },
 # ---------------------------- EXT: E3 / WEEK 19 ---------------------------
 "Week-19-Code-Web-Agents": {
  "01-code-agents-swe-patterns.md": [
   "SWE-agent loop — navigate/localize/edit/validate",
   "Repo tools — interface design, caps, containment",
   "Localization — grep-first vs read-all strategies",
   "Edit gating — diffs, approval, test validation",
  ],
  "02-web-browser-agents.md": [
   "Browser loop — state extraction, typed actions",
   "Numbered snapshots — the observation contract",
   "Injection at page scale — untrusted content guards",
   "Form automation — gated submits",
  ],
  "03-computer-use-agents.md": [
   "Screenshot action space — perception and grounding",
   "Failure modes — offsets, staleness, runaway actions",
   "A11y-tree hybrid — snapping coordinates",
   "Safety — VMs, gates, no secrets on screen",
  ],
  "04-agents-in-ci-pipelines.md": [
   "Reviewer bot — diff review, idempotent comments",
   "Fixer bot — bounded PR loops with provenance",
   "Gate hierarchy — what agents may touch",
   "Cost controls — routing, caching, skip conditions",
  ],
  "05-practice-repo-agent.md": [
   "QA agent over your repo — file:line citations",
   "Fixer drill — planted bug cycle",
   "CI review bot — local workflow run",
   "Gate table and failure modes",
  ],
 },
 # ---------------------------- EXT: E4 / WEEK 20 ---------------------------
 "Week-20-Vision-Deep-Dive-Detection-Document-AI": {
  "01-detection-segmentation.md": [
   "DETR — boxes/classes/thresholds, trained classes",
   "OWL-ViT — open-vocabulary text-prompted classes",
   "SAM — promptable masks, DETR composition",
   "Region chunks — RAG upgrade with provenance",
  ],
  "02-document-ai.md": [
   "OCR pipeline — Tesseract boxes, confidence filters",
   "VLM extraction — contracts, nulls, hallucination checks",
   "Tables/forms — pdfplumber/docling layout parsing",
   "Field-level citations — metadata contract",
  ],
  "03-vision-agents.md": [
   "Vision graph — classify→route→extract→verify",
   "Field verification — numeric grounding in OCR",
   "Multi-page merge — conflict checks",
   "Route accuracy — measured against hand labels",
  ],
  "04-practice-vision-pipeline.md": [
   "15-document corpus — mixed types and gold labels",
   "Three-store indexing — chunks/fields/crops",
   "Field accuracy evaluation — per-field tables",
   "Cost ledger — OCR vs VLM extraction",
  ],
 },
 # ---------------------------- EXT: E5 / WEEK 21 ---------------------------
 "Week-21-Audio-Production-Diarization-TTS": {
  "01-diarization-speech-analytics.md": [
   "pyannote pipelines — speaker turns, known/unknown counts",
   "Transcript merge — overlap-weighted assignment",
   "Hard cases — crosstalk, label churn, interjections",
   "Analytics — talk-time, interruptions, commitments",
  ],
  "02-tts-voice-cloning.md": [
   "TTS landscape — API voices vs open models",
   "Quality knobs — reference samples, sentence splitting",
   "Voice cloning — consent line and disclosure",
   "Agent integration — sentence streaming, expansion",
  ],
  "03-realtime-voice-production.md": [
   "VAD/endpointing — turn-taking machinery",
   "Barge-in — playback interruption and cancellation",
   "Telephony — 8kHz, echo, jitter handling",
   "Voice observability — per-stage metrics",
  ],
  "04-practice-meeting-assistant.md": [
   "Meeting ingestion — merge pipeline with flags",
   "RAG with speaker citations — turn-group chunks",
   "Commitment extraction — verified vs transcript",
   "TTS summary — expansion and consent",
  ],
 },
 # ---------------------------- EXT: E6 / WEEK 22 ---------------------------
 "Week-22-Advanced-Inference-Decoding": {
  "01-speculative-decoding.md": [
   "Draft/verify loop — the acceptance theorem",
   "Speed math — k_eff, cost ratio, slowdown cases",
   "vLLM/HF flags — running and measuring",
   "Benchmarking — parity + acceptance sweeps",
  ],
  "02-grammar-constrained-decoding.md": [
   "Token masking — how grammars guarantee validity",
   "Outlines — Pydantic/enum/regex grammars",
   "Architecture changes — retries deleted, checks kept",
   "Content quality — what grammars don't fix",
  ],
  "03-gguf-quantization-ecosystem.md": [
   "GGUF format — conversion and quant alphabet decoded",
   "llama.cpp/Ollama — knobs, context, serving",
   "Engine selection — llama.cpp vs vLLM vs TRT-LLM",
   "Quality protocol — task evals over perplexity",
  ],
  "04-practice-decoding-lab.md": [
   "Validity experiment — free vs retry vs grammar",
   "Speed overhead — masking costs measured",
   "Content verification — kept in the loop",
   "Serving matrix — model×quant×engine",
  ],
 },
 # ---------------------------- EXT: E7 / WEEK 23 ---------------------------
 "Week-23-Security-Red-Teaming": {
  "01-owasp-deep-dive.md": [
   "Top 10 mapped — exposure per risk in your architecture",
   "Threat model — actors, surfaces, blast radius ranking",
   "Controls inventory — evidence-linked built/missing",
   "Accepted risks — explicit, justified entries",
  ],
  "02-jailbreak-taxonomy.md": [
   "Five families — mechanisms and examples",
   "Defense mapping — which layer catches which",
   "Known bypasses — encoding, multi-turn, relays",
   "Test-matrix generation — taxonomy to cases",
  ],
  "03-safety-evals.md": [
   "Red-team orchestration — taxonomy-driven generation",
   "Judge calibration — agreement discipline",
   "Benign controls — false-block budget",
   "Triage — severity, fix/ticket/accept workflow",
  ],
  "04-sandboxing-egress.md": [
   "Blast-radius baseline — compromised-from-birth design",
   "Sandbox tiers — process/container/micro-VM flags",
   "Egress allow-lists — proxies, DNS, secrets",
   "Tool blast-radius checklist — per tool review",
  ],
  "05-practice-red-team.md": [
   "Threat model worksheet — final version",
   "Automated red-team run — 15+ attacks",
   "Triage and hardening — fixes and tickets",
   "Regression battery — bypasses as tests",
  ],
 },
 # ---------------------------- EXT: E8 / WEEK 24 ---------------------------
 "Week-24-LLMOps-Scale": {
  "01-registry-cicd.md": [
   "Deployment manifest — pinning models/prompts/tools/evals",
   "Four CI gates — unit/eval/security/budget enforcement",
   "Rollback drills — minutes, verified by parity",
   "Model registry — lineage, promotion, staging",
  ],
  "02-ab-shadow-testing.md": [
   "Deterministic A/B — sticky arms, pre-registered metrics",
   "Shadow deployment — run, don't serve, compare",
   "Canary — auto-rollback thresholds and drills",
   "Strategy per change class — prompt/model/tool/router",
  ],
  "03-cost-management.md": [
   "Token ledger — feature/user attribution, cached column",
   "Budget ladder — request/user/feature/global with degradation",
   "Optimization ledger — attributed savings",
   "Forecasting — growth curves and planned changes",
  ],
  "04-otel-observability.md": [
   "GenAI conventions — spans, attributes, redaction",
   "Dashboards — latency/cost/quality/safety panels",
   "Alert set — thresholds, tuning, pagination policy",
   "Unified story — LangSmith+OTel reconciliation",
  ],
  "05-practice-llmops.md": [
   "Registry+CI with planted regression caught",
   "Canary auto-rollback drill",
   "Ledger and budgets load-tested",
   "Operating manual — playbooks and SLOs",
  ],
 },
 # ---------------------------- EXT: E9 / WEEK 25 ---------------------------
 "Week-25-Memory-Long-Term-Agents": {
  "01-memory-architectures.md": [
   "Hierarchy — core/recall/archival tiers and paging",
   "Write policies — what earns memory, reversals",
   "Retrieval policies — budgets, provenance",
   "Letta hands-on — memory tools and persistence",
  ],
  "02-semantic-caching-compression.md": [
   "Semantic vs exact caching — thresholds and keys",
   "Invalidation — versions, TTL, source changes",
   "Wrong-hit auditing — sampling and judges",
   "Compression — extractive/abstractive/LLMLingua at agent scale",
  ],
  "03-long-term-memory-design.md": [
   "Lifecycle — propose→validate→store→retrieve→update→decay→delete",
   "Conflict resolution — authority tables",
   "Decay and consolidation — fade, merge, strengthen",
   "Privacy — tiers, erasure, cross-tenant isolation",
  ],
  "04-practice-memory-agent.md": [
   "Lifecycle implementation — all seven stages",
   "Reversal and conflict drills",
   "Erasure across tiers — retrieval probes",
   "Moving-baseline evaluation",
  ],
 },
 # ---------------------------- EXT: E10 / WEEK 26 --------------------------
 "Week-26-Specialization-Benchmark-Literacy": {
  "01-benchmark-literacy.md": [
   "Benchmark categories — what each measures and hides",
   "Contamination/saturation — failure lenses",
   "Claim checklists — reading vendor scores",
   "Your capstone claim — design and limits",
  ],
  "02-interpretability-basics.md": [
   "Attention inspection — maps on real inputs",
   "Logit lens — depth trajectories",
   "Probing agent decisions — routing/retrieval failures",
   "Interpretability reports — mechanistic explanations",
  ],
  "03-staying-current.md": [
   "Source triage — tiers, cadence, filters",
   "Three-pass paper protocol — 30 minutes",
   "Adoption gate — minimum experiments",
   "Weekly routine — sustainable 3 hours",
  ],
  "04-capstone-future-roadmap.md": [
   "Specialization tracks — six options, first artifacts",
   "Capstone 2.0 — product planning with pilots",
   "Compounding portfolio — artifacts and write-ups",
   "Gap-closing plan — blockers first",
  ],
 },
}

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def find_week_folders():
    folders = []
    for base in PLAN_ROOTS:
        if base.is_dir():
            folders += sorted([d for d in base.iterdir()
                               if d.is_dir() and d.name.startswith("Week-")])
    return folders


def topic_files(folder: Path):
    out = []
    for p in sorted(folder.glob("*.md")):
        if p.name in ("README.md", "handoff.md"):
            continue
        if re.match(r"^Week-\d\d-", p.name):      # generated overview
            continue
        if re.match(r"^\d\d-", p.name):
            out.append(p)
    return out


def slug_of(stem: str) -> str:
    return re.sub(r"^\d\d-", "", stem)


def overview_files(folder: Path):
    return [p for p in sorted(folder.glob("*.md"))
            if re.match(r"^Week-\d\d-", p.name)]


def render(folder: Path, title: str, plan: dict) -> str:
    files = topic_files(folder)
    table_rows = ["| `README.md` | week index — do not modify |"]
    table_rows += [f"| `{p.name}` | generated overview — do not modify |"
                   for p in overview_files(folder)]
    table_rows += [f"| `{p.name}` | topic deep-dive |" for p in files]
    table_rows.append("| `handoff.md` | this brief |")
    rows = "\n".join(table_rows)

    per_file = []
    for p in files:
        stem = p.stem
        sub = stem                                   # subfolder named after the file stem
        bullets = plan.get(p.name)
        if not bullets:
            bullets = [
                "Expand each major section of the parent file into its own deep-dive",
                "Add end-to-end worked examples and failure drills on real data",
                "Add a comparison/alternatives section and production notes",
                "Extend the exercise set with capstone-tied labs and checklists",
            ]
        lines = [f"#### `{p.name}` → subfolder `{sub}/`", ""]
        lines.append("Deep-dive files to create (suggested titles — refine as you write):")
        lines.append("")
        for i, b in enumerate(bullets, 1):
            lines.append(f"{i}. {b}")
        per_file.append("\n".join(lines))

    plan_md = "\n\n".join(per_file)
    week_rel = folder.relative_to(ROOT).as_posix()

    md = f"""# Handoff — {title}: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
{rows}

## 2. Expansion convention (applies to EVERY `NN-*.md` file)

1. Create subfolder `NN-<slug>/` named exactly after the file stem (e.g., `01-dpo-preference-optimization.md` → `01-dpo-preference-optimization/`).
2. Inside, create **4–6 detailed files**:
   - `README.md` — subtopic index: what this deep-dive covers, file map, study order, prerequisites (link back to `../NN-<slug>.md`).
   - `01-<subtopic>.md` … `0N-<subtopic>.md` — one deep-dive per major subtopic, following the expansion plan below.
   - `exercises.md` — expanded exercise set with worked approaches.
   - optionally `solutions.md` and `quiz.md` (self-assessment).
3. Each file: **4–8 KB**, same structure as the parent guides (What you'll learn → concepts with runnable code → tables → Exercises → Pitfalls → Resources).
4. The parent `NN-<slug>.md` stays **unchanged** — it remains the week-level overview.
5. Depth expectation: subfolders go **beyond** the parent — edge cases, end-to-end worked examples, failure drills, comparisons, performance notes — never a reformat of the parent.
6. Subfolder READMEs link back to the parent; deep-dive files cross-link other weeks' files by relative path when they build on them.

## 3. Quality rules (non-negotiable)

- Windows/PowerShell: `py` (not `python`), `.venv\\Scripts\\Activate.ps1`. Use **repo-relative paths** in all examples (`doc/...`, `data/...`, `scripts/...`) — never machine-specific absolute paths.
- All code **runnable**; verify framework APIs via **context7 MCP** before writing framework examples (note the library id used).
- Brief pedagogical comments allowed; no filler prose; every concept paired with a runnable artifact.
- Exercises tie to the capstone (GEF C7: RAG + agents over the learner's own corpus/tables/media).
- Do **not** modify: `README.md`, `Week-XX-*.md` overviews, other weeks' folders, `doc/GEF-C7-Final-Schedule.md`.
- **No compression, no placeholders** — full detail in every file (the user has explicitly rejected compressed outputs).

## 4. Per-file expansion plan

{plan_md}

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

{chr(10).join(f"- [ ] `{p.stem}/`" for p in files)}

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
{week_rel}/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
"""
    return md


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    folders = find_week_folders()
    if not folders:
        sys.exit("no Week-* folders found")

    written, missing_plan = [], []
    for folder in folders:
        plan = PLANS.get(folder.name, {})
        files = topic_files(folder)
        for p in files:
            if p.name not in plan:
                missing_plan.append(f"{folder.name}/{p.name}")

        title = folder.name.replace("-", " ")
        md = render(folder, title, plan)
        out = folder / "handoff.md"
        if not args.dry_run:
            out.write_text(md, encoding="utf-8")
        written.append(out)

    print(f"handoffs: {len(written)} ({'dry-run' if args.dry_run else 'written'})")
    if missing_plan:
        print("\nfiles without a specific expansion plan (generic plan used):")
        for m in missing_plan:
            print(f"  - {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
