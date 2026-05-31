import logging
import re

import numpy as np

from workout.utilities.llava_client import LLaVAClient

logger = logging.getLogger(__name__)

_CLOCK_PROMPT = (
    "Look at this image carefully, including the floor area. "
    "There may be a physical competition timer — a black rectangular device on the floor "
    "displaying time in MM:SS format (e.g. 00:00, 00:01, 01:30). "
    "If you can see a timer showing MM:SS time anywhere in the image, "
    "reply with exactly: TIMER MM:SS where MM:SS is the exact time shown. "
    "If no MM:SS timer is visible, reply with exactly: NO TIMER"
)


def read_clock(frame: np.ndarray, client: LLaVAClient) -> str | None:
    """
    Read a competition clock from a video frame.

    Returns a MM:SS string if a timer is visible, or None.
    """
    try:
        response = client.query(frame, _CLOCK_PROMPT)
        logger.info("read_clock response: %s", response)
        if "no timer" in response.lower():
            return None
        match = re.search(r'\b(\d{2}:\d{2})\b', response)
        return match.group(1) if match else None
    except Exception as exc:
        logger.warning("read_clock failed: %s", exc)
        return None
