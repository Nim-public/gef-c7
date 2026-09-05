# CNN Mechanics — Convolution, Pooling, Receptive Fields by Hand

**What you'll learn:** compute convolutions on arrays small enough to check
with your eyes, derive output sizes from the formula, and understand
receptive fields — the property ViT replaced, not abandoned.

## 1. Convolution on a 5×5, verified by hand

```python
import numpy as np

x = np.arange(25, dtype=np.float32).reshape(5, 5)
k = np.array([[1., 0., -1.],
              [1., 0., -1.],
              [1., 0., -1.]])          # vertical edge detector

def conv2d(x, k, stride=1, pad=0):
    kh, kw = k.shape
    oh = (x.shape[0] - kh + 2 * pad) // stride + 1
    ow = (x.shape[1] - kw + 2 * pad) // stride + 1
    xp = np.pad(x, pad)
    out = np.zeros((oh, ow), dtype=np.float32)
    for i in range(oh):
        for j in range(ow):
            patch = xp[i*stride:i*stride+kh, j*stride:j*stride+kw]
            out[i, j] = (patch * k).sum()
    return out

print(conv2d(x, k).shape)   # (3, 3)
```

Output size formula — derive it, don't memorize it:
`out = floor((in − kernel + 2·pad) / stride) + 1`.
For 5×5, k=3, stride 1, pad 0: `(5−3)/1 + 1 = 3`. ✓

Check one cell by hand: `out[0,0] = 0·1+1·0+2·(−1) + 5·1+6·0+7·(−1) +
10·1+11·0+12·(−1) = (0+5+10) − (2+8+14) = −9`. If you can do this, you can
debug any CNN shape error for the rest of the program.

## 2. Stacking: channels, depth, and the size algebra

```python
# A "conv block" = conv + nonlinearity + pool. Sizes through a small net:
def out_size(in_, k=3, stride=1, pad=1):      # 'same' conv
    return (in_ - k + 2 * pad) // stride + 1

h = 224
h = out_size(h, 7, 2, 3);  print(h)   # 112   (stem conv)
h = out_size(h, 3, 2, 1);  print(h)   # 56    (downsample)
h = out_size(h, 3, 1, 1);  print(h)   # 56    (keep)
h = out_size(h, 2, 2, 0);  print(h)   # 28    (maxpool)
```

Each conv layer also multiplies by output channels; the *spatial* size
shrinks while *channel* count grows — the hourglass that makes deep nets
affordable. Params for conv(C_in→C_out, k): `C_in·C_out·k² + C_out`
(bias) — compare with a fully-connected layer on 224×224×3: `150M` weights
vs `k²·C·C` for conv. This asymmetry *is* the CNN's efficiency argument.

## 3. Receptive fields — what a unit can "see"

```python
def receptive_field(layers: list[tuple[int, int]]) -> int:
    """layers = [(kernel, stride), ...] from input to target layer."""
    rf, jump = 1, 1
    for k, s in layers:
        rf = rf + (k - 1) * jump
        jump *= s
    return rf

# VGG-style stack of 3× (3×3, stride 1) convs:
print(receptive_field([(3,1)]*3))   # 7 — three 3×3 convs see 7×7 pixels
# one 7×7 conv sees the same area with fewer params: 3·49 vs 3·(3·9)·... 
```

The famous result: **two 3×3 convs = one 5×5 receptive field with fewer
params and an extra nonlinearity** (2·3·3·C² = 18C² vs 25C²). Deep small
kernels beat wide ones — this is why ResNets are built from 3×3s.

## 4. Pooling and its cost

```python
def maxpool2d(x, size=2):
    h, w = x.shape
    return x[:h//size*size, :w//size*size] \
        .reshape(h//size, size, w//size, size).max(axis=(1, 3))
```

Max-pool keeps the strongest activation per window — translation tolerance
for free, spatial resolution paid. Down the network, "where" is traded for
"what"; ViT (file 03) instead keeps all positions and lets attention decide.

## Exercises

1. Hand-compute `conv2d(x, k)` cell `[1,1]`; then verify against code.
2. Write a 3-layer "net" (conv 3×3 → pool 2 → conv 3×3 → pool 2) on a 32×32
   input; predict final shape before running, then check.
3. Receptive field drill: how many 3×3 stride-1 convs until rf ≥ 64? How many
   params if C=64 throughout? Compare with one 64×64 conv's param count.

## Pitfalls

- Forgetting padding changes both size *and* edge behavior — border pixels are seen less; same-padding compensates.
- Confusing stride on the *kernel* vs dilation — dilation grows rf without growing params, but with sparse sampling.
- `np.pad` with pad=1 pads both sides — the `2*pad` in the formula already counts both; don't double-pad.

## Resources

- VGG paper §2 (the 3×3 stacking argument).
- CS231n conv nets notes — the output-size arithmetic drill.
