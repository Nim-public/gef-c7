# The Gradio Model — Interface, Blocks, Events, Queue, State

**What you'll learn:** how Gradio *actually executes* your function — the
event loop, the queue, and state — so your multimodal app does not deadlock
on a GPU or leak model copies per request.

## 1. Interface vs Blocks: when each

| | `gr.Interface` | `gr.Blocks` |
|---|---|---|
| Layout | single fn → single UI | arbitrary graphs |
| State | none built-in | `gr.State`, session-scoped |
| Multi-step apps | awkward | natural |
| Use for | quick demos | every capstone app |

```python
import gradio as gr

def caption_image(img) -> str:
    return blip_caption(img)          # any callable (Path, np.array, PIL)

demo = gr.Interface(caption_image, gr.Image(type="pil"), gr.Textbox(),
                    title="Captioner", allow_flagging="never")
```

## 2. The execution model: events and the queue

Every `.click()`/`.change()` schedules your function on a **queue** —
without `queue()` the app crashes under concurrency (Gradio serializes
some things, not model inference):

```python
with gr.Blocks() as demo:
    img = gr.Image(type="pil")
    out = gr.Textbox()
    btn = gr.Button("Caption")
    btn.click(caption_image, img, out)

demo.queue(max_size=20)        # ← required under any load
demo.launch()                  # binds 127.0.0.1:7860
```

Three execution facts that shape app design:

1. **Handlers are sync by default** — one request blocks the worker; GPU
   apps need `queue()` and (optionally) `concurrency_limit`.
2. **Progress** comes from `gr.Progress()` — for a 30-step diffusion call,
   streaming progress is the difference between "hung" and "working".
3. **Every event = one function call** — state must flow through
   inputs/outputs or `gr.State`, never module globals (breaks under
   multiple workers).

## 3. State: session-scoped, not global

```python
with gr.Blocks() as demo:
    history = gr.State([])                     # per-browser-session

    def add(img, hist):
        hist = hist + [blip_caption(img)]      # return NEW list — don't mutate
        return hist, "\n".join(hist)

    btn.click(add, [img, history], [history, out])
```

The mutation trap: returning the *same list object* means Gradio's diffing
sees no change; always build new containers. For the Week-07 explorer and
this week's apps, the pattern is identical — state in, new state out.

## 4. Streaming progress on heavy calls

```python
def generate(prompt, progress=gr.Progress()):
    latents = None
    for i, (step_lat, _) in enumerate(pipe(prompt, num_inference_steps=30,
                                           generator=g)):
        progress((i + 1) / 30, desc="denoising")
        latents = step_lat
    return pipe.vae.decode(latents / vae_scale).sample
```

(Exact generator-callback APIs vary by diffusers version — check the
`StableDiffusionPipeline.__call__` signature for `callback_on_step_end`;
the pattern above is the conceptual shape.)

## Exercises

1. Convert the Week-07 explorer to `Blocks` with session state holding the
   last 5 viewed units; verify two browser tabs have independent state.
2. Add `gr.Progress` to a 20-step generation; measure perceived latency
   (time to first progress update) — the number users judge you by.
3. Break it on purpose: launch without `queue()`, fire 10 concurrent
   requests with `curl`, record the failure mode; then re-enable and
   compare.

## Pitfalls

- Globals for models are fine; globals for *user state* are not — models once at import, state via `gr.State`.
- `launch(share=True)` on a work machine — a public URL to your corpus; treat as deployment (file 04).
- Heavy work in `__main__` before `launch()` delays app boot; lazy-load on first request if boot time matters.

## Resources

- Gradio docs: Blocks, Events, Queue, State guides.
- Your Week-07 explorer — the code you are upgrading.
