"""
TargetDetector: Locates the wall ball target in a video frame.

The target can be:
  - A horizontal tape line on a wall
  - A circular target on a rig or wall
  - A colored marker

Detection runs once during a short calibration phase (first N frames) while
the athlete is standing still.  The detected target Y-coordinate is stored and
reused for the full video.  If auto-detection fails, a ``manual_target_y``
value can be provided as an override.
"""
import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Approx. fraction of frame height above which the target is expected to be.
# For a standard 10ft wall ball target the ball must reach ~9ft; assuming a
# typical camera angle the target line appears in the upper ~40% of the frame.
_TARGET_SEARCH_REGION_FRACTION = 0.60

# HSV colour ranges for common tape/target colours.
# Each entry is ((h_lo, s_lo, v_lo), (h_hi, s_hi, v_hi)).
_COLOUR_RANGES = [
    ((35, 80, 80), (85, 255, 255)),    # green
    ((20, 100, 100), (35, 255, 255)),  # yellow
    ((0, 100, 80), (10, 255, 255)),    # red (low hue)
    ((170, 100, 80), (180, 255, 255)), # red (high hue)
    ((100, 100, 60), (130, 255, 255)), # blue
]


class TargetDetector:
    """
    Detects the wall ball target height (Y-pixel coordinate) from video frames.

    Usage::

        td = TargetDetector(calibration_frames=30)
        for frame_idx, frame in enumerate(frames):
            if not td.is_calibrated:
                td.update(frame, frame_idx, athlete_wrist_y=lmList[15][2])
            if td.is_calibrated:
                hit = td.is_target_reached(ball_centroid_y)

    Args:
        calibration_frames:  Number of frames to attempt detection on.
        manual_target_y:     If provided, skip auto-detection and use this value.
        min_line_length_frac: Minimum line length as a fraction of frame width
                              for the Hough line detector.
    """

    def __init__(
        self,
        calibration_frames: int = 30,
        manual_target_y: int | None = None,
        min_line_length_frac: float = 0.15,
    ):
        self.calibration_frames = calibration_frames
        self.min_line_length_frac = min_line_length_frac

        self.target_y_px: int | None = manual_target_y
        self.is_calibrated: bool = manual_target_y is not None
        self._frames_checked: int = 0
        self._candidate_ys: list[int] = []

        # Set when a circle is the detection source — (cx, cy, radius) in full-frame coords.
        self.target_circle: tuple | None = None
        # Last frame's raw circle detections for debug overlay — list of (cx, cy, r).
        self._debug_circles: list[tuple] = []
        # Last frame's search region top-left offset (for mapping debug_circles to full frame).
        self._search_region_h: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(
        self,
        frame: np.ndarray,
        frame_idx: int,
        athlete_wrist_y: int | None = None,
    ) -> bool:
        """
        Feed a frame during the calibration phase.

        Args:
            frame:            BGR image.
            frame_idx:        Current frame index (used for logging only).
            athlete_wrist_y:  Y-pixel of the athlete's wrist when standing.
                              Used to sanity-check that the detected target is
                              actually above the athlete's reach.

        Returns:
            True once the target has been found and ``is_calibrated`` is set.
        """
        if self.is_calibrated:
            return True

        self._frames_checked += 1
        h, w = frame.shape[:2]
        self._search_region_h = int(h * _TARGET_SEARCH_REGION_FRACTION)
        search_region = frame[:self._search_region_h, :]
        self._debug_circles = []  # reset each frame

        y = (
            self._detect_circle_target(search_region)
            or self._detect_horizontal_line(search_region, w)
            or self._detect_colour_target(search_region)
        )

        if y is not None:
            if athlete_wrist_y is None or y < athlete_wrist_y:
                self._candidate_ys.append(y)
                logger.debug(
                    "Target candidate at y=%d (frame %d)", y, frame_idx
                )

        # Commit once we have ≥5 consistent candidates or exhausted calibration frames.
        # Requiring 5 reduces false positives from background edges in the first few frames.
        if len(self._candidate_ys) >= 5 or self._frames_checked >= self.calibration_frames:
            self._commit()

        return self.is_calibrated

    def is_target_reached(self, ball_centroid_y: int) -> bool:
        """
        Return True if the ball centroid is at or above the target line.

        Lower Y in pixel coordinates = higher on screen.
        """
        if self.target_y_px is None:
            return False
        return ball_centroid_y <= self.target_y_px

    def draw_target(self, frame: np.ndarray) -> np.ndarray:
        """Draw the detected target line on a frame (for debugging)."""
        if self.target_y_px is None:
            return frame
        out = frame.copy()
        cv2.line(out, (0, self.target_y_px), (frame.shape[1], self.target_y_px), (0, 255, 0), 2)
        cv2.putText(
            out, f"Target y={self.target_y_px}",
            (10, max(self.target_y_px - 10, 10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
        )
        return out

    def draw_debug(self, frame: np.ndarray) -> None:
        """
        Draw calibration debug info directly onto ``frame`` (in-place).

        During calibration:
          - Yellow dashed line marks the bottom of the search region.
          - All detected circle candidates are drawn in blue.
          - The chosen (largest) circle is drawn in magenta.

        After calibration:
          - The confirmed target circle (if from circle detection) is drawn
            in green with its centre marked.
        """
        h, w = frame.shape[:2]

        if not self.is_calibrated:
            # Show search region boundary
            sr_y = self._search_region_h or int(h * _TARGET_SEARCH_REGION_FRACTION)
            for x in range(0, w, 20):
                cv2.line(frame, (x, sr_y), (min(x + 10, w), sr_y), (0, 220, 220), 1)
            cv2.putText(frame, 'Search region', (10, sr_y - 6),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 220, 220), 1)

            # All circle candidates this frame (blue)
            for cx, cy, r in self._debug_circles:
                cv2.circle(frame, (cx, cy), r, (255, 100, 0), 1)
                cv2.drawMarker(frame, (cx, cy), (255, 100, 0),
                               cv2.MARKER_CROSS, 10, 1)

            # Highlight the chosen (largest) circle in magenta
            if self._debug_circles:
                chosen = max(self._debug_circles, key=lambda c: c[2])
                cx, cy, r = chosen
                cv2.circle(frame, (cx, cy), r, (255, 0, 255), 2)
                cv2.putText(frame, f'best circle r={r}',
                            (cx + r + 4, cy),
                            cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 2)

        else:
            # After calibration — draw the confirmed target circle if we have it
            if self.target_circle:
                cx, cy, r = self.target_circle
                cv2.circle(frame, (cx, cy), r, (0, 255, 0), 3)
                cv2.drawMarker(frame, (cx, cy), (0, 255, 0),
                               cv2.MARKER_CROSS, 16, 2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _commit(self) -> None:
        """Pick the median candidate and mark calibration as complete."""
        if self._candidate_ys:
            self.target_y_px = int(np.median(self._candidate_ys))
            self.is_calibrated = True
            logger.info("Target calibrated at y=%d px", self.target_y_px)
        else:
            logger.warning(
                "Target detection failed after %d frames — use manual_target_y as override.",
                self._frames_checked,
            )
            self.is_calibrated = True   # Stop retrying even if we failed

    def _detect_horizontal_line(self, region: np.ndarray, frame_width: int) -> int | None:
        """
        Use Canny edge detection + HoughLinesP to find a prominent horizontal
        tape line.  Returns the Y-coordinate of the best candidate line within
        ``region``.
        """
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        min_length = int(frame_width * self.min_line_length_frac)
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=80,
            minLineLength=min_length,
            maxLineGap=20,
        )
        if lines is None:
            return None

        horizontal = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) <= 5:  # near-horizontal only
                horizontal.append((y1 + y2) // 2)

        if not horizontal:
            return None

        # Pick the most frequently occurring Y band (cluster with tolerance ±5 px).
        horizontal.sort()
        best_y, best_count = horizontal[0], 1
        cur_y, cur_count = horizontal[0], 1
        for y in horizontal[1:]:
            if y - cur_y <= 5:
                cur_count += 1
            else:
                if cur_count > best_count:
                    best_y, best_count = cur_y, cur_count
                cur_y, cur_count = y, 1
        return best_y

    def _detect_circle_target(self, region: np.ndarray) -> int | None:
        """
        Use HoughCircles to detect a circular rig/wall target.

        Returns the Y coordinate of the centre of the best circle found,
        in region-local coordinates.  All candidates are stored in
        ``self._debug_circles`` (full-frame coords) for visualisation.
        """
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 2)
        h, w = region.shape[:2]

        # Try progressively looser thresholds so we don't miss a real target.
        circles = None
        for param2 in (35, 25, 18):
            circles = cv2.HoughCircles(
                blur,
                cv2.HOUGH_GRADIENT,
                dp=1.2,
                minDist=40,
                param1=80,
                param2=param2,
                minRadius=8,
                maxRadius=w // 3,
            )
            if circles is not None:
                break

        if circles is None:
            return None

        circles = np.uint16(np.around(circles))
        # Store all for debug — region starts at y=0, so region-local Y == full-frame Y.
        self._debug_circles = [
            (int(c[0]), int(c[1]), int(c[2]))
            for c in circles[0]
        ]

        # Pick the largest circle — most likely to be the target disc.
        largest = max(circles[0], key=lambda c: c[2])
        cx, cy, r = int(largest[0]), int(largest[1]), int(largest[2])

        # Remember the winning circle for drawing.
        self.target_circle = (cx, cy, r)

        logger.debug(
            "Circle target candidate: centre=(%d, %d) r=%d (region-local)",
            cx, cy, r,
        )
        return cy  # region-local Y; caller adds search_region offset if needed

    def _detect_colour_target(self, region: np.ndarray) -> int | None:
        """
        Segment common tape colours (green, yellow, red, blue) and find the
        topmost horizontal contour.
        """
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        for lo, hi in _COLOUR_RANGES:
            mask = cv2.inRange(hsv, np.array(lo), np.array(hi))
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        closed = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        h, w = region.shape[:2]
        min_area = w * 3  # at least 3 pixels tall × full width
        candidates = []
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            if cw >= w * 0.10 and cv2.contourArea(cnt) >= min_area:
                candidates.append(y + ch // 2)

        return min(candidates) if candidates else None
