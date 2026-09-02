# 06 — From Neural Networks to Transformers to LLMs

> Week 1 index: [README.md](README.md)

**Session 2 topic:** *ML → LLMs: Neural networks → transformers, pre-trained vs instruction-tuned models.* You don't need to derive backprop this week — you need a working mental model of the stack:

```
one-hot (file 01) ─► embeddings ─► neural network ─► attention/transformer ─► pre-training ─► instruction tuning ─► the model you call via API (file 07)
```

---

## What you'll learn

- What a neural network computes and how it trains (forward, loss, backward, step)
- Why embeddings replaced one-hot encodings
- What problem attention solves, and the encoder/decoder split
- What "pre-trained" vs "instruction-tuned" means in practice — and how behavior differs
- How to run small open models locally and compare them

## 1. Neural networks in one page

A **neuron** computes a weighted sum + bias, then squashes it through a non-linearity:

```
a = activation(w·x + b)
```

A **network** stacks layers of neurons; a modern LLM is a deep stack of a special layer type (the transformer block). Non-linear activations (`ReLU`, `GELU`) are what let networks learn curves, not just planes.

### Minimal network training in raw PyTorch

```python
import torch
import torch.nn as nn

X = torch.linspace(-1, 1, 64).unsqueeze(1)
y = torch.sin(3 * X)                       # learn a curve, not a line

model = nn.Sequential(nn.Linear(1, 32), nn.ReLU(), nn.Linear(32, 1))
loss_fn, opt = nn.MSELoss(), torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(500):
    pred = model(X)                        # forward pass
    loss = loss_fn(pred, y)                # measure wrongness
    opt.zero_grad()
    loss.backward()                        # backward pass: gradients for every weight
    opt.step()                             # optimizer updates weights
    if epoch % 100 == 0:
        print(epoch, loss.item())
```

The four lines in the loop — **forward, loss, backward, step** — are the training loop of every deep learning model ever trained. `loss.backward()` is backpropagation: calculus chaining gradients from loss back to every parameter.

## 2. Embeddings as learned representations

Recall file 01: one-hot vectors are orthogonal — no similarity. A network's first layer can *learn* the mapping from one-hot (or token ID) to a dense vector where similar things sit close together.

- Word2Vec (2013) showed this yields semantics: `king − man + woman ≈ queen`
- Transformers generalize this: every token gets a **contextual** embedding — `"bank"` in "river bank" vs "bank account" gets different vectors

This single idea — *represent items as learned vectors, do geometry on them* — powers recommendation, search (Week 4), RAG (Weeks 4–6), and multimodal alignment (Week 8: CLIP puts images and text in one space).

## 3. The Transformer (2017) — what problem it solves

Before transformers, sequences were processed step-by-step (RNN/LSTM). Two failures at scale: **no parallelism** (slow) and **long-range forgetting** (information from 500 tokens ago decays).

**Attention** fixes both: every token can *look at every other token* directly and pull in what it needs, weighted by relevance. "It" attends back to "The animal" and finds its referent — in one hop, in parallel.

Key vocabulary you must own:

| Term | Meaning |
|---|---|
| self-attention | tokens attend to other tokens in the same sequence |
| multi-head attention | several attention patterns in parallel (syntax, coreference, topic...) |
| Q, K, V | query/key/value — "what am I looking for / what do I offer / what I pass on" |
| positional encoding | tells the model token order (attention itself is order-blind) |
| feed-forward block | per-token MLP after attention |
| residual + layer norm | stability glue between sublayers |
| context window | max tokens the model can attend over |

### Encoder vs decoder (and why both exist)

| | Encoder (BERT-style) | Decoder (GPT-style) |
|---|---|---|
| sees | full sequence, bidirectional | only previous tokens (causal mask) |
| trained for | masked-token prediction | **next-token prediction** |
| good at | understanding: classify, embed, rerank | generating: chat, code, summaries |
| program use | embeddings, rerankers (Weeks 4–5) | everything you chat with |

LLMs are **decoder-only transformers**: token in → distribution over the next token → sample → append → repeat. That's autoregressive generation (file 07).

## 4. Pre-trained vs instruction-tuned — the difference you'll feel

| | **Base model** | **Instruct model** |
|---|---|---|
| training | next-token prediction on trillions of tokens of web text | base + **SFT** on (instruction → good answer) pairs |
| behavior | *continues* text like an autocomplete | *obeys* instructions, answers questions |
| prompt `"What is RAG?"` | may continue with more questions, or a FAQ fragment | explains RAG |
| when to use | research, further training, style imitation | all application work |

The post-training recipe (expanded in file 07):

1. **Pre-training** — learn language & world knowledge (expensive, done by labs)
2. **Supervised fine-tuning (SFT)** — learn the *assistant format*
3. **Preference tuning (RLHF / DPO)** — learn which of two answers humans prefer: helpful, harmless, honest

### Hands-on: feel the difference on your laptop

```powershell
pip install transformers torch --index-url https://pypi.org/simple
```

```python
from transformers import pipeline

base = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B")
instruct = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")

prompt = "What is RAG in AI?"
print(base(prompt, max_new_tokens=80)[0]["generated_text"])
print(instruct(prompt, max_new_tokens=80)[0]["generated_text"])
```

Same architecture, same size — different post-training, dramatically different usefulness. (`Qwen2.5-0.5B` ≈ 1 GB download; alternatives: `HuggingFaceTB/SmolLM2-360M-Instruct`.)

Note the instruct output may wrap the answer in chat-template markers — a first look at why file 07's APIs exist: to hide this formatting and hand you `message.content`.

### Choosing models (you'll do this every week)

Check in order: **license** → **size vs your hardware** → **benchmark + community usage** → tokenizer/context window. Model cards on the Hub document all of it.

## Exercises

1. Modify the PyTorch demo: widen the hidden layer (32 → 128). Does it converge faster? Add noise to `y`. What happens?
2. Print `instruct.tokenizer.chat_template`-rendered prompt for a system+user conversation. Match each marker to its role.
3. Ask base and instruct models the *same* question 3× each (deterministic settings). Describe the behavioral difference in one paragraph.
4. Attention by hand: for the sentence `"The animal didn't cross the street because it was too tired"`, write which words "it" should attend to — and what changes with "wide" instead of "tired".
5. On the Hub, find the smallest instruct model with an Apache-2.0 license and 32k+ context. Record size, license, context, and why you picked it.

## Pitfalls

- **Thinking bigger = always better** — a 0.5 B model with a good prompt often beats a badly prompted 70 B model; the capstone will prove this to you
- **Using base models in apps** — they will ramble; always instruct-tuned unless you know why not
- **Confusing tokenizer's context limit with model's** — check the model card
- **CPU training illusions** — `loss.backward()` on your laptop is for learning; real training is distributed GPU work (Week 16 shows the fine-tuning version)

## Resources

- Karpathy, *Neural Networks: Zero to Hero* (YouTube) — build backprop and GPT from scratch
- 3Blue1Brown, *Neural networks* + *Attention in transformers* series
- Jay Alammar, *The Illustrated Transformer*
- Vaswani et al., *Attention Is All You Need* (skim: architecture figure + abstract)
- Hugging Face NLP Course, ch. 1 & 3
