# vision

Vision inference clients used for wall ball video analysis.

## Overview

The vision layer handles two tasks during wall ball analysis:

- **Target detection** — locates the wall ball target at the start of a video, returning its vertical position as a fraction (0.0 = top, 1.0 = bottom) of the frame height
- **Ball-dropped check** — asks whether the ball was dropped during a rep, used to distinguish a low throw from a drop

Everything else (squat depth, ball trajectory, rep counting) is handled by pose landmarks and YOLO object detection — the vision model is only called a handful of times per video, not per frame.

## Structure

```
base_vision_client.py  — abstract base class with shared query logic
llava_client.py        — Ollama backend (local, uses minicpm-v by default)
nvidia_client.py       — NVIDIA cloud API backend (integrate.api.nvidia.com)
vision_client.py       — primary/fallback wrapper (NVIDIA first, Ollama fallback)
vision_utils.py        — read_clock() helper for reading competition timers
```

## Adding a new backend

Subclass `BaseVisionClient` and implement `_chat`:

```python
from vision.base_vision_client import BaseVisionClient

class MyClient(BaseVisionClient):
    _max_images = 1  # set if the backend limits images per request

    def _chat(self, content: str, images: list[str]) -> str:
        # images is a list of base64-encoded JPEG strings
        ...
```

Then wire it into `VisionClient` in `vision_client.py`.

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `NVIDIA_API_KEY` | — | Enables NVIDIA backend; omit to use Ollama only |
| `NVIDIA_MODEL` | `meta/llama-3.2-11b-vision-instruct` | NVIDIA model ID |
| `OLLAMA_HOST` | `192.168.1.64:11434` | Ollama server address |
| `OLLAMA_MODEL` | `minicpm-v` | Ollama model name |

## Backend behaviour

**NVIDIA** (`NvidiaVisionClient`)
- Cloud API, requires `NVIDIA_API_KEY`
- Limited to 1 image per request — `ask_yes_no` uses the middle frame of a clip
- Available vision models on `integrate.api.nvidia.com`: `meta/llama-3.2-11b-vision-instruct`, `meta/llama-3.2-90b-vision-instruct`, `nvidia/nemotron-nano-12b-v2-vl`, `microsoft/phi-4-multimodal-instruct`

**Ollama** (`LLaVAClient`)
- Local inference, no API key needed
- Supports multiple images per request — `ask_yes_no` sends start, middle, and end frames
- Runs on a separate machine; configure `OLLAMA_HOST` to point at it

**VisionClient** (wrapper)
- NVIDIA is primary when `NVIDIA_API_KEY` is set; Ollama is the fallback
- If NVIDIA fails on a call, that call automatically retries on Ollama and logs a warning
- If `NVIDIA_API_KEY` is not set, Ollama is used exclusively
