"""
WorkoutAnalyser: Multi-movement video analysis for structured CrossFit workouts.

Tracks progress through a workout plan (ordered sequence of movements with target
rep counts), classifying each frame and counting reps per set. Advances through
the plan either when required reps are reached or when the classifier detects the
athlete has switched movement.
"""
import logging
import os

import cv2

import workout.utilities.PoseModule as pm
from workout.utilities.movement_classifier import MovementClassifier
from workout.utilities.movement_counters import (
    PullUpCounter, PushUpCounter, SquatCounter, ThrusterCounter, ToesToBarCounter,
    WallBallCounter,
)
from workout.utilities.utils import download_youtube_video, load_movement_criteria

logger = logging.getLogger(__name__)


def _torso_bbox(lmList: list) -> tuple | None:
    """Rough torso bounding box from pose landmarks for ball-detection false-positive filtering."""
    try:
        xs = [lmList[i][1] for i in (11, 12, 23, 24)]
        ys = [lmList[i][2] for i in (11, 12, 23, 24)]
        padding = 30
        return (min(xs) - padding, min(ys) - padding, max(xs) + padding, max(ys) + padding)
    except (IndexError, TypeError):
        return None


# Maps human-readable movement names (from the DB) to the internal classifier keys.
_NAME_MAP = {
    'air squat': 'squat',
    'squat': 'squat',
    'thruster': 'thruster',
    'back squat': 'squat',
    'front squat': 'squat',
    'overhead squat': 'squat',
    'push-up': 'push_up',
    'push up': 'push_up',
    'pushup': 'push_up',
    'push ups': 'push_up',
    'pull-up': 'pull_up',
    'pull up': 'pull_up',
    'pullup': 'pull_up',
    'pull ups': 'pull_up',
    'toes to bar': 'toes_to_bar',
    'toes-to-bar': 'toes_to_bar',
    't2b': 'toes_to_bar',
    'wall ball': 'wall_ball',
    'wall balls': 'wall_ball',
    'wall-ball': 'wall_ball',
    'wallball': 'wall_ball',
    'wall ball shot': 'wall_ball',
    'wall ball shots': 'wall_ball',
    'clean and jerk': 'clean_and_jerk',
    'clean & jerk': 'clean_and_jerk',
    'clean-and-jerk': 'clean_and_jerk',
    'hang clean and jerk': 'hang_clean_and_jerk',
    'hang clean & jerk': 'hang_clean_and_jerk',
    'snatch': 'snatch',
    'hang snatch': 'hang_snatch',
}

_BARBELL_MOVEMENTS = {'clean_and_jerk', 'hang_clean_and_jerk', 'snatch', 'hang_snatch'}


def normalise_movement_name(name: str) -> str:
    """Normalise a movement name to a consistent internal key."""
    key = name.lower().strip()
    if key in _NAME_MAP:
        return _NAME_MAP[key]
    # Fallback: replace spaces/hyphens with underscores
    return key.replace('-', '_').replace(' ', '_')


class WorkoutPlan:
    """
    Describes the ordered sequence of movements expected in a workout.

    For 'For Time' workouts the sequence is fixed and runs once.
    For AMRAP workouts the sequence repeats until the video ends.
    """

    def __init__(self, components: list, workout_type: str = 'FT'):
        """
        Args:
            components: list of dicts, each with:
                        - movement: normalised movement key (e.g. 'squat')
                        - expected_reps: int or None
                        - sequence: int (ordering key)
            workout_type: 'FT' (For Time), 'AMRAP', or 'FW' (For Weight)
        """
        self.components = sorted(components, key=lambda c: c['sequence'])
        self.workout_type = workout_type
        self.is_amrap = workout_type == 'AMRAP'

    def get_current_spec(self, plan_index: int) -> dict | None:
        """Return the movement spec at plan_index, wrapping around for AMRAP."""
        if not self.components:
            return None
        return self.components[plan_index % len(self.components)]

    def is_complete(self, plan_index: int) -> bool:
        """True when a For Time workout has had all its movements processed."""
        if self.is_amrap:
            return False
        return plan_index >= len(self.components)

    def __len__(self):
        return len(self.components)


