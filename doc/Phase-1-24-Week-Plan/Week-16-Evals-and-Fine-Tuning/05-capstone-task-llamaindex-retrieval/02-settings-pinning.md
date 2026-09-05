# Settings Pinning — Embedder/Chunker, Not Defaults

**What you'll learn:** LlamaIndex's `Settings` global: pin the embedder,
the LLM, and the node parser explicitly — the defaults are convenient
for tutorials and a silent-mismatch factory for your corpus.

## 1. The pinning block

```python
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5")      # your W8-memo embedder
Settings.llm = OpenAI(model="pinned-model-id", temperature=0)
Settings.node_parser = SentenceSplitter(
    chunk_size=512, chunk_overlap=64)          # your W4 settings
```

| Setting | Your value | Source |
|---|---|---|
| `embed_model` | the W8 memo's encoder | the encoder decision |
| `llm` | pinned id, temperature 0 | the AGENT_CONFIG |
| `node_parser` | W4's chunk settings | `preproc-settings.json` |

The pinning block is your `AGENT_CONFIG` in LlamaIndex's dialect —
every value traced to a decision memo, none left to defaults.

## 2. The default-mismatch failure (the silent killer)

| Unpinned setting | Default | Mismatch with your stack |
|---|---|---|
| embed_model | OpenAI text-embedding-ada | different space than your LanceDB vectors |
| chunk_size | 1024 | your W4 chunking was 512 |
| llm | gpt-4o-mini-class | not your pinned eval model |

The embedder mismatch is the killer: LlamaIndex re-embeds with its
default, your LanceDB vectors were built with yours — queries and
vectors in different spaces, retrieval "works", hits are wrong. The
parity loop (W12 file 02-01) catches it in one run; pinning prevents it
entirely.

## 3. The settings audit (the pin's test)

```python
def test_settings_pinned():
    assert "bge-small" in str(Settings.embed_model)     # your embedder
    assert Settings.node_parser.chunk_size == 512        # your W4 chunking
    assert "pinned-model-id" in str(Settings.llm)        # your model
```

| Check | Catches |
|---|---|
| embedder identity | the space mismatch |
| chunk size | the W4 settings drift |
| model id | the eval-config drift |

The audit runs at import in the eval harness — the pin is enforced, not
documented.

## Exercises

1. Write the pinning block; run the settings audit; deliberately unpin
   one setting and watch the audit fail.
2. Parity drill: run the parity loop (W12 file 02-01) with LlamaIndex
   retrieval vs your W9 stack — identical hits or name the mismatch.
3. Pin-note drill: record the Settings values in `reports/sdk-versions.md`;
   the LlamaIndex version joins the pin.