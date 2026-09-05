# Exercises — Encoding Text & Images

Expanded set with worked approaches. Everything runs on CPU; the geometry
drill uses ≤ 30 images from `data/processed/images-224/`.

## 1. Template conformity check (from 01-text-encoder-template)

**Task:** write the `Encoder` Protocol implementations for MiniLM (text) and
CLIP image tower (image), then a single test that runs *identical* roundtrip
assertions on both — proving the interface, not the modality.

**Worked approach:**

```python
def test_encoder_protocol(enc):
    v = enc.encode([{"rel_path": u} for u in sample_units])
    assert v.shape == (len(sample_units), enc.dim)
    assert abs(np.linalg.norm(v, axis=1) - 1).max() < 1e-5   # L2-normalized
    assert float(v[0] @ v[0]) == 1.0                          # self-sim
```

The `sample_units` fixture fakes manifests rows, so the test needs no data
on disk — CI-safe by construction.

**Pass criterion:** one parametrized test, two encoders, green.

## 2. Convolution algebra mastery (from 02-cnn-mechanics)

**Task:** without running code, predict outputs of: (a) 224×224, k=5, s=2,
p=2; (b) 55×55, k=3, s=2, p=1; (c) 29×29, k=2, s=2, p=0. Then verify all
three with `conv2d` and explain any miss (floor behavior on odd gaps).

**Worked approach:** (a) (224−5+4)/2+1 = 112 ✓; (b) (55−3+2)/2+1 = 28 ✓;
(c) (29−2)/2+1 = 14 (floor(27/2)+1) ✓ — the floor is where hand-math and
torch occasionally disagree; know that torch's `Conv2d` uses floor too.

**Pass criterion:** three predictions correct *with the floor reasoning
written down*.

## 3. Token-count drill set (from 03-vit-patch-tokens)

**Task:** compute tokens + attention-pair counts for: ViT-B/16 @ 224,
ViT-B/16 @ 384, ViT-L/14 @ 336, and a hypothetical patch-8 @ 224. Which one
is already impractical on CPU?

**Worked approach:** tokens = (res/patch)² + 1; pairs = tokens². B/16@384 →
577 tokens → 333k pairs (8.5× of 224). Patch-8@224 → 785 tokens → 616k
pairs (16×) — the impractical one. Write the four rows as a table in your
week notes; this exact arithmetic is Week 09's encoder-cost input.

## 4. Position-embedding interpolation drill (from 03)

**Task:** load a pretrained ViT's pos-embedding (timm or HF), reshape to
14×14+1, bicubic-resize to 16×16+1, and encode a 256×256 image. Then encode
the same image *downscaled to 224* with the original weights. Compare
cosines of the two CLS vectors.

**Worked approach:**

```python
pos = model.embeddings.position_embeddings          # (1, 197, 768)
cls, grid = pos[:, :1], pos[:, 1:].reshape(1, 14, 14, 768).permute(0, 3, 1, 2)
grid_up = torch.nn.functional.interpolate(grid, size=(16, 16), mode="bicubic")
pos_up = torch.cat([cls, grid_up.flatten(2).permute(0, 2, 1)], 1)   # (1, 257, 768)
```

Expect cosine ≈ 0.85–0.98 (high but degraded): the low-res path is usually
*more* faithful for small images — resolution helps only when detail exists.

**Pass criterion:** both encodings run; the cosine gap is reported with one
sentence of interpretation.

## 5. Capstone: encoder shortlist memo (from 04-cnn-vs-vit)

**Task:** write `doc/capstone/encoder_decision.md` (one page): the two
candidate image encoders, the geometry/retrieval numbers from the practice
lab, cost per 1k images, and the pick with a one-paragraph justification.

**Worked approach:** the memo template is §4's decision procedure with your
numbers in §1–2's tables. It must be *revisable*: a "revisit if" line per
criterion (e.g., "revisit if screenshot share > 30%") keeps the decision
alive without reopening it weekly.

**Pass criterion:** the memo cites concrete numbers from your own runs —
no leaderboard quotes without your-corpus confirmation.

## Pitfalls recap

- Tests that hardcode model names without a fixture abstraction — parametrize over the Protocol or every encoder swap breaks CI.
- Attention-pair math quoted per *image* when the real unit is the *batch* — B multiplies everything; state the batch size in cost tables.
- Interpolating pos embeddings for *fewer* tokens than trained — works but wastes quality; downscale the image instead.
