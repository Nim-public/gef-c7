# Exercises — Small Language Models

> Subfolder index: [README.md](README.md) · Parent: [../05-small-language-models.md](../05-small-language-models.md)

Labs for this subfolder. Shared fixture: the 10-prompt mini-eval (W2-06's set) plus a 30-case mixed eval (extraction/summary/reasoning/creative) — reused across all labs.

---

## E1 — Capability-per-size mapping (file 01)

1. Three sizes × your 30-case eval: Qwen2.5-0.5B/1.5B/7B (or SmolLM2 ladder) — accuracy per task class; plot capability vs size.
2. The floor test: find the smallest model that passes each task class at your quality bar — build the size ladder (W15-04's router needs it).
3. License matrix: the 5 families × (internal/product/redistribute) — the legal verdict table.

**Worked approach:** exercise 2's ladder is the routing design — each rung has an evidence row from the eval table.

## E2 — Local serving certification (file 02)

1. Three paths side-by-side (transformers/Ollama/LM Studio): same model, same prompts — output diffs and latency table.
2. Concurrency probe: 5 parallel requests to Ollama — throughput, queueing, timeouts (W15-01's budgets).
3. Portability proof: `base_url` swap between Ollama and the API in your W14-05 assistant — zero code changes beyond config; document anything that broke.

**Worked approach:** exercise 3 is the endpoint-compatibility dividend — the portability claim verified on your own stack.

## E3 — Quantization quality audit (file 03)

1. Quant sweep: fp16 pipeline vs Ollama Q8/Q4 on the 30-case eval — accuracy per slice (the degradation map).
2. Memory verification: computed vs measured memory per quant (W15-03's formula + `psutil`) — reconcile.
3. The degradation map: which task classes degrade first at Q4 — reasoning? rare knowledge? format compliance? (The non-uniformity measurement.)

**Worked approach:** exercise 3's degradation map is the deliverable — "Q4 is fine" is a claim; "Q4 loses 3 points on reasoning, 0 on extraction" is a decision input.

## E4 — The routing decision pack (file 04)

1. The benchmark protocol (§1): 30 cases × {API, local-SLM} — the sliced table.
2. The privacy test: egress monitoring during a local-only run (E7-04's audit) — zero-egress proof for the sensitive slice.
3. Hybrid: local-first with confidence escalation — the blended cost and quality table (W15-04 §3's pattern).
4. The break-even analysis: your traffic forecast (E8-03) × the §1 costs — the crossover month.

**Worked approach:** exercise 3's hybrid is the production pattern — the router sends the easy 80% local and escalates the tail, with the escalation rate as the tuning metric.

## Self-assessment

- Can you state your size ladder with the evidence per rung?
- Can you run the same eval across three serving paths and reconcile the differences?
- Can you defend your SLM-vs-API split with measured numbers, not preferences?
