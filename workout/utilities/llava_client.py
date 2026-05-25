import base64
import logging
import os
import re

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "192.168.1.47:11434"
_MODEL = "llava"
_TIMEOUT = 30


class LLaVATargetDetectionError(Exception):
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

    def locate_target_crop(self, frame: np.ndarray) -> tuple[int, int, int, int] | None:
        """
        Ask LLaVA where the wall ball target is in the frame.

        Returns a (x1, y1, x2, y2) strip bounding box for CV to refine,
        or None if no target is found.
        """
        h, w = frame.shape[:2]
        prompt = (
            "Look at this gym image. Is there a wall ball target visible? "
            "A wall ball target is a tape line, painted circle, or marker on the wall, "
            "usually in the upper half of the frame. "
            "If yes, reply with exactly: TARGET <fraction> "
            "where fraction is its vertical position as a decimal from 0.0 (top) to 1.0 (bottom). "
            "If no target is visible, reply with exactly: NO TARGET"
        )
        try:
            response = self._chat(prompt, [self._encode(frame)])
            logger.debug("LLaVA target locate response: %s", response)

            if "no target" in response.lower():
                return None

            matches = re.findall(r"\b0?\.\d+\b", response)
            if not matches:
                return None

            fraction = float(matches[0])
            if not (0.05 < fraction < 0.95):
                logger.warning("LLaVA target fraction out of range: %s", fraction)
                return None

            center_y = int(fraction * h)
            strip = max(int(h * 0.10), 30)
            y1 = max(0, center_y - strip)
            y2 = min(h, center_y + strip)
            logger.info("LLaVA target crop: y=[%d, %d] (fraction=%.2f)", y1, y2, fraction)
            return (0, y1, w, y2)

        except Exception as exc:
            logger.warning("LLaVA target location request failed: %s", exc)
            return None

    def check_equipment(self, frames: list[np.ndarray], prompt: str) -> tuple[bool, str]:
        """
        Check whether equipment is present in the given frames.

        Uses the middle frame. Returns (present, raw_llava_response).
        Ambiguous or error responses are treated as not present (strict judging).
        """
        frame = frames[len(frames) // 2]
        full_prompt = f"{prompt} Answer YES or NO at the very start of your response."
        try:
            response = self._chat(full_prompt, [self._encode(frame)])
            logger.debug("LLaVA equipment check response: %s", response)
            present = response.strip().upper().startswith("YES")
            return present, response
        except Exception as exc:
            logger.warning("LLaVA equipment check failed: %s", exc)
            return False, f"error: {exc}"
