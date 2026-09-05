# QLoRA — 4-Bit Base Training on One GPU

**What you'll learn:** QLoRA: the base model quantized to 4-bit (NF4),
LoRA adapters trained on top — a 7B SFT on a single 24 GB GPU, with the
memory math and the dequantization nuance that keeps quality.

## 1. The memory math

| Component | fp16 | QLoRA (NF4) |
|---|---|---|
| base weights | 14 GB | ~4 GB |
| LoRA params (r=16) | 80 MB | 80 MB (fp16) |
| optimizer states | ~320 MB | ~320 MB |
| activations + KV | ~2–4 GB | ~2–4 GB |
| **total** | **~20 GB** | **~7–10 GB** |

```python
from transformers import BitsAndBytesConfig

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",          # NormalFloat4 — info-theoretic
    bnb_4bit_compute_dtype="bfloat16",  # compute in bf16, store in NF4
    bnb_4bit_use_double_quant=True,     # quantize the quantization consts
)
```

NF4 (NormalFloat4) is the trick: weights are normally distributed, so a
4-bit datatype built for normal distributions preserves more
information than uniform int4. `use_double_quant` saves another ~0.4
bits/param on the quantization constants.

## 2. The dequantization nuance

The base weights stay 4-bit *stored* but are dequantized to bf16 for
the forward/backward *compute* — the LoRA gradients flow through the
dequantized values. Quality implications:

| Aspect | Effect |
|---|---|
| forward | near-fp16 quality (NF4's design) |
| backward | gradients update only the fp16 LoRA adapters |
| base weights | frozen, quantized, never updated |

The training updates the adapters in full precision while the frozen
base stays 4-bit — which is why QLoRA ≈ LoRA quality in practice, and
why the parity check (file 04) is still mandatory.

## 3. The single-GPU run

```python
from peft import get_peft_model, prepare_model_for_kbit_training

model = AutoModelForCausalLM.from_pretrained(
    "pinned-model-id", quantization_config=bnb, device_map="auto")
model = prepare_model_for_kbit_training(model)   # casts norms, disables dropout quirks
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()               # the 0.62% headline
trainer = Trainer(model=model, args=args, train_dataset=..., eval_dataset=...)
trainer.train()
```

| Step | Purpose |
|---|---|
| quantize base | 4-bit NF4 load |
| `prepare_model_for_kbit_training` | cast norms to fp32, gradient checkpointing |
| attach LoRA | the adapters |
| train | the W16-03 loop, unchanged |

The run is the W16-03 loop with a quantized base — the eval-during-
training, best-pick, and diagnosis disciplines all apply unchanged.

## Exercises

1. Load the base in NF4; verify the memory footprint against §1's
   table; the 24 GB card fits with headroom.
2. Quality drill: QLoRA vs fp16 LoRA on the 15-case eval; the delta is
   NF4's cost — usually within noise for behavior fine-tunes.
3. Double-quant drill: toggle `use_double_quant`; measure the memory
   delta; the ~0.4 bits/param saving is the flag's value.