class WorkoutAnalyser:
    """
    Frame-by-frame video analyser for multi-movement workouts.

    Responsibilities:
    - Classify the movement being performed on each frame.
    - Count valid/invalid reps using movement-specific counters.
    - Advance through the WorkoutPlan when a set is completed or the
      classifier detects a movement switch.
    - Accumulate per-set results across the full video.
    """

    def __init__(self, video_path: str, workout_plan: WorkoutPlan, criteria: dict):
        """
        Args:
            video_path: Local filesystem path to the video file.
            workout_plan: WorkoutPlan instance.
            criteria: Movement analysis criteria loaded from JSON config.
        """
        self.video = cv2.VideoCapture(video_path)
        self.plan = workout_plan
        self.criteria = criteria

        self.detector = pm.PoseDetector()
        self.classifier = MovementClassifier(buffer_size=15)

        # Note: the JSON config key for push-ups is 'pushup', not 'push_up'.
        self.counters: dict = {
            'squat': SquatCounter(criteria.get('squat', {})),
            'thruster': ThrusterCounter(criteria.get('thruster', {})),
            'push_up': PushUpCounter(criteria.get('pushup', {})),
            'pull_up': PullUpCounter(criteria.get('pull_up', {})),
            'toes_to_bar': ToesToBarCounter(criteria.get('toes_to_bar', {})),
        }

        # Wall ball needs YOLO + target detection; only load if the plan contains wall balls.
        self._object_detector = None
        self._target_detector = None
        self._wall_ball_frame_idx: int = 0
        self._wall_ball_calibration_frames: int = 30
        if any(c['movement'] == 'wall_ball' for c in workout_plan.components):
            from workout.utilities.wall_ball.object_detector import GymObjectDetector  # noqa: PLC0415
            from workout.utilities.wall_ball.target_detector import TargetDetector  # noqa: PLC0415
            self.counters['wall_ball'] = WallBallCounter(criteria.get('wall_ball', {}))
            self._object_detector = GymObjectDetector()
            self._target_detector = TargetDetector(
                calibration_frames=self._wall_ball_calibration_frames,
            )

        # State
        self.plan_index: int = 0
        self.round: int = 1
        self.completed_sets: list = []
        self.current_movement: str | None = None
        self.current_counter = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_angle(self, movement: str, lmList: list):
        """Return the primary joint angle for the given movement type."""
        if movement in ('squat', 'thruster'):
            # Both squat and thruster use hip-knee-ankle as the primary angle.
            # ThrusterCounter handles the additional overhead check internally.
            hip, knee, ankle = self.detector.getLandmarkIndices(lmList, is_squat=True)
            return self.detector.getAngle(None, hip, knee, ankle)

        if movement == 'push_up':
            return self.detector.getAngle(None, 12, 14, 16)  # shoulder-elbow-wrist

        if movement == 'pull_up':
            return self.detector.getAngle(None, 12, 14, 16)  # shoulder-elbow-wrist

        if movement == 'toes_to_bar':
            return self.detector.getAngle(None, 24, 26, 28)  # hip-knee-ankle

        if movement == 'wall_ball':
            hip, knee, ankle = self.detector.getLandmarkIndices(lmList, is_squat=True)
            return self.detector.getAngle(None, hip, knee, ankle)

        return None

    def _save_current_set(self, reason: str) -> None:
        """Append the in-progress set to completed_sets."""
        if self.current_counter is None:
            return

        stats = self.current_counter.get_stats()
        spec = self.plan.get_current_spec(self.plan_index)

        entry = {
            'round': self.round,
            'sequence': spec['sequence'] if spec else self.plan_index + 1,
            'movement': self.current_movement,
            'reps': stats['count'] + stats['no_rep'],
            'no_reps': stats['no_rep'],
            'good_reps': stats['good_rep'],
            'expected_reps': spec['expected_reps'] if spec else None,
            'advance_reason': reason,
        }
        self.completed_sets.append(entry)

        logger.info(
            "Set saved — %s: %d reps, %d no-reps (reason: %s)",
            self.current_movement, stats['count'], stats['no_rep'], reason,
        )

    def _advance_plan(self, reason: str) -> None:
        """Save the current set and move to the next position in the plan."""
        self._save_current_set(reason)
        self.plan_index += 1

        # For AMRAP: increment round counter when the sequence wraps
        if self.plan.is_amrap and self.plan.components:
            if self.plan_index > 0 and self.plan_index % len(self.plan.components) == 0:
                self.round += 1
                logger.info("Round %d started", self.round)

    def _switch_movement(self, new_movement: str) -> None:
        """
        Transition to a new movement type.

        Saves the current set (if any), resets the new counter, and logs a
        warning if the athlete is not following the expected plan order.
        """
        if new_movement == self.current_movement:
            return

        if self.current_movement is not None:
            self._advance_plan(reason='movement_change')

        self.current_movement = new_movement
        self.current_counter = self.counters.get(new_movement)
        if self.current_counter:
            self.current_counter.reset()

        # When entering a wall ball set, reset detectors so target calibration starts fresh.
        if new_movement == 'wall_ball' and self._object_detector is not None:
            from workout.utilities.wall_ball.target_detector import TargetDetector  # noqa: PLC0415
            self._target_detector = TargetDetector(
                calibration_frames=self._wall_ball_calibration_frames,
            )
            self._object_detector.reset_tracker()
            self._wall_ball_frame_idx = 0

        logger.info("Switched to movement: %s (plan index %d)", new_movement, self.plan_index)

    def _reps_target_reached(self) -> bool:
        """True if the current counter has hit the required reps for this set."""
        if self.current_counter is None or not self.plan.components:
            return False
        spec = self.plan.get_current_spec(self.plan_index)
        if not spec or not spec.get('expected_reps'):
            return False
        return self.current_counter.count >= spec['expected_reps']

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_frame(self, img, lmList: list) -> dict:
        """
        Process one video frame: classify, count, and advance the plan if needed.

        Returns:
            dict with keys: movement, count, no_rep, outcome, angle, round, plan_index
        """
        stats = {
            'movement': self.current_movement,
            'count': 0,
            'no_rep': 0,
            'outcome': '',
            'angle': 0,
            'round': self.round,
            'plan_index': self.plan_index,
        }

        if not lmList:
            return stats

        # In plan mode: initialise current movement from the plan on the first frame
        # so we never rely on the classifier to name the first movement.
        if self.current_movement is None and self.plan.components:
            first_spec = self.plan.get_current_spec(self.plan_index)
            if first_spec:
                self.current_movement = first_spec['movement']
                self.current_counter = self.counters.get(self.current_movement)

        detected = self.classifier.classify(lmList, self.detector)

        if detected and detected != self.current_movement:
            if self.plan.components:
                # Plan mode: only switch when the classifier sees the *next* expected
                # movement — classifier noise on the current movement is ignored.
                next_spec = self.plan.get_current_spec(self.plan_index + 1)
                if next_spec and detected == next_spec['movement']:
                    self._switch_movement(detected)
            else:
                # Free mode (no plan): follow the classifier freely.
                self._switch_movement(detected)

        stats['movement'] = self.current_movement

        if self.current_movement and self.current_counter:
            # Wall ball: run ball detection and target calibration before counting.
            if self.current_movement == 'wall_ball' and self._object_detector is not None:
                athlete_torso_bbox = _torso_bbox(lmList) if lmList else None
                detection = self._object_detector.detect(img, self._wall_ball_frame_idx, athlete_torso_bbox)
                self.current_counter.update_ball_position(detection.get('ball'))

                if not self._target_detector.is_calibrated:
                    wrist_y = lmList[15][2] if lmList and len(lmList) > 16 else None
                    self._target_detector.update(img, self._wall_ball_frame_idx, wrist_y)
                    if self._target_detector.is_calibrated and self._target_detector.target_y_px:
                        self.current_counter.set_target_y(self._target_detector.target_y_px)
                        logger.info(
                            "Wall ball target set at y=%d px after %d frames",
                            self._target_detector.target_y_px,
                            self._wall_ball_frame_idx,
                        )

                self._wall_ball_frame_idx += 1

            angle = self._get_angle(self.current_movement, lmList)
            if angle is not None:
                movement_criteria = self.criteria.get(self.current_movement, {})
                direction = self.detector.checkDirectionFromAngle(
                    angle,
                    movement_criteria.get('descending_threshold', 110),
                    movement_criteria.get('ascending_threshold', 110),
                    self.current_counter.previous_angle,
                    downward_movement=(self.current_movement in ['squat', 'push_up', 'thruster', 'wall_ball']),
                )

                counter_stats = self.current_counter.process(
                    angle, lmList, self.detector, direction
                )
                stats.update(counter_stats)
                stats['angle'] = angle
                stats['round'] = self.round
                stats['plan_index'] = self.plan_index

                # Advance to the next set if required reps are complete
                if self._reps_target_reached():
                    self._advance_plan(reason='reps_complete')
                    # Reset the counter for the same movement if it repeats
                    self.current_counter = self.counters.get(self.current_movement)
                    if self.current_counter:
                        self.current_counter.reset()

        return stats

    def analyse(self) -> dict:
        """
        Run analysis on the entire video.

        Returns:
            dict with keys:
                total_reps (int), no_reps (int), is_valid (bool), is_scaled (bool),
                breakdown (list of per-set dicts), rounds_completed (int)
        """
        if not self.video.isOpened():
            raise RuntimeError("Could not open video for analysis")

        has_frames = False
        while True:
            success, img = self.video.read()
            if not success or img is None:
                break
            has_frames = True
            img = self.detector.getPose(img, draw=False)
            lmList = self.detector.getPosition(img, draw=False)
            self.process_frame(img, lmList)

        self.video.release()

        # Persist any in-progress set at the end of the video
        if self.current_movement and self.current_counter:
            in_progress = self.current_counter.get_stats()
            if in_progress['count'] > 0 or in_progress['no_rep'] > 0:
                self._save_current_set(reason='video_end')

        total_reps = sum(s['reps'] for s in self.completed_sets)
        total_no_reps = sum(s['no_reps'] for s in self.completed_sets)
        total_good_reps = sum(s['good_reps'] for s in self.completed_sets)

        # For Time: valid if athlete completed all required reps
        is_valid = has_frames
        if self.plan.components and not self.plan.is_amrap:
            expected_total = sum(
                c['expected_reps'] for c in self.plan.components
                if c.get('expected_reps')
            )
            is_valid = has_frames and (total_good_reps >= expected_total)

        rounds_completed = (
            self.round - 1
            if self.plan.is_amrap
            else (1 if self.plan_index >= len(self.plan.components) else 0)
        )

        return {
            'total_reps': total_reps,
            'no_reps': total_no_reps,
            'good_reps': total_good_reps,
            'is_valid': is_valid,
            'is_scaled': False,
            'breakdown': self.completed_sets,
            'rounds_completed': rounds_completed,
        }


