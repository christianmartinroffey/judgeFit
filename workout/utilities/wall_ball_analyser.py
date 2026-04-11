"""
WallBallAnalyser: Coordinates pose detection, ball detection, and target
detection specifically for wall ball shot analysis.

Produces the same output dict shape as WorkoutAnalyser.analyse() so it
is a drop-in replacement for the Celery task.
"""
import logging
import os

import cv2

import workout.utilities.PoseModule as pm
from workout.utilities.movement_counters import WallBallCounter
from workout.utilities.object_detector import GymObjectDetector
from workout.utilities.target_detector import TargetDetector
from workout.utilities.utils import download_youtube_video, load_movement_criteria

logger = logging.getLogger(__name__)


class WallBallAnalyser:
    """
    Analyse a wall ball shot video.

    Pipeline per frame:
      1. Pose detection (every frame) — provides squat angle + landmark data.
      2. Target calibration (first ``calibration_frames`` frames) — auto-detects
         the target Y coordinate once; stored for the full video.
      3. Ball detection (every ``detect_every_n_frames`` frames, with CSRT
         tracker between detections).
      4. WallBallCounter.process() — state machine that combines squat + ball
         trajectory signals to count valid/invalid reps.

    Args:
        video_path:             Local path to the video file.
        expected_reps:          How many reps the athlete should perform (or None).
        criteria:               Full movement_analysis_criteria dict.
        target_y_px:            Manual target Y override (skips auto-detection).
        detect_every_n_frames:  YOLO runs every N frames; CSRT bridges the rest.
        calibration_frames:     Frames dedicated to target auto-detection.
    """

    def __init__(
        self,
        video_path: str,
        expected_reps: int | None,
        criteria: dict,
        target_y_px: int | None = None,
        detect_every_n_frames: int = 3,
        calibration_frames: int = 30,
    ):
        self.video = cv2.VideoCapture(video_path)
        self.expected_reps = expected_reps
        self.criteria = criteria
        self.calibration_frames = calibration_frames

        # Perception modules
        self.pose_detector = pm.PoseDetector()
        self.object_detector = GymObjectDetector(
            detect_every_n_frames=detect_every_n_frames,
        )
        self.target_detector = TargetDetector(
            calibration_frames=calibration_frames,
            manual_target_y=target_y_px,
        )

        # Counter
        wall_ball_criteria = criteria.get('wall_ball', {})
        logging.info(wall_ball_criteria)
        self.counter = WallBallCounter(wall_ball_criteria)
        if target_y_px is not None:
            self.counter.set_target_y(target_y_px)

        self._frame_idx: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyse(self) -> dict:
        """
        Run full video analysis.

        Returns:
            Dict compatible with WorkoutAnalyser.analyse():
                total_reps, no_reps, is_valid, is_scaled,
                breakdown, rounds_completed, target_y_px.
        """
        if not self.video.isOpened():
            raise RuntimeError("Could not open video for wall ball analysis")

        has_frames = False
        while True:
            success, img = self.video.read()
            if not success or img is None:
                break
            has_frames = True
            self._process_frame(img)
            self._frame_idx += 1

        self.video.release()

        stats = self.counter.get_stats()
        total_reps = stats['count']
        total_no_reps = stats['no_rep']

        is_valid = has_frames
        if self.expected_reps is not None:
            is_valid = has_frames and total_reps >= self.expected_reps

        breakdown = [{
            'round': 1,
            'sequence': 1,
            'movement': 'wall_ball',
            'reps': total_reps,
            'no_reps': total_no_reps,
            'expected_reps': self.expected_reps,
            'advance_reason': 'video_end',
        }]

        return {
            'total_reps': total_reps,
            'no_reps': total_no_reps,
            'is_valid': is_valid,
            'is_scaled': False,
            'breakdown': breakdown,
            'rounds_completed': 1 if (is_valid and total_reps > 0) else 0,
            'target_y_px': self.target_detector.target_y_px,
        }

    # ------------------------------------------------------------------
    # Internal frame processing
    # ------------------------------------------------------------------

    def _process_frame(self, img) -> None:
        # 1. Pose detection
        img = self.pose_detector.getPose(img, draw=False)
        lmList = self.pose_detector.getPosition(img, draw=False)

        # 2. Target calibration — runs for the first N frames.
        if not self.target_detector.is_calibrated:
            athlete_wrist_y = None
            if lmList and len(lmList) > 16:
                athlete_wrist_y = lmList[15][2]  # left wrist Y
            self.target_detector.update(img, self._frame_idx, athlete_wrist_y)
            if self.target_detector.is_calibrated and self.target_detector.target_y_px:
                self.counter.set_target_y(self.target_detector.target_y_px)
                logger.info(
                    "Target set at y=%d px after %d frames",
                    self.target_detector.target_y_px,
                    self._frame_idx,
                )

        # 3. Ball detection — build athlete torso bbox from landmarks to filter FPs.
        athlete_torso_bbox = _torso_bbox(lmList) if lmList else None
        detection = self.object_detector.detect(img, self._frame_idx, athlete_torso_bbox)
        self.counter.update_ball_position(detection.get('ball'))

        # 4. Squat angle + counter
        if not lmList:
            return

        try:
            hip, knee, ankle = self.pose_detector.getLandmarkIndices(lmList, is_squat=True)
            angle = self.pose_detector.getAngle(None, hip, knee, ankle)
        except Exception:
            return

        wall_ball_criteria = self.criteria.get('wall_ball', {})
        direction = self.pose_detector.checkDirectionFromAngle(
            angle,
            wall_ball_criteria.get('descending_threshold', 110),
            wall_ball_criteria.get('ascending_threshold', 110),
            self.counter.previous_angle,
            downward_movement=True,
        )

        self.counter.process(angle, lmList, self.pose_detector, direction)

        # 5. Dynamic target recalibration from observed ball peaks.
        # After 3 throw peaks have been recorded, use their median as the target.
        # This corrects a miscalibrated initial target (e.g. rig bar instead of disc).
        self._maybe_recalibrate_target()

    def _maybe_recalibrate_target(self) -> None:
        """
        After 3+ observed throw peaks, recalibrate target_y_px to the median
        peak Y.  Only fires once, and only when the observed peak differs from
        the current target by more than 20px.
        """
        samples = self.counter._peak_samples
        if len(samples) < 3:
            return
        if getattr(self, '_target_recalibrated', False):
            return

        import statistics
        observed_target = int(statistics.median(samples))
        current_target = self.counter.target_y_px

        if current_target is None or abs(observed_target - current_target) > 20:
            logger.info(
                "Recalibrating target from ball peaks: y=%s → y=%d (samples=%s)",
                current_target, observed_target, samples[-5:],
            )
            self.target_detector.target_y_px = observed_target
            self.counter.set_target_y(observed_target)

        self._target_recalibrated = True


