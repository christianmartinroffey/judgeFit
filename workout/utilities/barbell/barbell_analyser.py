"""
BarbellAnalyser: coordinates pose detection, vision model barbell checks, and
rep counting for barbell movements (clean and jerk, snatch, hang variants).

Flow per frame
--------------
1. Pose detection (MediaPipe) — every frame.
2. counter.get_vision_check_needed(lmList) — pose-driven trigger.
3. If triggered AND cooldown elapsed: call vision model to confirm barbell position.
4. counter.update_barbell_confirmed(position) — if vision says YES.
5. counter.process(angle, lmList, detector, direction) — every frame.
"""
import logging

import cv2

import workout.utilities.PoseModule as pm
from vision.vision_client import VisionClient
from workout.utilities.barbell.barbell_counters import CleanAndJerkCounter, SnatchCounter
from workout.utilities.utils import download_youtube_video, load_movement_criteria

logger = logging.getLogger(__name__)

_VISION_PROMPTS = {
    'ground': (
        "Is the barbell in the starting or finishing position on the ground? "
        "In weightlifting the bar always rests on weight plates — the plates sit on the floor "
        "and the bar lies across them. Answer YES if the barbell and its plates are resting on "
        "the floor (whether the bar itself touches the floor or not). "
        "Answer NO only if the athlete is actively holding the bar off the ground."
    ),
    'shoulder': (
        "Is the athlete holding a barbell in a front rack position at their shoulders or chest? "
        "Answer YES if the bar is racked at shoulder/chest height. Answer NO otherwise."
    ),
    'overhead': (
        "Is the barbell overhead with the athlete holding it above their head? "
        "Answer YES if the bar is clearly above the athlete's head. Answer NO otherwise."
    ),
}

_MOVEMENT_COUNTERS = {
    'clean_and_jerk':      (CleanAndJerkCounter, False),
    'hang_clean_and_jerk': (CleanAndJerkCounter, True),
    'snatch':              (SnatchCounter, False),
    'hang_snatch':         (SnatchCounter, True),
}


class BarbellAnalyser:
    """
    Analyse a barbell movement video.

    Args:
        video_path:    Local filesystem path to the video file.
        movement_type: One of 'clean_and_jerk', 'hang_clean_and_jerk',
                       'snatch', 'hang_snatch'.
        expected_reps: Target rep count (or None).
        criteria:      Full movement_analysis_criteria dict.
        vision_cooldown_frames: Minimum frames between vision model calls.
    """

    def __init__(
        self,
        video_path: str,
        movement_type: str,
        expected_reps: int | None,
        criteria: dict,
        vision_cooldown_frames: int = 30,
    ):
        if movement_type not in _MOVEMENT_COUNTERS:
            raise ValueError(f"Unknown movement type: {movement_type!r}. "
                             f"Choose from: {list(_MOVEMENT_COUNTERS)}")

        self.video_path = video_path
        self.movement_type = movement_type
        self.expected_reps = expected_reps
        self._vision_cooldown_frames = vision_cooldown_frames

        counter_cls, hang = _MOVEMENT_COUNTERS[movement_type]
        movement_criteria = criteria.get(movement_type, {})
        self.counter = counter_cls(movement_criteria, hang=hang)

        self.video = cv2.VideoCapture(video_path)
        fps = self.video.get(cv2.CAP_PROP_FPS)
        self.counter.set_fps(fps if fps > 0 else 30.0)

        self.pose_detector = pm.PoseDetector()
        self.vision_client = VisionClient()

        self._last_vision_frame = -vision_cooldown_frames

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyse(self) -> dict:
        """
        Run analysis on the full video.

        Returns the same shape as WallBallAnalyser.analyse():
            total_reps, no_reps, good_reps, is_valid, is_scaled,
            breakdown, rep_log, rounds_completed.
        """
        if not self.video.isOpened():
            raise RuntimeError(f"Could not open video: {self.video_path}")

        frame_idx = 0
        while True:
            success, img = self.video.read()
            if not success or img is None:
                break

            img = self.pose_detector.getPose(img, draw=False)
            lmList = self.pose_detector.getPosition(img, draw=False)

            if lmList:
                self._maybe_call_vision(img, lmList, frame_idx)

                angle = self._hip_knee_ankle_angle(lmList)
                direction = self.pose_detector.checkDirectionFromAngle(
                    angle, 110, 110, self.counter.previous_angle, downward_movement=True
                )
                self.counter.process(angle, lmList, self.pose_detector, direction)

            frame_idx += 1

        self.video.release()

        stats = self.counter.get_stats()
        good = stats['count']
        no_reps = stats['no_rep']
        total = good + no_reps
        expected = self.expected_reps or 0
        is_valid = good >= expected if expected else True

        return {
            'total_reps': total,
            'no_reps': no_reps,
            'good_reps': good,
            'is_valid': is_valid,
            'is_scaled': False,
            'breakdown': [],
            'rep_log': stats.get('rep_log', []),
            'rounds_completed': 1 if is_valid else 0,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _maybe_call_vision(self, img, lmList: list, frame_idx: int) -> None:
        check = self.counter.get_vision_check_needed(lmList)
        if not check:
            return
        if frame_idx - self._last_vision_frame < self._vision_cooldown_frames:
            return

        self._last_vision_frame = frame_idx
        prompt = _VISION_PROMPTS[check]
        _, buf = cv2.imencode('.jpg', img)
        confirmed, raw = self.vision_client.ask_yes_no([bytes(buf)], prompt)
        logger.info("Vision check '%s' frame=%d confirmed=%s raw=%s", check, frame_idx, confirmed, raw)

        if confirmed:
            prev_phase = self.counter._phase
            self.counter.update_barbell_confirmed(check)
            # Phase changed — allow next check almost immediately so fast movements
            # (e.g. the jerk after front rack) aren't blocked by the full cooldown.
            if self.counter._phase != prev_phase:
                self._last_vision_frame = frame_idx - self._vision_cooldown_frames + 5

    def _hip_knee_ankle_angle(self, lmList: list) -> float:
        """Hip-knee-ankle angle on the more visible side."""
        l_vis = lmList[23][3] if len(lmList[23]) > 3 else 0
        r_vis = lmList[24][3] if len(lmList[24]) > 3 else 0
        if l_vis >= r_vis:
            hip, knee, ankle = 23, 25, 27
        else:
            hip, knee, ankle = 24, 26, 28
        return self.pose_detector.getAngle(None, hip, knee, ankle)


# ------------------------------------------------------------------
# Convenience entry point
# ------------------------------------------------------------------

def analyse_barbell_video(
    video_url: str,
    movement_type: str,
    expected_reps: int | None = None,
) -> dict:
    """
    Download (if needed) and analyse a barbell movement video.

    Args:
        video_url:     YouTube URL or local file path.
        movement_type: 'clean_and_jerk', 'hang_clean_and_jerk',
                       'snatch', or 'hang_snatch'.
        expected_reps: Target rep count for validity check.
    """
    criteria = load_movement_criteria()
    is_local = video_url and __import__('os').path.exists(video_url)
    video_path = video_url if is_local else download_youtube_video(video_url)
    try:
        analyser = BarbellAnalyser(video_path, movement_type, expected_reps, criteria)
        return analyser.analyse()
    finally:
        if not is_local and __import__('os').path.exists(video_path):
            __import__('os').unlink(video_path)
