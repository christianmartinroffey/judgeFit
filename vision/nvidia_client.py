import logging
import os

import requests

from vision.base_vision_client import BaseVisionClient

logger = logging.getLogger(__name__)

_API_BASE = "https://integrate.api.nvidia.com/v1"
_DEFAULT_MODEL = "meta/llama-3.2-11b-vision-instruct"
_TIMEOUT = 60


class NvidiaVisionClient(BaseVisionClient):
    _max_images = 1

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.environ["NVIDIA_API_KEY"]
        self.model = model or os.environ.get("NVIDIA_MODEL", _DEFAULT_MODEL)

    def _chat(self, content: str, images: list[str]) -> str:
        msg_content = [{"type": "text", "text": content}] + [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}
            for img in images
        ]
        resp = requests.post(
            f"{_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": msg_content}],
                "stream": False,
            },
            timeout=_TIMEOUT,
        )
        if not resp.ok:
            logger.error("NVIDIA API error %s: %s", resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
