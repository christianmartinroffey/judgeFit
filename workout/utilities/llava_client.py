import base64
import logging
import os
import re

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "192.168.1.47:11434"
_MODEL = "minicpm-v"
_TIMEOUT = 30


class LLaVATargetDetectionError(Exception):
    pass


class LLaVAClockDetectionError(Exception):
    pass


class LLaVAClient:
    def __init__(self, host: str | None = None):
        raw = (host or os.environ.get("OLLAMA_HOST", _DEFAULT_HOST)).strip()
        raw = raw.replace("http://", "").replace("https://", "")
        self.base_url = f"http://{raw}"
        self.model = _MODEL

    def _encode(self, frame: np.ndarray) -> str:
        _, buf = cv2.imencode(".jpg", frame)
        return base64.b64encode(buf).decode("utf-8")

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

    def query(self, frame: np.ndarray, prompt: str) -> str:
        """Single-frame query — returns raw model response."""
        return self._chat(prompt, [self._encode(frame)])

    def ask_fraction(self, frame: np.ndarray, prompts: list[str]) -> float | None:
        """
        Try each prompt in sequence to locate a vertical position in the frame.

        Returns the first valid fraction (0.0 = top, 1.0 = bottom), or None if
        all prompts fail. Expects responses containing a decimal like 'TARGET 0.42'
        or a plain number; skips responses containing 'no target'.
        """
        encoded = self._encode(frame)
        for i, prompt in enumerate(prompts):
            try:
                response = self._chat(prompt, [encoded])
                logger.info("ask_fraction response (attempt %d): %s", i + 1, response)

                if "no target" in response.lower():
                    continue

                matches = re.findall(r"\b(0?\.\d+|1\.0)\b", response)
                if not matches:
                    continue

                fraction = float(matches[0])
                if not (0.05 < fraction < 0.95):
                    logger.warning("ask_fraction: fraction out of range: %s", fraction)
                    continue

                return fraction

            except Exception as exc:
                logger.warning("ask_fraction failed (attempt %d): %s", i + 1, exc)

        return None

    def ask_yes_no(self, jpeg_frames: list[bytes], prompt: str) -> tuple[bool, str]:
        """
        Ask a YES/NO question across pre-encoded JPEG frames.

        Sends all frames in a single multi-image call.
        Returns (answer_is_yes, raw_response).
        """
        n = len(jpeg_frames)
        indices = sorted({0, n // 2, n - 1}) if n >= 3 else list(range(n))
        encoded = [base64.b64encode(jpeg_frames[i]).decode("utf-8") for i in indices]

        full_prompt = (
            f"I am showing you {len(encoded)} frames from the same video clip. "
            f"{prompt} Answer YES or NO at the very start of your response."
        )
        try:
            response = self._chat(full_prompt, encoded)
            logger.info("ask_yes_no response: %s", response)
            return response.strip().upper().startswith("YES"), response
        except Exception as exc:
            logger.warning("ask_yes_no failed: %s", exc)
            return False, ""
