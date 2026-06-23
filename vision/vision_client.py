import logging
import os

from vision.llava_client import LLaVAClient
from vision.nvidia_client import NvidiaVisionClient

logger = logging.getLogger(__name__)


class VisionClient:
    """
    Primary: NvidiaVisionClient. Falls back to LLaVAClient on any exception.
    Set NVIDIA_API_KEY to enable NVIDIA; omit to use Ollama only.
    """

    def __init__(self):
        self._nvidia: NvidiaVisionClient | None = None
        self._ollama: LLaVAClient | None = None

        if os.environ.get("NVIDIA_API_KEY"):
            try:
                self._nvidia = NvidiaVisionClient()
                logger.info("VisionClient: NVIDIA primary (%s)", self._nvidia.model)
            except Exception as exc:
                logger.warning("VisionClient: NVIDIA init failed, Ollama only: %s", exc)

        self._ollama = LLaVAClient()
        if self._nvidia is None:
            logger.info("VisionClient: Ollama only (%s)", self._ollama.model)

    def _with_fallback(self, method: str, *args, **kwargs):
        if self._nvidia is not None:
            try:
                return getattr(self._nvidia, method)(*args, **kwargs)
            except Exception as exc:
                logger.warning("NVIDIA %s failed, falling back to Ollama: %s", method, exc)
        return getattr(self._ollama, method)(*args, **kwargs)

    def query(self, frame, prompt: str) -> str:
        return self._with_fallback("query", frame, prompt)

    def ask_fraction(self, frame, prompts: list[str]) -> float | None:
        return self._with_fallback("ask_fraction", frame, prompts)

    def ask_yes_no(self, jpeg_frames: list[bytes], prompt: str) -> tuple[bool, str]:
        return self._with_fallback("ask_yes_no", jpeg_frames, prompt)
