# Platform Guardrails — Moderation and PII Layering

**What you'll learn:** platform-level guardrails: moderation endpoints
and PII detection as a layer *in front of* your agent, layered with your
own firewall stack — each layer catching what the others miss.

## 1. The layering

```text
user input
  ├─▶ [1] platform moderation endpoint     (hosted classifier)
  ├─▶ [2] local PII detector               (regex + NER, your data)
  ├─▶ [3] your W13 firewall layers         (instruction patterns)
  └─▶ agent (constitution + tools + output filters)
```

| Layer | Catches | Latency cost |
|---|---|---|
| 1. moderation endpoint | policy violations, harmful content | ~100 ms (hosted) |
| 2. local PII detector | emails, phones, keys in *input* | ~5 ms |
| 3. your firewall | instruction patterns, known attacks | ~1 ms |
| 4. agent + filters | the rest | — |

The layering principle from W13 file 06-03: every stage carries a
defense; the platform layers add *independent* classifiers that don't
share your regexes' blind spots. Cost: the moderation call is one more
hosted request — gate-worthy content only (the W10 triage table).

## 2. The moderation layer

```python
def moderation_check(text: str) -> dict:
    """Hosted moderation: returns flagged categories."""
    result = moderation_client.create(input=text)
    flagged = [r.category for r in result.results if r.flagged]
    return {"flagged": bool(flagged), "categories": flagged}
```

| Result | Action |
|---|---|
| clean | proceed to the agent |
| flagged: violence/hate/etc | refuse with the safety message |
| flagged: self-harm | refuse + resources message (the human one) |

The moderation decision maps to the W10 refusal paths — same handler
map (file 01-03), one more exception class. The refusal *messages* are
yours; the detection is the platform's.

## 3. The local PII detector (your data's rules)

```python
PII_PATTERNS = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "phone": r"\+?\d[\d\s-]{8,}\d",
    "api_key": r"sk-[A-Za-z0-9]{20,}",
}

def detect_pii(text: str) -> dict[str, list[str]]:
    found = {name: re.findall(pat, text)
             for name, pat in PII_PATTERNS.items()}
    return {k: v for k, v in found.items() if v}
```

| Finding | Action |
|---|---|
| email/phone in input | mask before logging; proceed masked |
| api_key shape | refuse immediately (a leaked key is an incident) |
| custom patterns (your domain) | mask per your manifest's sensitivity |

The local detector covers what the platform moderation does not know:
*your* sensitive shapes. It runs on inputs AND outputs — the W9
firewall's PII extension, bidirectional.

## 4. The guardrail battery (the layered test)

| Case | Layer expected to fire |
|---|---|
| harmful content request | 1 (moderation) |
| input containing an API key | 2 (PII) — refuse |
| injection phrasing | 3 (your firewall) |
| clean query | all layers pass silently |

The battery asserts *which layer* fired — the layering's value is
defense in depth, and the test proves each layer catches its class. A
case caught by an earlier layer must also pass through the later layers
cleanly (no double-refusals with conflicting messages).

## Exercises

1. Wire the moderation endpoint as layer 1; run the battery; verify the
   refusal paths and the latency added.
2. PII drill: feed an input with an embedded key; the detector refuses
   before the moderation call — ordering and masking verified.
3. Layer-attribution drill: for each battery case, log which layer
   fired; the attribution table is the layering's proof.

## Pitfalls

- Moderation on every request including chitchat — the hosted call
  costs; gate-worthy content only (the triage table).
- PII masking that doesn't cover outputs — exfiltration via answers is
  the bidirectional case; mask both directions.
- Double-refusals with conflicting messages — the layers must compose;
  the battery asserts one coherent refusal.