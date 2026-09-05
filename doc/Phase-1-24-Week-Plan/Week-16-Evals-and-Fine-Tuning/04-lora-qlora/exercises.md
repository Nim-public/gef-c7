# Exercises — LoRA & QLoRA

Expanded set with worked approaches. The deliverable: the LoRA math on
your model, the adapter config measured, a QLoRA run on one GPU, and
merge parity proven.

## 1. The LoRA math (from 01-lora-math)

**Task:** compute the parameter counts for r ∈ {8, 16, 32, 64} on your
target model's projections; plot the capacity/params curve.

**Worked approach:** the count is `d·r + r·k` per targeted projection,
summed. The curve shows capacity growing linearly while params stay
~1% of the model — the efficiency claim, made visual.

**Pass criterion:** the curve committed; the r=16 point's count
verified against the adapter's `print_trainable_parameters`.

## 2. Adapter config sweep (from 02-adapter-config)

**Task:** attention-only vs attention+MLP targets on the citation
battery; the alpha sweep on the eval curve; the pin manifest written.

**Worked approach:** one knob per experiment (the bake-off rule). The
targets' behavioral difference shows on the citation battery; the alpha
sweep shows the effective-scale effect on the eval curve.

**Pass criterion:** both sweeps recorded; the config chosen with its
numbers; the manifest committed.

## 3. The QLoRA run (from 03-qlora)

**Task:** load the base in NF4; verify the memory footprint; run the
W16-03 loop on the single GPU; the quality drill vs fp16 LoRA.

**Worked approach:** the memory table (§1) is verified by
`nvidia-smi` during the run; the quality drill is the NF4 cost, usually
within noise for behavior fine-tunes.

**Pass criterion:** memory within the table; the quality delta
recorded; the run's artifacts committed (config, curve, eval).

## 4. Merge parity (from 04-parity-checks)

**Task:** merge the adapter; run the token-identity parity test on 20
prompts; run the 15-case eval on both serving modes; the dtype note.

**Worked approach:** token-identity is the strict bar — merged ≡
adapter means the merge is arithmetic. The dtype note (fp16 vs bf16
serving) belongs in the pin.

**Pass criterion:** 20/20 token-identical; the eval scores match; the
dtype recorded.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| LoRA math: counts + zero-init verified | math + drill | 4 |
| Config sweep: targets + alpha measured | sweep report | 4 |
| QLoRA run: memory + quality drill | run artifacts | 4 |
| Merge parity: token-identical + eval match | parity tests | 4 |
| Pin notes (adapter + merge) | pin notes | 2 |

**Pass bar:** 15/18 to proceed to file 05 (LlamaIndex). The merge
parity (4-pointer) is the efficiency week's proof — the adapter and the
merged model are the same agent.

## 6. The LoRA-QLoRA pin note (the efficiency manifest)

**Task:** consolidate the efficiency stack in `reports/sdk-versions.md`:
the LoRA math counts, the config sweep results, the QLoRA memory/quality
drills, and the merge-parity record — one block.

**Worked approach:** the efficiency manifest follows the pin discipline:
the math's counts, the sweeps' results, and the parity proofs.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## 7. The efficiency quiz (self-tested)

**Task:** answer without notes: (a) why does B start at zero? (b) what
does alpha/r control? (c) why does NF4 preserve quality? (d) why must
merged ≡ adapter? One paragraph each, checked against the files.

**Worked approach:** the quiz is the concepts' compression test — the
answers join the recap sheet family, and the stalls name the sections
to re-read.

**Pass criterion:** four paragraphs, mechanically correct against the
files.

## Pitfalls recap

- Raising r without raising alpha — the effective update *shrinks*; the
  alpha/r convention keeps the scale.
- Merging without the parity test — dtype or missing-module bugs ship;
  token-identity is the gate.
- QLoRA quality assumed ≈ LoRA — the 15-case eval verifies it on *your*
  tasks; usually true, but verified.