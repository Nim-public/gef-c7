# vLLM/SGLang Serving — Knobs and Benchmarks

**What you'll learn:** the serving knobs you will actually tune
(`max_num_seqs`, `gpu_memory_utilization`, chunked prefill, prefix
caching), a benchmark methodology, and the PagedAttention idea that
makes it all work.

## 1. PagedAttention in one paragraph

The KV cache is stored in fixed-size *blocks* (like OS memory pages)
instead of contiguous buffers per sequence. Sequences share prefix
blocks (copy-on-write when they fork), fragmentation drops to ~4%, and
prefix caching becomes a lookup instead of a recompute. Every serving
efficiency claim in this file rests on that design.

## 2. The knobs

```python
from vllm import LLM

llm = LLM(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    max_num_seqs=64,                  # max sequences in a batch
    gpu_memory_utilization=0.90,      # fraction of VRAM for KV+weights
    enable_prefix_caching=True,       # shared prefixes pay once
    enable_chunked_prefill=True,      # long prompts interleave
    max_model_len=16384,              # context cap
    quantization="awq",               # file 04
)
```

| Knob | Up effect | Watch for |
|---|---|---|
| `max_num_seqs` | throughput | KV exhaustion → preemption |
| `gpu_memory_utilization` | more KV headroom | OOM against other processes |
| `enable_prefix_caching` | agent loops (shared system prompt) free | stale cache if prompts rotate |
| `enable_chunked_prefill` | no head-of-line blocking | slight latency per long prompt |
| `max_model_len` | context ceiling | KV per sequence scales with it |

The agent-workload knob: `enable_prefix_caching=True` is the biggest
single win for agents — your constitution, tool schemas, and knowledge
preamble are a shared prefix paid once per batch instead of per
sequence.

## 3. The benchmark methodology (yours, not the marketing's)

| Metric | Measure | Tool |
|---|---|---|
| throughput (tok/s) | total tokens / wall time | `vllm bench serve` or your loop |
| TTFT (time to first token) | prefill latency | streaming client |
| ITL (inter-token latency) | decode smoothness | streaming client |
| P99 under load | the demo's real number | concurrent client harness |

```text
benchmark protocol (yours):
  1. your 15-case eval set as the prompt mix (real lengths)
  2. concurrency 1, 4, 16 — the demo's shape
  3. report TTFT, ITL p50/p99, throughput
  4. compare knob settings, same protocol
```

The protocol uses *your* prompts — marketing numbers use uniform
lengths and hide the head-of-line blocking your corpus's long
retrieval prompts would cause.

## Exercises

1. Serve the 7B model with defaults; benchmark your eval set; record
   TTFT/ITL/throughput at concurrency 1/4/16.
2. Knob drill: flip `enable_prefix_caching` on; rerun; the TTFT delta on
   agent-loop workloads is the headline number.
3. Chunked-prefill drill: add a 30k-token prompt to the mix; measure
   other sequences' ITL with and without chunked prefill — the
   head-of-line blocking, demonstrated.
4. Protocol drill: write `reports/serving-benchmark.md` with the §3
   protocol and your numbers; the knob table gains a "your result"
   column.