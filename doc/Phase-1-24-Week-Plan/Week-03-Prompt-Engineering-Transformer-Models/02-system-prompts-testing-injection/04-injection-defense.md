# 02.4 — Injection Defense

> Subfolder index: [README.md](README.md) · Parent: [../02-system-prompts-testing-injection.md](../02-system-prompts-testing-injection.md)

---

## What you'll learn

- The attack surface map for your agent (every input channel, every output consumer)
- The defense stack, layer by layer, with bypass classes
- The red-team drill design (W23-03's suite, prompt-layer edition)
- The residual-risk documentation discipline

## 1. The attack surface map

Every place data enters the model, and every place model output goes:

```text
INPUTS                          OUTPUTS
├─ user chat                    ├─ user-facing reply
├─ retrieved documents (W4)     ├─ tool calls (W10)
├─ tool results (W10)           ├─ database writes (W6)
├─ uploaded files (W9)          ├─ emails/Slack (W14-05)
├─ web pages (crawled)          └─ stored memories (E9)
└─ images (W9-03)
```

Each input channel is an injection vector (W3-02's map); each output consumer defines the blast radius. The defense design question: *for each input channel, what is the worst instruction it could carry, and what would the output consumer do if obeyed?*

## 2. The defense stack, layer by layer

| Layer | What it does | Bypass class |
|---|---|---|
| **1. Input screening** | regex/classifier on entry | encoding, novel phrasing |
| **2. Delimiting + goal anchoring** | data marked untrusted; goal restated | tag spoofing, semantic reframing |
| **3. Privilege separation** | model proposes, separate executor approves | social-engineering the approver |
| **4. Output validation** | schema + allow-lists on actions | valid-format harmful actions |
| **5. Least privilege** | tools scoped to minimum | approved-but-dangerous tools |
| **6. Rate/step limits** | bounded damage per session | distributed slow attacks |

The stack is evaluated per *family* (file E7-02's taxonomy) — each family has bypasses for the layers above it, which is why layering is the design and single defenses are the anti-pattern.

## 3. The layer-bypass drill (design your tests from the cracks)

| Layer | Known bypass | Test |
|---|---|---|
| screening | base64 the payload | encoded attack battery |
| delimiting | spoofed close-tags in data | `</context>` in retrieved text |
| goal anchoring | "new goal" framing | multi-turn goal replacement |
| output validation | valid JSON with harmful content | schema-valid exfiltration |
| least privilege | approved tools chained dangerously | tool-combination drill |

Each row = one pytest case (W3-02 §5's battery) — the drill is the suite's design input.

## 4. Residual-risk documentation

```markdown
## Accepted risks (v3)
1. Multi-turn slow-burn escalation (family 5) across >20 turns is not fully
   detected. Mitigation: per-10-turn re-anchoring + session caps.
   Residual: a determined 30-turn attack may succeed. Monitored via drift alerts.
2. Confident-wrong outputs from the classifier (no hallucination detection
   at the semantic level). Mitigation: citation verification only.
   Residual: unsupported claims with correct format pass.
```

Accepted risks are **explicit, bounded, and monitored** — the E7-01 §4 discipline. "We tested and it seems fine" is not documentation.

## Exercises

1. Surface map: draw your agent's full input/output map (§1) — count the channels; identify the one with the largest blast radius.
2. Layer-bypass suite: implement one test per bypass class (§3) against your agent; log pass/bypass per layer.
3. The combo attack: screening passes + delimiting holds, but a *valid tool call* causes harm — design it, then add the missing gate.
4. Residual-risk audit: for each remaining bypass, write the accepted-risk entry (file 01 §4's format) — or the fix.
5. Cross-channel drill: an attack split across a document (W4), a tool result (W10), and user turns — the multi-channel assembly attack; test your layers in combination.

## Pitfalls

- **Layer confidence** — "my regex screen is good" is not a defense; every layer has a bypass class (§3)
- **Guards tested individually, attacked in combination** — the multi-channel drill (ex. 5) is the real test
- **Output channels forgotten** — the Slack post is an output surface; injection via *output* (W14-05's chain) hits downstream systems
- **Residual risks undocumented** — reviewers assume unlisted risks are unknown; name them
- **Security as a phase** — new tools/channels re-open the surface; the drill re-runs at every architecture change (E8-01's manifest gates it)

## Resources

- W3-02 parent, W5-04 (the guardrail sandwich), E7-01/02/03 (the deep versions) — composed here
- [OWASP LLM01](https://owasp.org/www-project-top-10-for-large-language-model-applications/) · [MITRE ATLAS](https://atlas.mitre.org/) — the attack catalogs
- W10-04 (the trajectory evidence) — the monitoring layer
