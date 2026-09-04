# 05 — Ragas & Explanations: Deep Dive

> Parent topic: [../05-response-evaluation-explanations.md](../05-response-evaluation-explanations.md) · Week 5 index: [../../README.md](../../README.md)

The four Ragas metrics (faithfulness, answer relevancy, context precision, context recall) as a diagnosis system — each score maps to a pipeline stage, and the diagnosis drives the fix.

**Key content from the parent topic:**

- **Faithfulness**: is every claim in the response supported by the retrieved context? Low = generation hallucinating
- **Answer relevancy**: does the response address the question? Low = routing or prompt failure
- **Context precision**: are the relevant chunks ranked at the top? Low = reranking needed
- **Context recall**: did retrieval surface everything needed? Low = chunking or embedding gap

The diagnosis table maps score patterns to fixes: faithfulness low + precision high = generation lying; recall low + precision high = retrieval missing content. The fix targets the failing stage, not the whole pipeline.

The explanation levels (citations → retrieval transparency → self-check statements) make the system's confidence visible to users — the auditability that enterprise deployments require.

For the full implementation, the judge calibration, and the exercises, see the parent file and the W5-05 exercises.
