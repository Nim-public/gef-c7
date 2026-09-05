# RNNs — LSTM/GRU Sequence Encoding and Limits

**What you'll learn:** the pre-attention sequence encoder, its actual
mechanics (gates, states, BPTT), where it still wins, and the three limits
that made attention necessary.

## 1. The recurrence, in six lines

```python
import numpy as np

def lstm_step(x, h_prev, c_prev, W, b):
    z = x @ W["x"] + h_prev @ W["h"] + b            # 4d concatenated pre-act
    f, i, o, g = np.split(z, 4, axis=-1)
    f, i, o = 1 / (1 + np.exp(-f)), 1 / (1 + np.exp(-i)), 1 / (1 + np.exp(-o))
    g = np.tanh(g)
    c = f * c_prev + i * g                           # cell: keep + write
    h = o * np.tanh(c)                               # hidden: read
    return h, c

def lstm_encode(xs, dim: int):
    h = np.zeros(xs.shape[:-1] + (dim,)); c = np.zeros_like(h)
    for t in range(xs.shape[0]):
        h[t], c[t] = lstm_step(xs[t], h[t - 1] if t else h[0] * 0,
                               c[t - 1] if t else c[0] * 0, W, b)
    return h                                          # (T, dim) per-step states
```

Read the cell update as an accounting system: `c` is a *running sum* with
forget-gate discounting (`f`) and input-gate depositing (`i·g`); `h` is what
the outside world may read of it (`o`). GRU collapses the pair into one
`h` with update/reset gates — same idea, 25% fewer params, similar quality
at small scale.

## 2. Why gates at all

Plain RNN backprop multiplies by W repeatedly through time; gradients
vanish (∥W∥<1) or explode (>1). The LSTM's cell path is *additive*
(`c_t = f·c_{t-1} + i·g`) — gradients flow through addition, not repeated
multiplication. This is the entire trick: the forget gate *chooses* when to
multiply. A sanity drill:

```python
# gradient magnitude through 100 steps, plain RNN vs LSTM cell path
# plain: 0.9^100 ≈ 2.6e-5 (vanished); LSTM: ≈ sum of gate-weighted terms (alive)
```

## 3. The three limits (and their attention-era answers)

| Limit | Symptom | Attention's answer |
|---|---|---|
| Sequential compute | t steps = t serial ops; batch of long sequences is slow | all positions in parallel |
| Fixed-size bottleneck (seq2seq pre-2017) | late inputs crushed into final h | direct access to all positions |
| Weak long-range recall | 500+ tokens degrade | O(T²) attention, O(1) path length |

Numeric shape of the first: a 30 s clip at 50 Hz = 1500 steps — 1500 serial
kernel launches vs a transformer's ~24 layers × parallel T. On GPUs this is
a 10–50× throughput difference, which is why you fine-tune wav2vec2 (conv+attn)
and not an LSTM stack.

## 4. Where RNNs still win

| Setting | Why RNN (LSTM/GRU) |
|---|---|
| Streaming, fixed memory | O(1) state vs transformer's growing KV cache |
| Tiny MCUs / edge | 10k–100k params viable; attention is not |
| Sub-second latency, low batch | no quadratic attention to launch |
| Online ASR frontends | causal by construction |

The capstone angle: if you ever ship the corpus-indexer to a phone, a GRU
frontend *is* the pragmatic audio encoder — knowing when "obsolete"
architecture is the right tool is an engineering judgment, not a fashion.

## Exercises

1. Gate intuition: set `f=0, i=1` — what is `c_t`? (pure overwrite). Set
   `f=1, i=0` (pure memory). Verify both with `lstm_step`.
2. Vanishing demo: unroll a plain RNN over 50/100/200 steps, backprop a unit
   gradient, plot the norm — the curve is the argument for gates.
3. Latency micro-bench: LSTM step vs one transformer layer at T=1500 on CPU
   (numpy/torch), per-token cost; write the two numbers down.

## Pitfalls

- Assuming GRU ≪ LSTM always — parity within noise on many sequence tasks; GRU wins on params.
- Reading `h` and `c` interchangeably — `h` is gated; `c` is the long-term memory; state access matters.
- Testing recurrence with random weights and blaming the optimizer — fix gates explicitly (e.g., `f`→1) before diagnosing learning.

## Resources

- Hochreiter & Schmidhuber 1997 (LSTM); Cho et al. 2014 (GRU).
- "The Unreasonable Effectiveness of RNNs" (Karpathy) — still the best gate intuition.