# ------------------------------------------------------------------
# Convenience entry point
# ------------------------------------------------------------------

def analyse_wall_ball_video(
    video_url: str,
    expected_reps: int | None = None,
    target_y_px: int | None = None,
) -> dict:
    """
    Download/locate a video and run wall ball analysis.

    Args:
        video_url:      YouTube URL or local file path.
        expected_reps:  Target rep count for validity check.
        target_y_px:    Optional manual target Y coordinate (skips auto-detect).

    Returns:
        Analysis result dict (same shape as WorkoutAnalyser.analyse()).
    """
    criteria = load_movement_criteria()

    is_local = os.path.exists(video_url)
    if is_local:
        video_path = video_url
        cleanup = False
    else:
        video_path = download_youtube_video(video_url)
        cleanup = True

    try:
        analyser = WallBallAnalyser(
            video_path,
            expected_reps=expected_reps,
            criteria=criteria,
            target_y_px=target_y_px,
        )
        return analyser.analyse()
    finally:
        if cleanup and os.path.exists(video_path):
            os.unlink(video_path)


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

def _torso_bbox(lmList: list) -> tuple | None:
    """
    Build a rough torso bounding box from pose landmarks to use as a
    false-positive filter for ball detection.

    Returns (x1, y1, x2, y2) or None.
    """
    try:
        # Shoulders (11, 12) and hips (23, 24)
        xs = [lmList[i][1] for i in (11, 12, 23, 24)]
        ys = [lmList[i][2] for i in (11, 12, 23, 24)]
        padding = 30
        return (
            min(xs) - padding,
            min(ys) - padding,
            max(xs) + padding,
            max(ys) + padding,
        )
    except (IndexError, TypeError):
        return None
