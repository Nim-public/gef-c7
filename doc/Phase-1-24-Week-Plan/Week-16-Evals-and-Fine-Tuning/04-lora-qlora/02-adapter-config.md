# Adapter Config — Targets, r, Alpha, Dropout

**What you'll learn:** the adapter configuration: which projections get
LoRA (targets), how rank and alpha trade capacity for stability, and
dropout's role — the config that decides what the adapter can learn.

## 1. The target modules

```python
from peft import LoraConfig

config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    task_type="CAUSAL_LM",
)
```

| Target | Layer type | Include when |
|---|---|---|
| `q_proj, o_proj` | attention out | always (the minimal set) |
| `k_proj, v_proj` | attention KV | usually |
| `gate/up/down_proj` | MLP | for stronger adaptation |
| `lm_head` | output | rarely (vocab-sized, expensive) |

The targets are the capacity allocation: attention-only adapters learn
*style*; adding the MLP projections learns *domain behavior*. The
capstone's citation-discipline fine-tune: attention + MLP, r=16 — the
behavior change is real but narrow.

## 2. The knobs' effects (measured, not assumed)

| Knob | Up effect | Cost |
|---|---|---|
| r | capacity (more behaviors learnable) | params, overfitting risk |
| alpha/r | effective update size | stability |
| dropout | regularization | slight capacity |
| targets | breadth of adaptation | params |

The W16 file 04-01's math prices each knob; the drill is the
measurement. The starting config: r=16, alpha=32, dropout=0.05,
attention+MLP targets — then sweep one knob at a time (the bake-off
rule).

## 3. The config's pin note (the adapter's manifest)

```markdown
# LoRA adapter (W16)
- base: pinned-model-id
- targets: q/k/v/o + gate/up/down
- r=16, alpha=32, dropout=0.05
- task: CAUSAL_LM, SFT data v1 (W16-03)
- trainable params: 41.9M / 6.7B (0.62%)
```

The manifest is the adapter's identity — the same pin discipline as
every artifact. The trainable-percentage row is the headline: 0.62% of
the model, trained to change the behavior that mattered.

## 5. The config's pitfall battery (the sweep's guard)

| Pitfall | Symptom | Guard |
|---|---|---|
| alpha not scaled with r | effective update shrinks | alpha = 2r convention |
| dropout 0 on small data | overfitting (W16-03) | 0.05 default |
| wrong target names | zero trainable params | `print_trainable_parameters` |
| r too high for the data | memorization (W16-03 file 04) | the paraphrase probe |

The pitfall battery is the config's own test suite — each row's guard
is a §1–§2 mechanism or a W16-03 discipline. The zero-trainable-params
symptom is the most common first-run failure: a target-name typo
silently trains nothing.

## Exercises

1. Configure the adapter; count trainable params vs total; verify the
   percentage matches the math (file 01).
2. Targets drill: attention-only vs attention+MLP on the citation
   battery; the behavioral difference is the targets' effect, measured.
3. Pin drill: write the manifest; the config committed with the run.
4. Battery drill: run the §5 pitfalls as tests — zero-params detection,
   dropout assertion, alpha/r assertion.