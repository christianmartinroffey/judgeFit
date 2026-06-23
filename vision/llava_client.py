import logging
import os

import requests

from vision.base_vision_client import BaseVisionClient

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "192.168.1.64:11434"
_DEFAULT_MODEL = "minicpm-v"
_TIMEOUT = 30


class LLaVATargetDetectionError(Exception):
    pass


class LLaVAClockDetectionError(Exception):
    pass


class LLaVAClient(BaseVisionClient):
    def __init__(self, host: str | None = None, model: str | None = None):
        raw = (host or os.environ.get("OLLAMA_HOST", _DEFAULT_HOST)).strip()
        raw = raw.replace("http://", "").replace("https://", "")
        self.base_url = f"http://{raw}"
        self.model = model or os.environ.get("OLLAMA_MODEL", _DEFAULT_MODEL)

    def _chat(self, content: str, images: list[str]) -> str:
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "stream": False,
                "messages": [{"role": "user", "content": content, "images": images}],
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