# ------------------------------------------------------------------
# Convenience entry point
# ------------------------------------------------------------------

def analyse_workout_video(
    video_url: str,
    workout_components: list,
    workout_type: str = 'FT',
) -> dict:
    """
    Download a video and run multi-movement workout analysis.

    Args:
        video_url: YouTube URL or local file path.
        workout_components: list of dicts with keys:
                            - movement (str): human-readable name, e.g. 'Air Squat'
                            - expected_reps (int | None): target reps for the set
                            - sequence (int): ordering position in the workout
        workout_type: 'FT' (For Time), 'AMRAP', or 'FW' (For Weight)

    Returns:
        dict: Analysis result including total_reps, no_reps, is_valid, is_scaled,
              breakdown (per-set details), rounds_completed.
    """
    criteria = load_movement_criteria()

    normalised = [
        {
            'movement': normalise_movement_name(c['movement']),
            'expected_reps': c.get('expected_reps') or c.get('reps'),
            'sequence': c['sequence'],
        }
        for c in workout_components
    ]

    # Dispatch to the dedicated wall ball analyser when all components are wall ball.
    if normalised and all(c['movement'] == 'wall_ball' for c in normalised):
        from workout.utilities.wall_ball.wall_ball_analyser import WallBallAnalyser  # noqa: PLC0415
        total_expected = sum(c['expected_reps'] for c in normalised if c.get('expected_reps'))
        is_local = os.path.exists(video_url)
        video_path = video_url if is_local else download_youtube_video(video_url)
        try:
            analyser = WallBallAnalyser(
                video_path,
                expected_reps=total_expected or None,
                criteria=criteria,
                target_y_px=None,
            )
            return analyser.analyse()
        finally:
            if not is_local and os.path.exists(video_path):
                os.unlink(video_path)

    # Dispatch to barbell analyser when all components are the same barbell movement.
    if normalised and all(c['movement'] in _BARBELL_MOVEMENTS for c in normalised):
        movement_type = normalised[0]['movement']
        if all(c['movement'] == movement_type for c in normalised):
            from workout.utilities.barbell.barbell_analyser import BarbellAnalyser  # noqa: PLC0415
            total_expected = sum(c['expected_reps'] for c in normalised if c.get('expected_reps'))
            is_local = os.path.exists(video_url)
            video_path = video_url if is_local else download_youtube_video(video_url)
            try:
                analyser = BarbellAnalyser(
                    video_path,
                    movement_type=movement_type,
                    expected_reps=total_expected or None,
                    criteria=criteria,
                )
                return analyser.analyse()
            finally:
                if not is_local and os.path.exists(video_path):
                    os.unlink(video_path)

    plan = WorkoutPlan(normalised, workout_type=workout_type)

    is_local = os.path.exists(video_url)
    video_path = video_url if is_local else download_youtube_video(video_url)
    try:
        analyser = WorkoutAnalyser(video_path, plan, criteria)
        return analyser.analyse()
    finally:
        if not is_local and os.path.exists(video_path):
            os.unlink(video_path)
