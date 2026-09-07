# Exercises — Embeddings & Vector Databases

> Subfolder index: [README.md](README.md) · Parent: [../03-embeddings-vector-databases.md](../03-embeddings-vector-databases.md)

Labs for this subfolder. Shared fixture: the W4-02 chunks (from your corpus) + the 25-query eval set.

---

## E1 — The scaling curve (file 01)

1. Brute-force search at N = 1k/10k/100k — latency and memory per query; plot the curve.
2. The normalization proof: dot vs L2 on normalized vs unnormalized vectors — verify the ranking equivalence.
3. The determinism check: same query, 10 runs — identical results (they must be).

**Worked approach:** exercise 1's curve is the index-motivation baseline — without it, the IVF/LanceDB complexity is unjustified.

## E2 — FAISS mastery (file 02)

1. IVF recall sweep: nprobe ∈ {1, 5, 10, 50} at nlist=100 — recall@5 and latency; the knee table.
2. Training-size test: IVF trained on 1k/5k/30k — recall and stability; the minimum training size.
3. The metric flip: L2 vs IP on normalized and unnormalized vectors — the ranking equivalence verified (or disproven).

**Worked approach:** exercise 2's training-size test is the gotcha that bites every first IVF deployment — the table prevents it.

## E3 — LanceDB production (file 03)

1. Persistence test: create, close, reopen — all data and searchability intact.
2. The update lifecycle: add → update → delete → verify each reflected in search results immediately.
3. The security test: 3 personas × 10 queries with permission prefilters — zero cross-tenant leaks.
4. Schema evolution: add a column to an existing table — verify the index and search still work.

**Worked approach:** exercise 3's zero-leak verification is the E7-01 security evidence — the prefilter isn't a security control until it's tested as one.

## E4 — The consistency certification (file 04)

1. `validated_search` implementation with all five checks; each check tested individually.
2. The drift canary: change the contract; the assertion fires; fix; the assertion passes.
3. The metadata completeness audit: 100 hits — every required field present; the malformed-hit detector.

**Worked approach:** exercise 2's drift canary is the runtime safety net — the contract assertion that catches what code review misses.

## Self-assessment

- Can you state your recall/latency operating point and the sweep that found it?
- Can you implement the five-check query-time validation and test each check?
- Can you explain, to a reviewer, why prefilter is a security control and postfilter is not?
