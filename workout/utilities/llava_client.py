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

    def locate_target_crop(self, frame: np.ndarray) -> tuple[int, int, int, int] | None:
        """
        Ask LLaVA where the wall ball target is in the frame.

        Returns a (x1, y1, x2, y2) strip bounding box for CV to refine,
        or None if no target is found.
        """
        _TARGET_PROMPTS = [
            (
                "Look at this gym image carefully. Find the wall ball target on the wall. "
                "It could be any of these: a coloured circle or dot (red, orange, yellow, blue), "
                "a horizontal tape line, a painted mark, a white spot, a colour boundary or edge "
                "where two different coloured sections of wall meet, a coloured panel or section on the wall, "
                "or any other distinct visual marker on the wall surface. "
                "The target is usually in the upper half of the frame. "
                "Reply with exactly: TARGET <fraction> "
                "where fraction is the vertical position of the target as a decimal from 0.0 (top) to 1.0 (bottom). "
                "If you truly cannot identify any target or wall marker, reply with exactly: NO TARGET"
            ),
            (
                "Look at this gym image. In the upper half of the image, find the most prominent "
                "colour change, boundary, panel edge, or marking on the wall. "
                "Reply with exactly: TARGET <fraction> "
                "where fraction is its vertical position as a decimal from 0.0 (top) to 1.0 (bottom)."
            ),
            (
                "Look at this gym image. The wall ball target is a blue section or coloured area on the wall. "
                "Find the top edge of the blue or coloured section and reply with exactly: TARGET <fraction> "
                "where fraction is its vertical position as a decimal from 0.0 (top) to 1.0 (bottom). "
                "If no coloured section is visible, reply with exactly: NO TARGET"
            ),
        ]

        h, w = frame.shape[:2]
        encoded = self._encode(frame)

        for i, prompt in enumerate(_TARGET_PROMPTS):
            try:
                response = self._chat(prompt, [encoded])
                logger.info("LLaVA target locate response (attempt %d): %s", i + 1, response)

                if "no target" in response.lower():
                    continue

                matches = re.findall(r"\b(0?\.\d+|1\.0)\b", response)
                if not matches:
                    continue

                fraction = float(matches[0])
                if not (0.05 < fraction < 0.95):
                    logger.warning("LLaVA target fraction out of range: %s", fraction)
                    continue

                center_y = int(fraction * h)
                strip = max(int(h * 0.10), 30)
                y1 = max(0, center_y - strip)
                y2 = min(h, center_y + strip)
                logger.info("LLaVA target crop: y=[%d, %d] (fraction=%.2f, attempt=%d)", y1, y2, fraction, i + 1)
                return (0, y1, w, y2)

            except Exception as exc:
                logger.warning("LLaVA target location request failed (attempt %d): %s", i + 1, exc)

        return None

    def read_clock(self, frame: np.ndarray) -> str | None:
        """
        Ask LLaVA to read a competition clock from the frame.

        Returns the time string (e.g. "00:00", "00:01") if a MM:SS clock is
        visible, or None if no clock is found.
        """
        prompt = (
            "Look at this image carefully, including the floor area. "
            "There may be a physical competition timer — a black rectangular device on the floor "
            "displaying time in MM:SS format (e.g. 00:00, 00:01, 01:30). "
            "If you can see a timer showing MM:SS time anywhere in the image, "
            "reply with exactly: TIMER MM:SS where MM:SS is the exact time shown. "
            "If no MM:SS timer is visible, reply with exactly: NO TIMER"
        )
        try:
            response = self._chat(prompt, [self._encode(frame)])
            logger.info("LLaVA clock read response: %s", response)

            if "no timer" in response.lower():
                return None

            match = re.search(r'\b(\d{2}:\d{2})\b', response)
            if match:
                return match.group(1)

            return None
        except Exception as exc:
            logger.warning("LLaVA clock read failed: %s", exc)
            return None

    def check_equipment(self, jpeg_frames: list[bytes], prompt: str) -> tuple[bool, str]:
        """
        Check equipment presence using pre-encoded JPEG frames.

        Sends all frames in a single multi-image call.
        Returns (dropped, raw_response). dropped=True if the model answers YES.
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
            logger.info("LLaVA equipment check response: %s", response)
            return response.strip().upper().startswith("YES"), response
        except Exception as exc:
            logger.warning("LLaVA equipment check failed: %s", exc)
            return False, ""
