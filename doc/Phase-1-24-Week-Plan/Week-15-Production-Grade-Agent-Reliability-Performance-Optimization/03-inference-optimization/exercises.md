# Exercises — Inference Optimization

Expanded set with worked approaches. The deliverable: the KV math on
your models, a serving benchmark with your prompts, and a quantization
decision with measured quality.

## 1. The KV math (from 01-kv-cache)

**Task:** compute per-sequence KV at 4k/16k/32k context for two models
(7B GQA and 70B GQA), fp16 and fp8-KV; fill the table; derive the max
batch for your card.

**Worked approach:** the formula with GQA's kv_heads (check the config,
not memory) — the table is the serving decisions' substrate. Show the
fp8 doubling explicitly.

**Pass criterion:** the table complete; the max-batch derivations
shown; GQA verified against the model config.

## 2. Continuous batching simulation (from 02)

**Task:** simulate static vs continuous scheduling on uniform and mixed
length distributions; plot slot utilization; the waste is the argument.

**Worked approach:** numpy sequences with known lengths; the static
scheduler's utilization collapses as length variance grows — the plot
is the continuous-batching justification, self-made.

**Pass criterion:** both plots committed; the utilization numbers
annotated.

## 3. The serving benchmark (from 03-vllm-serving)

**Task:** serve a 7B model (vLLM); benchmark your eval-set prompts at
concurrency 1/4/16; flip prefix caching; record TTFT/ITL p50/p99 and
throughput in `reports/serving-benchmark.md`.

**Worked approach:** the protocol uses *your* prompts — uniform-length
marketing numbers hide the head-of-line blocking your long retrieval
prompts cause. Prefix caching is the agent-workload headline.

**Pass criterion:** the table committed with all knobs recorded; the
prefix-caching TTFT delta measured.

## 4. The quantization decision (from 04-quantization)

**Task:** run the four quality tests fp16 vs AWQ (and FP8 KV if you
have the card); fill the decision procedure; the verdict goes in the
serving memo.

**Worked approach:** the eval set is the verdict — perplexity is the
sanity check, the needle test is the KV sentinel, and the 15 cases are
the decision. No quantization without the before/after runs.

**Pass criterion:** all four tests recorded; the decision memo cites
the before/after numbers.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| KV table with GQA verified | math + config check | 4 |
| Batching simulation plots | reports/batching.md | 3 |
| Serving benchmark, your prompts | serving-benchmark.md | 4 |
| Quantization decision, quality-measured | memo + tests | 4 |
| Serving pin note | pin note | 2 |

**Pass bar:** 15/18 to proceed to file 04 (prompt caching). The serving
benchmark (4-pointer) is the week's measurement crown — your prompts,
your knobs, your numbers.

## 6. The serving pin note (the inference manifest)

**Task:** consolidate the inference stack in `reports/sdk-versions.md`:
the KV formula inputs, the benchmark protocol, the knob settings, and
the quantization decision — one block.

**Worked approach:** the serving manifest follows the pin discipline:
the formula's model-config values, the benchmark protocol, and the knob
settings that produced your numbers.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## 7. The inference quiz (the concepts, self-tested)

**Task:** answer without notes: (a) why is decode memory-bound but
prefill compute-bound? (b) why does GQA shrink the KV cache? (c) why do
agent workloads benefit most from continuous batching? (d) why does
prefix caching compound with agents? One paragraph each.

**Worked approach:** the quiz is the concepts' compression test — if
the paragraphs write themselves, the serving stack is understood; where
they stall, re-read the section. The answers join the recap sheet.

**Pass criterion:** four paragraphs, each mechanically correct (checked
against the file's sections).

## Pitfalls recap

- Full head-count on GQA models — 8× the real KV memory; check the
  config.
- Marketing-protocol benchmarks — your prompts have your length
  distribution; uniform lengths hide the blocking.
- Quantization without quality tests — silent regressions on your tasks
  are the failure the tests exist to catch.