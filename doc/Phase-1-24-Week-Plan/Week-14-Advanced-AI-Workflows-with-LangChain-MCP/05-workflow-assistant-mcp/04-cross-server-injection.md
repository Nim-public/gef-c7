# Cross-Server Injection Testing

**What you'll learn:** injection across server boundaries: a poisoned
file ingested by the files server, read by the RAG server, and served to
the agent — the W13 battery, federated. The defense stack must hold
*across* servers.

## 1. The federated attack path

```text
1. attacker writes poison.txt into the files sandbox
2. ingest chain proposes it (files server reads it fine)
3. RAG server ingests it → poisoned unit in the corpus
4. agent retrieves it → observation contains the injection
5. model reads it → the attack lands
```

| Stage | Defense that should fire |
|---|---|
| 2 | ingest-plan review (human sees the file) |
| 3 | the RAG server's ingest firewall (W13 sanitize at ingest) |
| 4 | the prompt-build firewall (host-side) |
| 5 | the constitution (rule 6) + output filters |

Five servers' worth of defense must hold across the chain — the drill
plants the poison at stage 1 and asserts *every* stage's defense fired.

## 2. The federated battery

```python
FEDERATED_CASES = [
    ("poison via file → ingest → retrieve", "all layers fire"),
    ("poison via RAG metadata field", "ingest firewall"),
    ("poison via util server response", "host-side sanitize"),
    ("poison in a *legitimate* file's footer", "ingest firewall + rule 6"),
]

@pytest.mark.parametrize("path,expected", FEDERATED_CASES)
def test_cross_server_injection(path, expected, federated_stack): ...
```

The last case is the realistic one: the poison hides in a legitimate
document's footer — not a standalone evil file. The ingest firewall must
scan *content*, not just filenames.

## 3. The containment proof (per server, per stage)

| Stage | Contained by | Drill evidence |
|---|---|---|
| files server | sandbox FS + no tokens | the process env probe |
| ingest plan | human approval | the gate test |
| RAG ingest | the sanitize pass | poisoned-unit fixture (W13) |
| retrieval | prompt-build firewall | the observation firewall test |
| generation | constitution + output filter | the W9 output battery |

The containment proof is a table with one row per stage — each row
cites the drill that fired at that stage. The federation adds *stages*,
not weaknesses, when each stage carries its own defense.

## 4. The federated trust boundaries (the security page)

```markdown
## Federated trust boundaries (W14)
- files → RAG: content sanitized at RAG ingest; human approves plans
- RAG → agent: observations firewalled at prompt-build
- util → agent: responses schema-validated, no free text
- agent → user: output filters + citation gate
- No server trusts another server's output raw.
```

## 5. The injection pin note

**Task:** extend `reports/sdk-versions.md` with the federated security
stack: the defense layers per stage (§3's table), the battery command,
and the last drill date.

**Worked approach:** the federated battery has the most stages of any
security drill — the pin note records which layer fired at which stage
and when the battery last ran.

**Pass criterion:** note committed; the battery command green as
recorded.

## 6. The injection battery (drills, numbered)

1. Poison via the files server; run the ingest chain; verify every
   stage's defense fired (the §1 table, one row each).
2. Metadata-drill: poison a RAG *metadata field* (not text); the ingest
   firewall must cover metadata too — extend it if not.
3. The realistic-footer drill: hide the injection in a legitimate doc's
   footer; the content scan catches it while the file passes human
   review (too long to read fully).
4. Pin drill: extend the note; confirm the battery covers all five
   stages.

## Pitfalls

- Testing injection only at the query — the federated path has more
  doors; this file's battery covers the federated ones.
- Server-to-server trust ("the files server is internal") — internal
  servers get compromised; no server trusts another's output raw.
- Defenses re-implemented per server — import the W13 sanitize/firewall
  functions; one defense, many callers.