# 03.3 — Translation

> Subfolder index: [README.md](README.md) · Parent: [../03-nlp-tasks.md](../03-nlp-tasks.md)

---

## What you'll learn

- Dedicated translation models (MarianMT/opus-mt, NLLB) vs LLM translation — measured
- The back-translation quality check
- Language-code discipline (the classic failure)
- Where translation fits the capstone (the W2-06 task's optional capability)

## 1. Dedicated translation models

```python
from transformers import pipeline

en_hi = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")
en_hi("Knowledge retrieval improves factuality.")[0]["translation_text"]

# many-to-many with language codes:
nllb = pipeline("translation", model="facebook/nllb-200-distilled-600M",
                src_lang="eng_Latn", tgt_lang="hin_Deva")
nllb("Retrieval makes answers verifiable.")[0]["translation_text"]
```

| Model family | Coverage | Notes |
|---|---|---|
| **opus-mt** (Helsinki-NLP) | ~1,400 pairs, one model per pair | small, fast, CPU-friendly; name says the direction — `en-hi` ≠ `hi-en` |
| **NLLB-200** | 200 languages, any→any | one model; language *codes* like `hin_Deva` (script included!) |
| **M2M-100** | 100 languages | earlier many-to-many |
| **LLMs** | any language the model knows | style-controllable via prompt; hallucination risk on low-resource pairs |

The classic failure: swapping the direction — `en-hi` used for Hindi→English produces gibberish that *looks* like translation. The model card's language-pair table is the contract.

## 2. Back-translation quality check

```python
def backtranslate(text: str, via: str = "hi") -> str:
    to_x = pipeline("translation", model=f"Helsinki-NLP/opus-mt-en-{via}")
    back = pipeline("translation", model=f"Helsinki-NLP/opus-mt-{via}-en")
    return back(to_x(text)[0]["translation_text"])[0]["translation_text"]

original = "Knowledge retrieval improves factuality."
roundtrip = backtranslate(original)
print(original); print(roundtrip)
# meaning drift visible: 'Knowledge search improves how factual it is.'
```

Back-translation measures *meaning preservation*, not fluency: if the round-trip loses the key term, forward translation likely did too. Score with token overlap (BLEU/ROUGE vs original, file W7-05) plus manual reading of the key terms.

## 3. LLM translation (the alternative)

```python
prompt = f"""Translate to Hindi. Preserve technical terms in English where they are
product names. Keep the tone professional.

Text: {text}"""
# LLM translation: style-controllable, handles context, but can omit/hallucinate
```

| | Dedicated (opus-mt/NLLB) | LLM |
|---|---|---|
| determinism | ✅ greedy | sampling-dependent |
| cost at volume | ~free self-hosted | per token |
| domain adaptation | none (retrain) | prompt-injectable glossary |
| long-context coherence | per-sentence | full context |
| low-resource pairs | varies | varies — verify! |

Selection: volume + fixed pairs → dedicated; style/context-sensitive + low volume → LLM; regulated content → dedicated + human review.

## 4. The glossary pattern (domain terms)

Translation models mangle product names and domain terms. The fix is a glossary constraint:

```python
GLOSSARY = {"RAG": "RAG", "AcmeCloud": "AcmeCloud", "tier 2": "टियर 2"}

def apply_glossary(translation: str, source: str) -> str:
    for en, target in GLOSSARY.items():
        if en in source:            # post-fix: enforce the term in the translation
            pass                    # per-term replacement or re-prompt with the glossary
    return translation
```

Simpler and more reliable: include the glossary in the LLM-translation prompt ("Translate 'RAG' as 'RAG'; translate 'tier 2' as 'टियर 2'"). Dedicated models need post-processing replacements or fine-tuning — the W17 route if volume justifies it.

## Exercises

1. Direction audit: for 5 language pairs available in opus-mt, translate both directions and back — build the pair-quality table; find the weak direction.
2. NLLB codes: translate one text into 3 scripts (Devanagari, Arabic, Thai) — verify script rendering survives your JSONL storage (W1-04 encoding rules).
3. Glossary enforcement: 10 domain terms through LLM translation with and without the glossary in the prompt — measure term-preservation rate.
4. Back-translation scoring: BLEU (W7-05) between original and round-trip for 10 texts — the score distribution per language pair.
5. Capstone integration: the W2-06 task's translation capability — which 2 languages, which model, what QA (back-translation + spot human check)? Write the decision into the integration README.

## Pitfalls

- **Language-code confusion** — `hin_Deva` (script) vs `hin` (macro); NLLB wants the full code, opus-mt wants the pair
- **Translating placeholders/markup** — `{variable}` and `<context>` tags get mangled; extract, translate, re-insert (W1-02's template discipline)
- **Numbers and dates reformatted** — "5 business days" → digit/dash conventions change per locale; verify numerals survived
- **Back-translation as proof of correctness** — it measures round-trip coherence, not accuracy; a human check on key terms is still required
- **Cultural/context loss** — honorifics and formality registers (Hindi आप/तुम) are tone-bearing; flag them in QA

## Resources

- HF [translation task guide](https://huggingface.co/docs/transformers/tasks/translation) — the pipeline patterns
- [Helsinki-NLP opus-mt models](https://huggingface.co/Helsinki-NLP) — the pair catalog
- [NLLB-200](https://huggingface.co/facebook/nllb-200-distilled-600M) card — language codes
- W11-04 (voice output of translations), W16-02 (multilingual synthetic data) — composed here
