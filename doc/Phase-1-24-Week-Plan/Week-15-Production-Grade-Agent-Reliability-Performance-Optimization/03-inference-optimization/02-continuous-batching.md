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

## 5. The simulation, expanded (the scheduler's rules)

```python
def simulate(sequences: list[int], continuous: bool):
    """Toy scheduler: one token per step per active sequence."""
    remaining = {i: n for i, n in enumerate(sequences)}
    slot_util, step = [], 0
    queue = list(remaining)                      # arrivals wait for slots
    while remaining or queue:
        active = min(len(remaining), MAX_SLOTS)
        slot_util.append(active / MAX_SLOTS)
        for i in list(remaining):
            remaining[i] -= 1
            if remaining[i] == 0:
                del remaining[i]
                if continuous and queue:         # refill immediately
                    remaining[queue.pop(0)] = sequences[queue_idx.pop(0)]
        step += 1
    return slot_util
```

| Scheduler behavior | Static | Continuous |
|---|---|---|
| slot on completion | idles until batch end | refills next step |
| arrival during batch | waits for next batch | joins next step |
| utilization | batch-length-limited | ~100% while work remains |

The simulation is the concept's proof — two schedulers, identical
arrivals, one plot. Extend it with arrival distributions (Poisson) and
you have the queueing model behind every serving benchmark.

## 6. The agent-workload fit (why your loops benefit most)

| Agent property | Effect on batching |
|---|---|
| many short decode turns | high turnover → slots refill often |
| variable output lengths | static batches waste on the longest |
| shared system prompts | prefix caching compounds the win |
| concurrent eval/demo runs | the arrivals exist |

The agent loop is continuous batching's ideal workload — the table maps
your W10 loop's properties onto the scheduler's wins. The benchmark
(file 03) measures it; this table predicts it.

## Exercises

1. Simulate both schedulers in numpy (toy sequences with known lengths);
   plot GPU-slot utilization per step; the waste is visible.
2. Length-distribution drill: uniform vs mixed lengths; measure the
   static scheduler's utilization collapse.
3. Workload drill: from your trajectory store, plot the token-length
   distribution of your agent's turns; conclude whether your serving
   workload is the best case (it is, for agent loops).
4. Extension drill: add Poisson arrivals to the simulation; compare
   queue depth static vs continuous under the same arrival rate.