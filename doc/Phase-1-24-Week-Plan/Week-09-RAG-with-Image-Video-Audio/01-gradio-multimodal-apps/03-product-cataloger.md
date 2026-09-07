# Product Cataloger — CLIP + BLIP + SQLite Composition

**What you'll learn:** the composition pattern: three systems (CLIP search,
BLIP captioning, SQLite metadata) behind one UI, with an explicit data flow
and an idempotent ingest path — the architecture your capstone reuses at
larger scale.

## 1. The data flow, drawn once

```text
upload image ──▶ [BLIP] caption ──▶ SQLite(product: id, name, caption, path)
                     │
                     └──▶ [CLIP] embedding ──▶ .npy matrix (row = product id)
                                                        │
query text ──▶ [CLIP text] ──▶ cosine vs matrix ──▶ top-K ──▶ UI gallery
```

Two stores, two reasons: SQLite owns *facts* (name, caption, path —
transactional, human-editable); the matrix owns *geometry* (vectors, bulk
numerics). Week 09 file 02 upgrades the matrix store to LanceDB; the split
itself survives.

## 2. Idempotent ingest (the part everyone skips)

```python
import sqlite3, hashlib, json
from pathlib import Path

def ingest_image(path: str, name: str, conn, matrix, ids: list[str]) -> int:
    h = hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]
    cur = conn.execute("SELECT id FROM products WHERE sha256=?", (h,))
    if cur.fetchone():
        return 0                                   # already ingested
    caption = blip_caption(path)
    emb = clip_image_embed(path)
    pid = f"p_{h}"
    conn.execute("INSERT INTO products VALUES (?,?,?,?,?)",
                 (pid, name, caption, path, h))
    conn.commit()
    matrix.append(emb); ids.append(pid)            # row order = ids order
    return 1
```

Idempotency = re-running ingest adds nothing new (the content hash is the
idempotency key — the Week-07 manifest discipline applied to an app).

## 3. The search path with row-alignment invariant

```python
import numpy as np

def search(query: str, matrix: np.ndarray, ids: list[str], k: int = 8):
    q = clip_text_embed(query)
    q = q / np.linalg.norm(q)
    M = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    top = np.argsort(-(M @ q))[:k]
    return [(ids[i], float(M[i] @ q)) for i in top]
```

The invariant to assert in tests: `len(ids) == matrix.shape[0]` and
`sqlite row pid == ids[i]` for sampled i — the Week-07 V2 check, because
this app *is* a tiny multimodal index.

## 4. UI composition: three tabs, one state

```python
with gr.Blocks() as demo:
    with gr.Tab("Ingest"):
        up = gr.File(file_types=["image"])
        name = gr.Textbox(label="Product name")
        status = gr.Textbox()
        up.upload(lambda f, n: f"ingested: {ingest_image(f, n, conn, M, IDS)}",
                  [up, name], status)
    with gr.Tab("Search"):
        q = gr.Textbox(label="Query")
        gallery = gr.Gallery()
        q.submit(lambda s: [(path_of(i), f"{s:.2f}") for i, s in search(s, M, IDS)],
                 q, gallery)
    with gr.Tab("Catalog"):
        grid = gr.DataFrame(value=lambda: pd.read_sql("SELECT * FROM products", conn))
```

State flows through the module-level `conn`/`M`/`IDS` (fine: they are
*application* state, not user state) — user session state stays in
`gr.State` per file 01.

## Exercises

1. Assert the row-alignment invariant in `tests/test_cataloger.py` (sample
   5 ids, re-embed, cosine > 0.999 vs stored row).
2. Add "edit caption" in the Catalog tab that updates SQLite *and* flags
   the matrix row for re-encode — write down why caption edits don't change
   image embeddings (they don't — different encoder inputs).
3. Scale probe: ingest 200 images; measure ingest time and search latency;
   at what count does the brute-force matrix search exceed 50 ms? (That
   number is file 02's reason to exist.)

## Pitfalls

- Two sources of truth (caption in SQLite *and* a sidecar JSON) — SQLite is
  the only fact store; the matrix never stores facts.
- Search returning paths from the *matrix* — the matrix holds ids; paths
  live in SQLite and are joined at render time.
- Ingest without transactions — a crash mid-batch leaves SQLite and the
  matrix divergent; wrap each unit in one transaction.

## Resources

- sqlite3 stdlib docs (transactions, parameterized queries).
- Your Week-07/08 CLIP + BLIP code — the components being composed.
