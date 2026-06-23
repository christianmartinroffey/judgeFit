import base64
import logging
import re
from abc import ABC, abstractmethod

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class BaseVisionClient(ABC):
    # Subclasses set this to cap images per request (e.g. 1 for NVIDIA)
    _max_images: int | None = None

    @abstractmethod
    def _chat(self, content: str, images: list[str]) -> str: ...

    def _encode(self, frame: np.ndarray) -> str:
        _, buf = cv2.imencode(".jpg", frame)
        return base64.b64encode(buf).decode("utf-8")

    def query(self, frame: np.ndarray, prompt: str) -> str:
        return self._chat(prompt, [self._encode(frame)])

    def ask_fraction(self, frame: np.ndarray, prompts: list[str]) -> float | None:
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
        n = len(jpeg_frames)
        if self._max_images == 1:
            indices = [n // 2]
        else:
            indices = sorted({0, n // 2, n - 1}) if n >= 3 else list(range(n))

        encoded = [base64.b64encode(jpeg_frames[i]).decode("utf-8") for i in indices]

        prefix = (
            f"I am showing you {len(encoded)} frames from the same video clip. "
            if len(encoded) > 1 else ""
        )
        full_prompt = f"{prefix}{prompt} Answer YES or NO at the very start of your response."

        try:
            response = self._chat(full_prompt, encoded)
            logger.info("ask_yes_no response: %s", response)
            return response.strip().upper().startswith("YES"), response
        except Exception as exc:
            logger.warning("ask_yes_no failed: %s", exc)
            return False, ""
