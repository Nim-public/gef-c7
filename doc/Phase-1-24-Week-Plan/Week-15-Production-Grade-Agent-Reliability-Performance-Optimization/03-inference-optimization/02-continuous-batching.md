# Continuous Batching — Throughput Mechanics

**What you'll learn:** why continuous batching (iteration-level
scheduling) multiplies throughput versus static batching: sequences
join and leave the batch at *every* decode step, and no sequence waits
for the slowest.

## 1. Static vs continuous

```text
STATIC batching (naive):
  batch [A(10 tok), B(100 tok)] → A finishes at t=10, sits idle until
  B finishes at t=100. GPU utilization: ~10%.

CONTINUOUS batching (vLLM-style):
  A finishes at t=10 → its slot refills with C immediately.
  The GPU never waits for the longest sequence.
```

| Mechanism | Waste | Throughput |
|---|---|---|
| static | idle slots until batch completes | baseline |
| continuous | none (slots refill per step) | 2–20× static |

The insight: LLM decode is *memory-bandwidth-bound* per token, so the
GPU has spare compute to process more sequences per step — continuous
batching fills that slack at every iteration.

## 2. The scheduler's decisions (per iteration)

| Decision | Mechanism | Effect |
|---|---|---|
| admit new sequence | if KV space allows | throughput up |
| preempt a sequence | KV pressure → evict, recompute later | prevents OOM |
| swap to CPU | VRAM full → KV offload | slower but alive |
| chunked prefill | split long prefills across steps | less head-of-line blocking |

The scheduler trades preemption/recompute against admission — the knobs
(file 03) tune the thresholds. Chunked prefill matters for your corpus:
a 30k-token retrieval prompt would block the batch for its whole
prefill; chunking lets other sequences interleave.

## 3. The numbers that justify it (measured, typical)

| Workload | Static TPS | Continuous TPS |
|---|---|---|
| uniform short outputs | ~1× | ~2–3× |
| mixed output lengths | ~1× | ~5–10× |
| agent loops (many short turns) | ~1× | ~8–20× |

Agent workloads are the *best* case for continuous batching: many
short-turn sequences with wildly variable lengths arrive concurrently —
exactly the shape static batching handles worst.

## Exercises

1. Simulate both schedulers in numpy (toy sequences with known lengths);
   plot GPU-slot utilization per step; the waste is visible.
2. Length-distribution drill: uniform vs mixed lengths; measure the
   static scheduler's utilization collapse.
3. Workload drill: from your trajectory store, plot the token-length
   distribution of your agent's turns; conclude whether your serving
   workload is the best case (it is, for agent loops).