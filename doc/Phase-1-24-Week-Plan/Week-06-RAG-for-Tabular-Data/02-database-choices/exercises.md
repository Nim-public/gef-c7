# Exercises — Database Choices

Expanded set with worked approaches. The deliverable: the engine choice
evidenced by dialect probes, the storage map verified, the read-only
wall proven, and the environment ladder implemented.

## 1. Engine choice (from 01-sqlite-mysql-postgres)

**Task:** run the dialect probes against SQLite; record which MySQL/
Postgres constructs fail; port Q2 (monthly revenue) into all three
dialects.

**Worked approach:** the probes are the diff table verified live —
`date('now')` works on SQLite, `DATE_FORMAT` fails, `strftime` wins.
The three-way port makes the dialect differences concrete for the
schema prompt.

**Pass criterion:** the probe table committed; the three dialect
versions of Q2 written side-by-side.

## 2. The storage map (from 02-storage-coexistence)

**Task:** draw your capstone's storage map (SQLite + LanceDB + files)
with the linking keys; the consistency drill across all stores.

**Worked approach:** the map's test is that every linking key resolves —
a unit_id lookup in LanceDB, a SQL query in SQLite, a file path on
disk. The consistency drill (counts across stores) is the sync rule's
evidence.

**Pass criterion:** the map committed; the consistency drill green; the
drift drill (orphan detection) proven.

## 3. The read-only wall (from 03-read-only-safety)

**Task:** open the warehouse `mode=ro`; attempt INSERT/DELETE/PRAGMA —
all refused; disable the SQL validator and confirm the wall still
holds; run the wall's test suite.

**Worked approach:** the layer-independence drill is the structural
argument — the file-level wall holds even when the SQL-level validator
is broken. The test suite joins CI.

**Pass criterion:** 3/3 write attempts refused at the connection level;
the validator-independence drill documented; the tests in CI.

## 4. The environment ladder (from 04-environment-ladder)

**Task:** implement the `ENV` config split; verify the per-env settings;
the promotion checklist rehearsal (staging → prod on your machine).

**Worked approach:** the promotion is a gate passage — the acceptance
command re-run on the promoted environment. The leak drill proves the
no-prod-to-dev rule.

**Pass criterion:** the config split verified; the promotion rehearsal
green; the leak drill refused.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Dialect probes + three-way port | probe table | 3 |
| Storage map with resolving keys | map + consistency drill | 4 |
| Read-only wall structurally proven | wall tests in CI | 4 |
| Environment ladder implemented | config split + promotion | 3 |
| Pin note (engine choice) | pin note | 2 |

**Pass bar:** 14/18 to proceed to file 03 (RAG over structured data).
The read-only wall (4-pointer) is the choices week's non-negotiable —
the structural proof is what makes the agent's SQL tool safe.

## 6. The choices pin note (the storage decisions' manifest)

**Task:** consolidate the storage decisions in `reports/sdk-versions.md`:
the engine choice, the storage map, the read-only wall, and the
environment ladder — one block.

**Worked approach:** the choices manifest follows the pin discipline:
engine + dialect, the polyglot map, the structural wall, and the
environment ladder — each citing its drill.

**Pass criterion:** the manifest lists all four with green commands as
recorded.

## 8. The storage-choice quiz (self-tested)

**Task:** answer without notes: (a) why does SQLite win for the capstone
demo? (b) why must the vector store and warehouse link by keys rather
than duplicate data? (c) why is the ro-mode wall stronger than the
validator? (d) why does prod data never flow to dev? One paragraph
each.

**Worked approach:** the quiz is the storage decisions' compression
test — each answer names the mechanism (zero-ops, linking keys,
structural enforcement, blast radius).

**Pass criterion:** four paragraphs mechanically correct; added to the
recap sheet family.

## Pitfalls recap

- Engine choice by familiarity instead of heuristics — the table's axes
  decide; SQLite's zero-ops wins for the capstone.
- Dialect mixing in Text2SQL — the probes and the schema prompt state
  the dialect; the repair loop catches the rest.
- Prod data flowing to dev — the ladder's rule; the leak drill keeps it
  visible.