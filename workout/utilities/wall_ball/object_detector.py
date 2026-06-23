"""
GymObjectDetector: YOLOv8-based gym equipment detection.

Uses YOLOv8n with COCO pre-trained weights.  COCO class 32 ("sports ball")
covers wall balls / medicine balls well enough for a first implementation.
A CSRT tracker bridges detection gaps between YOLO runs to handle brief
occlusions (e.g. when the athlete catches the ball).

Future: swap in fine-tuned weights for barbells, dumbbells, kettlebells.
"""
import logging
import os

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# COCO class index for sports ball (wall ball / medicine ball proxy).
_SPORTS_BALL_CLASS = 32

# Default path to pre-downloaded weights.
_DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', '..', 'static', 'models', 'yolov8n.pt',
)


class GymObjectDetector:
    """
    Detects gym equipment in video frames using YOLOv8.

    Usage (per-frame, inside a video loop)::

        detector = GymObjectDetector()
        for frame_idx, frame in enumerate(frames):
            result = detector.detect(frame, frame_idx, athlete_torso_bbox=...)
            if result['ball']:
                cx, cy = result['ball']['centroid']

    Args:
        model_path:            Path to YOLOv8 .pt weights file.
        confidence_threshold:  Minimum YOLO confidence to accept a detection.
        detect_every_n_frames: Run YOLO only on every Nth frame; use CSRT tracker
                               on the frames in between.
        device:                Torch device string ('cpu', 'cuda', 'mps').
    """

    def __init__(
        self,
        model_path: str = _DEFAULT_MODEL_PATH,
        confidence_threshold: float = 0.35,
        detect_every_n_frames: int = 3,
        device: str = 'cpu',
    ):
        self.confidence_threshold = confidence_threshold
        self.detect_every_n_frames = detect_every_n_frames
        self.device = device

        self._model = None
        self._model_path = os.path.abspath(model_path)

        # CSRT tracker state
        self._tracker = None
        self._tracker_active = False
        self._last_bbox = None   # (x, y, w, h) in OpenCV tracker format

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(
        self,
        frame: np.ndarray,
        frame_idx: int,
        athlete_torso_bbox: tuple | None = None,
    ) -> dict:
        """
        Run detection on a single frame.

        Args:
            frame:              BGR image as NumPy array.
            frame_idx:          Current frame number (used for N-frame scheduling).
            athlete_torso_bbox: Optional (x1, y1, x2, y2) bounding box of the
                                athlete's torso.  Ball detections whose centroid
                                falls inside this box are discarded as false positives
                                (e.g. head mistaken for ball).

        Returns:
            dict with keys:
                'ball': {'centroid': (cx, cy), 'bbox': (x1,y1,x2,y2), 'confidence': float}
                        or None if no ball detected.
                'frame_idx': int
        """
        ball = None

        if frame_idx % self.detect_every_n_frames == 0:
            ball = self._run_yolo(frame, athlete_torso_bbox)
            if ball:
                x1, y1, x2, y2 = ball['bbox']
                w, h = x2 - x1, y2 - y1
                self._last_bbox = (x1, y1, w, h)
                self._init_tracker(frame, self._last_bbox)
            else:
                self._tracker_active = False
        else:
            ball = self._update_tracker(frame)

        return {'ball': ball, 'frame_idx': frame_idx}

    def reset_tracker(self) -> None:
        """Reset the CSRT tracker (call between reps or at start of new set)."""
        self._tracker = None
        self._tracker_active = False
        self._last_bbox = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_model(self):
        """Lazy-load the YOLO model on first use."""
        if self._model is not None:
            return
        try:
            from ultralytics import YOLO  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "ultralytics is required for object detection. "
                "Install it with: pip install ultralytics"
            ) from exc

        logger.info("Loading YOLOv8 model from %s", self._model_path)
        self._model = YOLO(self._model_path)
        self._model.to(self.device)
        logger.info("YOLOv8 model loaded on device=%s", self.device)

    def _run_yolo(
        self,
        frame: np.ndarray,
        athlete_torso_bbox: tuple | None,
    ) -> dict | None:
        """Run YOLO inference and return the best sports-ball detection."""
        self._load_model()

        results = self._model(frame, verbose=False, device=self.device)
        if not results:
            return None

        best = None
        best_conf = self.confidence_threshold

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                if cls != _SPORTS_BALL_CLASS or conf < best_conf:
                    continue
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                if athlete_torso_bbox and _inside_bbox((cx, cy), athlete_torso_bbox):
                    continue

                best_conf = conf
                best = {
                    'centroid': (cx, cy),
                    'bbox': (x1, y1, x2, y2),
                    'confidence': conf,
                }

        return best

    def _init_tracker(self, frame: np.ndarray, bbox_xywh: tuple) -> None:
        """Initialise (or re-initialise) the CSRT tracker."""
        try:
            self._tracker = cv2.legacy.TrackerCSRT_create()
        except AttributeError:
            try:
                self._tracker = cv2.TrackerCSRT_create()
            except AttributeError:
                logger.warning("CSRT tracker unavailable; falling back to YOLO-only mode.")
                self._tracker = None
                self._tracker_active = False
                return

        self._tracker.init(frame, bbox_xywh)
        self._tracker_active = True

    def _update_tracker(self, frame: np.ndarray) -> dict | None:
        """Update the CSRT tracker and return ball position if tracking is active."""
        if not self._tracker_active or self._tracker is None:
            return None

        success, bbox = self._tracker.update(frame)
        if not success:
            self._tracker_active = False
            return None

        x, y, w, h = [int(v) for v in bbox]
        cx, cy = x + w // 2, y + h // 2
        x2, y2 = x + w, y + h

        return {
            'centroid': (cx, cy),
            'bbox': (x, y, x2, y2),
            'confidence': None,   # CSRT does not produce confidence scores
        }


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

def _inside_bbox(point: tuple, bbox: tuple) -> bool:
    """Return True if (px, py) falls inside (x1, y1, x2, y2)."""
    px, py = point
    x1, y1, x2, y2 = bbox
    return x1 <= px <= x2 and y1 <= py <= y2
