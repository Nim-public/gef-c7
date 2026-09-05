# Scope Containment — Paths, Tokens, Allow-Lists

**What you'll learn:** per-server scope containment: which paths each
server may touch, which tokens it holds, which tools the assistant may
call — the W10 read-only posture, federated per server.

## 1. The containment matrix

| Server | Paths | Tokens held | Tools allowed |
|---|---|---|---|
| rag | `data/lancedb` (ro) | none (local) | retrieve, get_unit_text |
| files | `data/sandbox/**` (rw) | none | list, read, write (sandbox only) |
| util | — | util API key | time_now only |

```python
SCOPE = {
    "rag":   {"paths_ro": ["data/lancedb"], "tokens": [], "tools": ["retrieve", "get_unit_text"]},
    "files": {"paths_rw": ["data/sandbox"], "tokens": [], "tools": ["list_files", "read_file", "write_file"]},
    "util":  {"tokens": ["UTIL_API_KEY"], "tools": ["time_now"]},
}
```

| Containment | Enforced by |
|---|---|
| path scopes | the server's own validators (W10 rule: server revalidates) |
| token scopes | per-server env, never shared |
| tool allow-lists | the adapter (only namespaced allow-listed tools exposed) |

The W10 containment rules per server: the RAG server reads LanceDB and
holds no tokens; the files server writes only in the sandbox; the util
server holds one key and exposes one tool. No server sees another's
tokens.

## 2. The token isolation rule

```python
# each server process gets ONLY its own env:
# rag:   (no tokens — local LanceDB)
# files: (no tokens — sandbox FS)
# util:  UTIL_API_KEY=...
```

| Threat | Containment |
|---|---|
| RAG server compromised | attacker gets corpus reads, no keys |
| files server compromised | attacker gets sandbox writes, no keys |
| util server compromised | attacker gets the util key only |

Blast radius per server equals its scope. The containment matrix is the
threat model's evidence — one row per server, one wall per column.

## 3. The assistant's exposure (what the LLM sees)

```python
EXPOSED_TO_LLM = {
    "rag__retrieve": "search the corpus",
    "rag__get_unit_text": "read a unit",
    "files__list_files": "list sandbox files",
    "files__write_file": "write sandbox files (gated)",
    "util__time_now": "current time",
}
```

The LLM sees the federated tools — *minus* anything the gates hold back
(the files server's write tool is gated, W10 file 04). The adapter's
exposure list is the gate policy's projection: what exists, what is
gated, what the model may see.
## 5. The containment battery (the matrix as tests)

```python
CONTAINMENT_CASES = [
    ("rag server reads outside data/lancedb", "refused"),
    ("files server writes outside data/sandbox", "refused"),
    ("util server reads another server's env", "impossible: env isolation"),
    ("assistant calls an unexposed tool", "refused at adapter"),
]

@pytest.mark.parametrize("attempt,expected", CONTAINMENT_CASES)
def test_containment(attempt, expected): ...
```

The battery is the containment matrix as executable tests — four
attempts, four refusals, one per wall. It runs in CI on every server or
adapter change; a wall that stops being tested is a wall in name only.

## Exercises

1. Build the containment matrix; verify each server's process env with
   a probe (print env keys inside each server — CI-assert the
   isolation).
2. Path-scoping drill: point the files server at `data/raw/`; the
   validator must refuse — the scope is the wall, tested.
3. Exposure drill: remove a tool from `EXPOSED_TO_LLM`; verify the model
   cannot call it (the adapter filters the schemas).
4. Battery drill: implement the §5 cases; wire into CI; one wall-removal
   mutation must turn the suite red.

## Pitfalls

- Shared tokens across servers — one compromised server leaks everything;
  per-server env is the wall.
- Path scopes in instructions only — the server validates paths; the
  model is untrusted.
- The exposure list drifting from the servers' actual tools — the
  tools/list diff runs per server at connect.