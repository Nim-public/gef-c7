# Parity Checks — Merged vs Adapter Serving

**What you'll learn:** the parity checks: the adapter's weights can be
*merged* into the base (W + B·A) for zero-overhead serving, or served
as adapters for multi-tenant flexibility — and both must produce
identical outputs.

## 1. The merge

```python
from peft import PeftModel

model = AutoModelForCausalLM.from_pretrained("pinned-model-id")
model = PeftModel.from_pretrained(model, "models/sft-run-01/adapter")
merged = model.merge_and_unload()       # W' = W + B·A, folded into weights
merged.save_pretrained("models/sft-run-01/merged")
```

| Serving mode | Memory | Latency | Flexibility |
|---|---|---|---|
| adapter loaded | base + adapter | tiny adapter overhead | hot-swap adapters |
| merged | base only (W' includes ΔW) | identical to base | one behavior per copy |

Merging folds B·A into the weights — the served model is a plain model
with the learned behavior baked in. Adapter serving keeps them separate
for multi-tenant deployments (one base, many adapters, swapped per
request).

## 2. The parity test (merged ≡ adapter)

```python
def test_merge_parity(prompts: list[str]):
    for prompt in prompts:
        a = adapter_model.generate(**tok(prompt, return_tensors="pt"))
        b = merged_model.generate(**tok(prompt, return_tensors="pt"))
        assert torch.equal(a, b), "merged and adapter outputs diverge"
```

The test runs identical prompts through both and asserts *identical
token sequences* — the merge is arithmetic (W + B·A), so divergence
means a dtype bug, a missing module, or a wrong adapter. The parity
test is the merge's acceptance gate.

## 3. The eval parity (the W16-03 discipline, post-merge)

| Check | Adapter | Merged |
|---|---|---|
| 15-case exact-match | 12/15 | 12/15 |
| citation gate | 100% | 100% |
| judge total | 6.9 | 6.9 |
| overfitting probes | pass | pass |

The merged model must pass the *same* eval battery as the adapter —
the merge is not a behavior change, and the battery is the proof. The
W16-03 diagnosis pin's numbers re-verify post-merge.

## Exercises

1. Merge the adapter; run the parity test on 20 prompts; token-identical
   outputs are the pass bar.
2. Eval-parity drill: run the 15-case set on both serving modes; the
   scores must match exactly.
3. Multi-tenant drill: load two adapters on one base; hot-swap between
   requests; verify no cross-contamination of behaviors.
4. Dtype drill: merge in fp16 and load in fp16 vs load in bf16; the
   outputs differ slightly — dtype is part of the serving pin.