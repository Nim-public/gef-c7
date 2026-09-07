# Role Design — Least-Privilege Specialist Split

**What you'll learn:** dividing work across crew members by *privilege
and capability*, not by adjective — the role/goal/backstory trio as a
least-privilege exercise, with the split tests that keep roles honest.

## 1. The split procedure

```text
1. List the capabilities the workflow needs (retrieve, SQL, write, verify).
2. Group capabilities that share a trust level and a failure surface.
3. One agent per group; role names the job, goal names "done", backstory
   carries the constraints.
4. Tasks assign work; tools enforce privilege (not the backstory).
```

| Role | Capabilities | Tools | Trust |
|---|---|---|---|
| Researcher | retrieve, read units | corpus tools | read-only |
| Analyst | query tables, verify numbers | analytics toolkit | read-only |
| Writer | compose from supplied evidence | none | unprivileged |
| Verifier | check claims against queries | `verify_number` | read-only |

The analyst/verifier split is deliberate: the agent that *produces* a
number should not be the one that *certifies* it — the same
independence your verification hooks require (W12 file 04-03).

## 2. Role boundaries as tests

```python
def test_writer_has_no_tools():
    assert writer.tools == []            # composition only, no capabilities

def test_analyst_cannot_write():
    # analytics toolkit excludes write paths (W10 read-only-first)
    assert not any("insert" in t.name or "update" in t.name
                   for t in analyst.tools)
```

The backstory says "meticulous"; the *tool list* is what makes it true.
Role design is least-privilege when the enforcement is in the toolkit
construction, not the adjective.

## 3. The role-goals checklist

```text
[ ] each role owns capabilities no other role has (or is merged)
[ ] goals state measurable outputs (expected_output matches)
[ ] backstories carry constraints, not personality
[ ] no role's tools overlap another's write surface
[ ] the hand-off between roles is a task `context`, not free chat
```

## 4. CrewAI roles vs Agno Team roles vs W11 handoffs

| Framework | Role expression | Enforcement |
|---|---|---|
| CrewAI | role/goal/backstory strings | tasks + tool assignment |
| Agno `Team` | member `role` field | team's internal routing |
| W11 handoffs | handoff descriptions | the loop's control flow |

Same concept, three syntaxes — the *enforcement* is always tools-plus-
tasks. The framework-completion table gains its final rows here.

## Exercises

1. Design your crew's roles via the §1 procedure; write the capability
   table (role × tools × trust); run the boundary tests (§2).
2. Adjective-audit drill: find one adjective-only backstory in your
   drafts; replace with a constraint; re-run its battery case.
3. Privilege drill: attempt a forbidden capability through each role
   (writer tries to query SQL); the tool layer must refuse — the
   backstory is not the wall.

## 5. Role design in one table (the crew's org chart)

| Role | Owns | Must NOT own | Battery case |
|---|---|---|---|
| Researcher | corpus reading + citing | numeric claims | citations present |
| Analyst | exact numbers via SQL | corpus interpretation | `sql_used` present |
| Writer | composition from evidence | retrieval | no invented sources |
| Verifier | independent checks | producing claims | mismatch flagged |

The org chart is the role design's deliverable — four columns per role,
the "must NOT own" column doing the least-privilege work. Every row's
battery case is the test that keeps the chart true after refactors.

## 6. The role pin note

**Task:** extend `reports/sdk-versions.md` with the crew definition:
roles, their tool lists, the process mode, and the boundary-test
command.

**Worked approach:** role strings are prompts and tool lists are
privileges — both are configuration; the pin note records when the
org chart was last verified by the boundary tests.

**Pass criterion:** note committed; boundary tests green as recorded.

## Pitfalls

- Roles split by politeness ("senior", "junior") — split by capability
  and privilege; seniority is not an architecture.
- Backstories carrying the *whole* constitution — constraints belong in
  backstories, rules belong in the crew's shared task descriptions; one
  source per rule.
- Trust assumed from role names — the tools are the privilege; test
  them.