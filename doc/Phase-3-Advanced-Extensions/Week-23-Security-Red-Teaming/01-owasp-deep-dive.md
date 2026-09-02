# 01 — OWASP LLM Top 10, Mapped to Your Capstone

> E7 index: [README.md](README.md)

**Core topic:** *The OWASP Top 10 for LLM Applications — each risk mapped to your architecture with concrete controls.*

---

## What you'll learn

- The Top 10 risks (2025 list) in plain terms
- Your architecture's exposure per risk — with the controls you already built (W3-02, W5-04, W10-04) and what's missing
- The threat-model worksheet for the capstone README

## 1. The Top 10, mapped

| # | Risk | Plain meaning | Your exposure | Controls (built / missing) |
|---|---|---|---|---|
| LLM01 | **Prompt Injection** | data becomes instructions | HIGH — RAG corpus, web pages, tickets, images (W3-02, W9-03) | ✅ delimiting, goal anchoring, action gates / ⚠️ systematic testing (file 05) |
| LLM02 | **Sensitive Disclosure** | PII/secrets leak via outputs | HIGH — transcripts, DB rows (W6) | ✅ PII scrubbing, read-only DB, citation scope / ⚠️ output PII scanning |
| LLM03 | **Supply Chain** | poisoned models/packages/data | MED — HF models (W2), corpus sources (W1-04 crawl) | ✅ pinned revisions, licenses / ⚠️ corpus provenance audit |
| LLM04 | **Data & Model Poisoning** | training/eval data corrupted | MED — fine-tuning sets (W17), eval sets | ✅ hand-audited seeds / ⚠️ poisoning detection |
| LLM05 | **Improper Output Handling** | unsafe downstream use of outputs | HIGH — generated SQL (W6), code (E3), Slack posts | ✅ validators, allow-lists, gates / ⚠️ output-encoding discipline |
| LLM06 | **Excessive Agency** | too much power, autonomy | HIGH — W14-05's cross-server assistant | ✅ least privilege, HITL gates (W10-04) / ⚠️ formal blast-radius review |
| LLM07 | **System Prompt Leakage** | constitution revealed | MED — every agent | ✅ anti-leak clauses (W3-02) / ⚠️ assume leaked; design so leakage isn't fatal |
| LLM08 | **Vector/Embedding Weaknesses** | corpus poisoning, cross-tenant leaks | MED — W4 index, multi-tenant filters | ✅ prefilter permissions (W5-03) / ⚠️ poisoning detection, tenant isolation tests |
| LLM09 | **Misinformation** | confident false outputs | MED — hallucination (W4-01) | ✅ grounding + citations, insufficiency escape / ⚠️ ongoing eval (W16-01) |
| LLM10 | **Unbounded Consumption** | cost/DoS | MED — loops, big contexts | ✅ RunBudget (W15-01), caps / ⚠️ per-tenant quotas |

**Reading discipline:** your exposure column is a *worksheet*, not a conclusion — each row needs the evidence file (test results, config) attached in the capstone README's security section.

## 2. The threats your capstone actually faces (threat model)

Actor × access × goal:

| Actor | Access | Attack |
|---|---|---|
| End user | the chat input | jailbreak, injection, exfiltration prompts (LLM01) |
| Corpus contributor | documents that enter RAG | indirect injection, poisoning (LLM01/03/04/08) |
| Tool provider | MCP/API responses | injection via tool output, supply chain (LLM01/03) |
| Insider | repo/config access | secrets in prompts, over-scoped agents (LLM02/06) |
| Automated attacker | public endpoint | consumption abuse, enumeration (LLM10) |

For each row: what's the *worst credible outcome*? (PII export? A refund executed? Poisoned eval set?) That's your blast radius — and the priority order for the missing controls.

## 3. The controls you've already built (evidence inventory)

| Control | Where built | OWASP coverage |
|---|---|---|
| Delimited untrusted data + goal anchoring | W3-02 | LLM01 |
| Action gates (HITL) | W10-04, W13-06 | LLM06 |
| Read-only DB user + SQL validator | W6-02/03 | LLM05 |
| Permission prefilter | W5-03 | LLM08 |
| RunBudget (turns/tokens/time/spend) | W15-01 | LLM10 |
| PII scrubbing + masking | W2-02, W4 | LLM02 |
| Pinned revisions + licenses | W2-01, W16-01 | LLM03 |
| Grounding + citations + insufficiency escape | W4-01 | LLM09 |
| Observation truncation + sanitization | W10-05 | LLM01/05 |

The gap analysis (file 05's practice) fills the ⚠️ rows — each missing control becomes a test + a fix.

## 4. The threat-model worksheet (capstone README template)

```markdown
## Security
### Assets
- Capstone corpus (internal docs), user PII in tickets, DB rows, Slack workspace
### Actors & surfaces
- End user (chat), corpus contributors, tool providers, automated attackers
### Top risks (ranked by blast radius)
1. LLM01 via document-embedded injection → refund action (gated, but draft leakage)
2. LLM02 via SQL tool reading PII columns → output disclosure
3. LLM06 via over-broad GitHub token → repo tampering
### Controls (evidence links)
- [battery results](security/battery.md) — 42/45 blocked, 3 findings triaged
- [sandbox config](security/sandbox.md) — read-only DB, scoped tokens
### Residual risks accepted
- ... (name them; "accepted" must be explicit)
```

## Exercises

1. Fill the worksheet for your capstone: assets, actors, top-3 risks by blast radius, controls with evidence links.
2. Control-gap drill: for each ⚠️ row in §1, write the *smallest test* that proves the gap (one sentence + one command).
3. Blast-radius review: take your most powerful tool (W14-05's cross-server assistant) — write the worst credible outcome if fully hijacked, then the control that shrinks it most.
4. Mapping audit: reread W3-02/W5-04/W10-04 files — list every control you built that *isn't* in your worksheet yet (completeness check).
5. Write the "accepted risks" paragraph — three risks you explicitly accept with justification. (Security reviews respect named, reasoned acceptance; they reject silence.)

## Pitfalls

- **Security theater** — controls without tests/evidence are decoration; every row needs an artifact
- **Focusing on jailbreaks only** — LLM01 is one row of ten; supply chain and output handling are where real breaches happen
- **"We use a big provider, we're safe"** — provider safety covers *their* model; your application layer (corpus, tools, gates) is yours
- **Static threat models** — new tools = new surfaces; the worksheet re-runs at every architecture change (W14-05 added four)
- **Undocumented acceptance** — an unnamed accepted risk reads as an unknown risk to a reviewer

## Resources

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — the source list (2025 edition)
- Anthropic/OpenAI security best practices (W3-02's resources) — the control catalogs
- [MITRE ATLAS](https://atlas.mitre.org/) — the attack-technique knowledge base (adversarial ML)
- W3-02, W5-04, W10-04, W15-01/02 — your built control files (the evidence base)
