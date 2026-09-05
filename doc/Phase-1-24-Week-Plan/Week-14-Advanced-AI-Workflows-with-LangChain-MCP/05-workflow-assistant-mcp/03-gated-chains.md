# Gated Chains — Cross-Server Automation

**What you'll learn:** the cross-server chain: a workflow touching two
or more servers (read from files → write to RAG), with gates at every
state-changing step — the W13 WAIT pattern, federated.

## 1. The chain

```text
1. files__list_files          (read — no gate)
2. files__read_file           (read — no gate)
3. agent proposes ingest plan (propose)
4. GATE: human approves the plan
5. rag__retrieve (verify not already ingested)
6. files__write_file → data/sandbox/ingested/   (state change, gated)
7. rag server re-index (gated)
```

| Step | Server | Gate |
|---|---|---|
| 1–3 | files | no (read-only) |
| 4 | — | **approve** |
| 6 | files | **write gate** |
| 7 | rag | **ingest gate** |

The chain is the W13 story-generator pattern with servers as nouns:
propose → WAIT → apply. Every state change gates; every read runs free.

## 2. The implementation (LangGraph nodes per server call)

```python
class IngestState(TypedDict):
    files: list[str]
    plan: str
    approved: bool
    ingested: Annotated[list[str], operator.add]

builder.add_node("list_files", files_list_node)
builder.add_node("propose", propose_ingest_node)
builder.add_node("verify", rag_verify_node)
builder.add_node("ingest", rag_ingest_node)

builder.add_edge(START, "list_files")
builder.add_edge("list_files", "propose")
# compile with interrupt_before=["ingest"]  ← the gate
```

The cross-server chain is a graph whose nodes call *different servers* —
the adapter namespaces the calls, the gates interrupt before state
changes, the checkpointer holds the workflow across the human pause.

## 3. The chain's battery

| Case | Assert |
|---|---|
| approve flow | files land in sandbox, RAG re-indexes |
| reject flow | nothing ingested, rejection recorded |
| partial failure (step 7 fails) | sandbox files marked, retry plan |
| duplicate detection | step 5 skips already-ingested units |

The battery runs the chain against test servers (the W10 battery's
federated edition): each case asserts the *server call sequence* from
the trace — cross-server chains fail by calling the wrong server in the
wrong order.

## 4. The chain's audit trail

| Event | Recorded as |
|---|---|
| file read | adapter log (server=files) |
| plan proposed | trajectory row |
| approval | human_edit event |
| ingestion | RAG server log + trajectory |

Every cross-server event lands in the store with its server namespace —
the audit trail answers "which server did what, when, on whose
approval", which is the question every federated system must answer.

## 5. The chain's state schema (the workflow's contract)

```python
class IngestState(TypedDict):
    files: list[str]
    plan: str
    approved: bool
    ingested: Annotated[list[str], operator.add]
    failed: Annotated[list[str], operator.add]
```

| Field | Writer | Reader |
|---|---|---|
| `files` | list_files node | propose node |
| `plan` | propose node | human gate |
| `approved` | human (via update_state) | ingest node |
| `ingested` / `failed` | ingest node (append) | retry planner |

The W13 team-state discipline (file 04-03), federated: one writer per
field, the human writes through `update_state`, and the failed-list is
the partial-failure drill's substrate.

## Exercises

1. Build the ingest chain; run the approve flow end-to-end; verify both
   servers' logs and the audit trail.
2. Reject drill: reject at the gate; nothing ingested; the rejection
   reason lands in the store.
3. Partial-failure drill: kill the RAG re-index mid-chain; the sandbox
   files are marked and the retry plan proposes only the remainder.
4. Schema drill: write the §5 table; probe for two-writer fields; add
   merge policies or split.