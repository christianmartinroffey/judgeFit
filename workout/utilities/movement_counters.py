"""
Movement-specific rep counters for CrossFit movements
Each counter implements the specific rules for counting valid reps
"""
import logging
from abc import ABC, abstractmethod
from collections import deque


class BaseCounter(ABC):
    """Base class for all movement counters"""

    def __init__(self, criteria):
        self.criteria = criteria
        self.count = 0
        self.no_rep = 0
        self.is_started = False
        self.outcome = ""
        self.previous_angle = 0

    @abstractmethod
    def process(self, angle, lmList, detector, direction):
        """Process a frame and update rep count"""
        pass

    def get_stats(self):
        """Return current counting statistics"""
        return {
            'count': self.count,
            'no_rep': self.no_rep,
            'outcome': self.outcome,
            'is_started': self.is_started
        }

    def reset(self):
        """Reset counter state"""
        self.count = 0
        self.no_rep = 0
        self.is_started = False
        self.outcome = ""
        self.previous_angle = 0


class SquatCounter(BaseCounter):
    """Counter for air squats"""

    def __init__(self, criteria):
        super().__init__(criteria)
        self.full_depth = False
        self.full_extension = False

        # Load thresholds from criteria
        self.descending_threshold = criteria.get('descending_threshold', 110)
        self.ascending_threshold = criteria.get('ascending_threshold', 110)
        self.start_point = criteria.get('start_point', 165)  # Full extension
        self.end_point = criteria.get('end_point', 60)  # Full depth

    def process(self, angle, lmList, detector, direction):
        """
        Process squat rep counting

        Args:
            angle: Current knee angle
            lmList: Pose landmarks
            detector: PoseDetector instance
            direction: 0 = descending, 1 = ascending
        """
        # Descending phase
        if direction == 0 and angle < self.descending_threshold:
            if not self.is_started:
                self.is_started = True
                self.full_depth = False
                self.full_extension = False
                self.outcome = ''

            # Check if reached full depth
            if angle <= self.end_point:
                self.full_depth = True

        # Ascending phase
        elif direction == 1 and self.is_started:
            if angle >= self.start_point:
                self.full_extension = True

            # Check for no full extension
            if self.full_depth:
                if not self.full_extension:
                    # If angle starts decreasing again (going back down)
                    if angle < self.previous_angle:
                        self.no_rep += 1
                        self.outcome = "no full extension"
                        self.is_started = False
                        self.full_depth = False
                        self.full_extension = False

            # Check for not deep enough
            elif not self.full_depth:
                if angle > self.previous_angle and self.full_extension:
                    self.no_rep += 1
                    self.outcome = "not deep enough"
                    self.is_started = False
                    self.full_depth = False
                    self.full_extension = False

        # Check for complete rep
        if self.full_depth and self.full_extension:
            self.count += 1
            self.outcome = "good rep"
            self.is_started = False
            self.full_depth = False
            self.full_extension = False

        self.previous_angle = int(angle)

        return self.get_stats()

    def reset(self):
        super().reset()
        self.full_depth = False
        self.full_extension = False


class PushUpCounter(BaseCounter):
    """Counter for push-ups"""

    def __init__(self, criteria):
        super().__init__(criteria)
        self.full_extension = False
        self.chest_to_ground = False

        # Push-up specific thresholds (using elbow angle)
        self.descending_threshold = criteria.get('descending_threshold', 90)
        self.ascending_threshold = criteria.get('ascending_threshold', 160)
        self.bottom_threshold = criteria.get('end_point', 60)  # Chest close to ground
        self.top_threshold = criteria.get('start_point', 165)  # Arms extended

    def process(self, angle, lmList, detector, direction):
        """
        Process push-up rep counting

        Args:
            angle: Current elbow angle
            lmList: Pose landmarks
            detector: PoseDetector instance
            direction: 0 = descending, 1 = ascending
        """
        # Descending phase (going down)
        if direction == 0 and angle < self.descending_threshold:
            if not self.is_started:
                self.is_started = True
                self.chest_to_ground = False
                self.full_extension = False
                self.outcome = ''

            # Check if chest reached ground level
            if angle <= self.bottom_threshold:
                self.chest_to_ground = True

        # Ascending phase (pushing up)
        elif direction == 1 and self.is_started:
            if angle >= self.top_threshold:
                self.full_extension = True

            # Check for incomplete lockout
            if self.chest_to_ground and not self.full_extension:
                if angle < self.previous_angle:  # Starting to go back down
                    self.no_rep += 1
                    self.outcome = "no lockout"
                    self.is_started = False
                    self.chest_to_ground = False
                    self.full_extension = False

            # Check for not low enough
            elif not self.chest_to_ground and angle > self.previous_angle:
                if self.full_extension:
                    self.no_rep += 1
                    self.outcome = "not low enough"
                    self.is_started = False
                    self.chest_to_ground = False
                    self.full_extension = False

        # Check for complete rep
        if self.chest_to_ground and self.full_extension:
            self.count += 1
            self.outcome = "good rep"
            self.is_started = False
            self.chest_to_ground = False
            self.full_extension = False

        self.previous_angle = int(angle)

        return self.get_stats()

    def reset(self):
        super().reset()
        self.full_extension = False
        self.chest_to_ground = False


class PullUpCounter(BaseCounter):
    """Counter for pull-ups"""

    def __init__(self, criteria):
        super().__init__(criteria)
        self.chin_over_bar = False
        self.full_extension = False

        # Pull-up specific thresholds
        self.descending_threshold = criteria.get('descending_threshold', 30)
        self.ascending_threshold = criteria.get('ascending_threshold', 150)
        self.chin_threshold = criteria.get('regular_full_range_threshold', 10)
        self.extension_threshold = criteria.get('full_extension_threshold', 170)

    def process(self, angle, lmList, detector, direction):
        """
        Process pull-up rep counting

        Args:
            angle: Current elbow/shoulder angle
            lmList: Pose landmarks
            detector: PoseDetector instance
            direction: 0 = ascending (pulling up), 1 = descending (going down)
        """
        # Note: For pull-ups, direction is inverted
        # direction 0 = pulling up (ascending)
        # direction 1 = lowering down (descending)

        # Pulling up phase
        if direction == 0 and angle < self.descending_threshold:
            if not self.is_started:
                self.is_started = True
                self.chin_over_bar = False
                self.full_extension = False
                self.outcome = ''

            # Check if chin cleared bar
            if angle <= self.chin_threshold:
                self.chin_over_bar = True

        # Lowering down phase
        elif direction == 1 and self.is_started:
            if angle >= self.extension_threshold:
                self.full_extension = True

            # Check for incomplete descent
            if self.chin_over_bar and not self.full_extension:
                if angle < self.previous_angle:  # Starting to go back up
                    self.no_rep += 1
                    self.outcome = "no full extension"
                    self.is_started = False
                    self.chin_over_bar = False
                    self.full_extension = False

            # Check for chin not over bar
            elif not self.chin_over_bar and angle > self.previous_angle:
                if self.full_extension:
                    self.no_rep += 1
                    self.outcome = "chin not over bar"
                    self.is_started = False
                    self.chin_over_bar = False
                    self.full_extension = False

        # Check for complete rep
        if self.chin_over_bar and self.full_extension:
            self.count += 1
            self.outcome = "good rep"
            self.is_started = False
            self.chin_over_bar = False
            self.full_extension = False

        self.previous_angle = int(angle)

        return self.get_stats()

    def reset(self):
        super().reset()
        self.chin_over_bar = False
        self.full_extension = False


class ToesToBarCounter(BaseCounter):
    """Counter for toes-to-bar"""

    def __init__(self, criteria):
        super().__init__(criteria)
        self.toes_to_bar = False
        self.full_extension = False

        # T2B specific thresholds
        self.descending_threshold = criteria.get('descending_threshold', 30)
        self.ascending_threshold = criteria.get('ascending_threshold', 150)
        self.t2b_threshold = criteria.get('full_range_threshold', 10)
        self.extension_threshold = criteria.get('full_extension_threshold', 170)

    def process(self, angle, lmList, detector, direction):
        """
        Process toes-to-bar rep counting

        Args:
            angle: Hip angle or leg elevation angle
            lmList: Pose landmarks
            detector: PoseDetector instance
            direction: Movement direction
        """
        # Ascending phase (legs going up)
        if direction == 0 and angle < self.descending_threshold:
            if not self.is_started:
                self.is_started = True
                self.toes_to_bar = False
                self.full_extension = False
                self.outcome = ''

            # Check if toes reached bar
            if angle <= self.t2b_threshold:
                self.toes_to_bar = True

        # Descending phase (legs going down)
        elif direction == 1 and self.is_started:
            if angle >= self.extension_threshold:
                self.full_extension = True

            # Check for incomplete descent
            if self.toes_to_bar and not self.full_extension:
                if angle < self.previous_angle:  # Starting to go back up
                    self.no_rep += 1
                    self.outcome = "no full extension"
                    self.is_started = False
                    self.toes_to_bar = False
                    self.full_extension = False

            # Check for toes not to bar
            elif not self.toes_to_bar and angle > self.previous_angle:
                if self.full_extension:
                    self.no_rep += 1
                    self.outcome = "toes not to bar"
                    self.is_started = False
                    self.toes_to_bar = False
                    self.full_extension = False

        # Check for complete rep
        if self.toes_to_bar and self.full_extension:
            self.count += 1
            self.outcome = "good rep"
            self.is_started = False
            self.toes_to_bar = False
            self.full_extension = False

        self.previous_angle = int(angle)

        return self.get_stats()

    def reset(self):
        super().reset()
        self.toes_to_bar = False
        self.full_extension = False


class ThrusterCounter(BaseCounter):
    """
    Counter for thrusters (front squat into overhead press).

    Primary angle tracked: hip-knee-ankle (squat depth).
    At the top, also checks:
      - shoulder-elbow-wrist angle >= overhead_angle_threshold (arms locked out)
      - x-coordinate spread of wrist, elbow, shoulder, hip, knee <= alignment_tolerance
        (landmarks vertically stacked, confirming barbell is overhead)
    """

    def __init__(self, criteria):
        super().__init__(criteria)
        self.full_depth = False
        self.overhead_lockout = False

        self.descending_threshold = criteria.get('descending_threshold', 110)
        self.ascending_threshold = criteria.get('ascending_threshold', 110)
        self.start_point = criteria.get('start_point', 165)        # full hip/knee extension
        self.end_point = criteria.get('end_point', 65)             # full squat depth
        self.overhead_angle_threshold = criteria.get('overhead_angle_threshold', 160)
        self.alignment_tolerance = criteria.get('alignment_tolerance', 50)  # pixels

    def _pick_side(self, lmList):
        """Return (wrist, elbow, shoulder, hip, knee) indices for the more visible side."""
        if lmList[23][3] > lmList[24][3]:
            return 15, 13, 11, 23, 25   # left: wrist, elbow, shoulder, hip, knee
        return 16, 14, 12, 24, 26       # right

    def _check_overhead(self, lmList, detector):
        """
        Return True when the athlete has a valid overhead lockout:
          1. Arm angle (shoulder-elbow-wrist) >= overhead_angle_threshold
          2. Wrist, elbow, shoulder, hip, knee x-coordinates are within alignment_tolerance
        """
        wrist, elbow, shoulder, hip, knee = self._pick_side(lmList)

        arm_angle = detector.getAngle(None, shoulder, elbow, wrist)
        if arm_angle < self.overhead_angle_threshold:
            return False

        xs = [lmList[i][1] for i in (wrist, elbow, shoulder, hip, knee)]
        return (max(xs) - min(xs)) <= self.alignment_tolerance

    def process(self, angle, lmList, detector, direction):
        """
        Process a thruster rep.

        Args:
            angle: hip-knee-ankle angle (drives squat phase direction)
            lmList: pose landmarks
            detector: PoseDetector instance
            direction: 0 = descending, 1 = ascending
        """
        # Descending — going into the squat
        if direction == 0 and angle < self.descending_threshold:
            if not self.is_started:
                self.is_started = True
                self.full_depth = False
                self.overhead_lockout = False
                self.outcome = ''

            if angle <= self.end_point:
                self.full_depth = True

        # Ascending — driving up and pressing overhead
        elif direction == 1 and self.is_started:
            if angle >= self.start_point:
                if self._check_overhead(lmList, detector):
                    self.overhead_lockout = True

            # Had depth but didn't lock out — athlete is heading back down
            if self.full_depth and not self.overhead_lockout:
                if angle < self.previous_angle:
                    self.no_rep += 1
                    self.outcome = 'no overhead lockout'
                    self.is_started = False
                    self.full_depth = False

            # Locked out overhead but never reached depth
            elif not self.full_depth and self.overhead_lockout:
                if angle > self.previous_angle:
                    self.no_rep += 1
                    self.outcome = 'not deep enough'
                    self.is_started = False
                    self.overhead_lockout = False

        # Valid rep: reached full depth AND overhead lockout
        if self.full_depth and self.overhead_lockout:
            self.count += 1
            self.outcome = 'good rep'
            self.is_started = False
            self.full_depth = False
            self.overhead_lockout = False

        self.previous_angle = int(angle)
        return self.get_stats()

    def reset(self):
        super().reset()
        self.full_depth = False
        self.overhead_lockout = False


class WallBallCounter(BaseCounter):
    """
    Counter for wall ball shots.

    A valid rep requires ALL of:
      1. Squat depth: hip-knee-ankle angle <= end_point threshold
      2. Ball thrown: centroid Y moves upward after squat ascent
      3. Target reached: ball centroid Y reaches/passes target_y_px
      4. Ball caught: centroid Y returns below shoulder height

    State machine phases (in order):
        IDLE → SQUATTING → THROWING → BALL_AT_TARGET → CATCHING → (rep)

    ``update_ball_position()`` must be called with the latest ball detection
    before each call to ``process()``.
    ``set_target_y()`` must be called once after TargetDetector calibrates.
    """

    IDLE = 'idle'
    SQUATTING = 'squatting'
    THROWING = 'throwing'
    BALL_AT_TARGET = 'ball_at_target'
    CATCHING = 'catching'

    # How many consecutive frames without a ball detection before we consider
    # the ball dropped (during CATCHING phase).
    _MAX_BALL_LOSS_FRAMES = 20
    # If stuck in THROWING this many frames with no resolution, reset silently.
    _THROWING_TIMEOUT_FRAMES = 120
    # If stuck waiting for ball to descend from target this long, advance anyway.
    _TARGET_TIMEOUT_FRAMES = 60
    # If stuck in CATCHING this long, finalise the rep rather than hanging forever.
    _CATCHING_TIMEOUT_FRAMES = 90

    def __init__(self, criteria: dict):
        super().__init__(criteria)
        self.descending_threshold = criteria.get('descending_threshold', 110)
        self.ascending_threshold = criteria.get('ascending_threshold', 110)
        self.start_point = criteria.get('start_point', 165)
        self.end_point = criteria.get('end_point', 65)
        self.ball_height_tolerance_px = criteria.get('ball_height_tolerance_px', 40)
        self.min_throw_frames = criteria.get('min_throw_frames', 3)

        self.target_y_px: int | None = None
        self._phase = self.IDLE
        self._squat_achieved = False
        self._ball_at_target_achieved = False
        self._shoulder_y_px: int | None = None
        self._wrist_y_px: int | None = None

        # Ball tracking
        self._current_ball: dict | None = None
        self._ball_positions: deque = deque(maxlen=10)
        self._ball_loss_frames: int = 0
        self._throw_frame_count: int = 0
        self._phase_frames: int = 0
        # Minimum ball Y seen during the current throw — used for target check
        # so YOLO missing a few frames at the apex doesn't cause a false no-rep.
        self._throw_min_y: int | None = None
        # Observed ball peaks (minimum Y per throw) used to recalibrate target.
        self._peak_samples: list[int] = []

        # Per-rep event log — each entry is saved as a ScoreBreakdown record.
        # {'rep_number', 'is_good_rep', 'no_rep_reason', 'rep_timestamp'}
        self._rep_log: list[dict] = []
        self._frame_counter: int = 0
        self._video_fps: float = 30.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_target_y(self, target_y_px: int) -> None:
        """Called by WallBallAnalyser once TargetDetector has calibrated."""
        self.target_y_px = target_y_px

    def set_fps(self, fps: float) -> None:
        """Set video FPS so rep timestamps can be converted to seconds."""
        self._video_fps = fps if fps > 0 else 30.0

    def get_stats(self) -> dict:
        stats = super().get_stats()
        stats['rep_log'] = self._rep_log
        return stats

    def update_ball_position(self, ball_detection: dict | None) -> None:
        """
        Receive the latest ball detection result from GymObjectDetector.
        Must be called before process() on each frame.

        Args:
            ball_detection: dict with 'centroid' key, or None if not detected.
        """
        self._current_ball = ball_detection
        if ball_detection and ball_detection.get('centroid'):
            self._ball_positions.append(ball_detection['centroid'])
            self._ball_loss_frames = 0
        else:
            self._ball_loss_frames += 1

    def process(self, angle: float, lmList: list, detector, direction: int) -> dict:
        """
        Process one frame.

        Args:
            angle:     Hip-knee-ankle angle (squat angle).
            lmList:    Pose landmark list from PoseDetector.
            detector:  PoseDetector instance (unused here but required by interface).
            direction: 0 = descending, 1 = ascending.
        """
        # Track shoulder and wrist Y for catch-height validation.
        # In wall balls the ball is caught above the shoulder joint, so we
        # use the wrist (raised to receive the ball) as the primary reference.
        if lmList and len(lmList) > 12:
            l_vis = lmList[11][3] if len(lmList[11]) > 3 else 0
            r_vis = lmList[12][3] if len(lmList[12]) > 3 else 0
            self._shoulder_y_px = lmList[11][2] if l_vis >= r_vis else lmList[12][2]
        if lmList and len(lmList) > 16:
            l_wrist = lmList[15][2] if len(lmList[15]) > 2 else None
            r_wrist = lmList[16][2] if len(lmList[16]) > 2 else None
            wrists = [w for w in (l_wrist, r_wrist) if w is not None]
            # Use the higher wrist (smaller Y = raised hand) as the catch reference.
            if wrists:
                self._wrist_y_px = min(wrists)

        self._frame_counter += 1
        self._advance_state(angle, direction)
        self.previous_angle = int(angle)
        return self.get_stats()

    def reset(self):
        super().reset()
        self._phase = self.IDLE
        self._squat_achieved = False
        self._ball_at_target_achieved = False
        self._shoulder_y_px = None
        self._shoulder_y_px = None
        self._wrist_y_px = None
        self._current_ball = None
        self._ball_positions.clear()
        self._ball_loss_frames = 0
        self._throw_frame_count = 0
        self._phase_frames = 0
        self._throw_min_y = None
        self._peak_samples = []
        self._rep_log = []
        self._frame_counter = 0

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def _ball_y(self) -> int | None:
        """Return current ball centroid Y, or None."""
        if self._current_ball and self._current_ball.get('centroid'):
            return self._current_ball['centroid'][1]
        return None

    def _ball_moving_up(self) -> bool:
        """Return True if the ball's recent trajectory is upward (decreasing Y)."""
        if len(self._ball_positions) < 2:
            return False
        # Compare latest position with oldest in the window.
        return self._ball_positions[-1][1] < self._ball_positions[0][1]

    def _advance_state(self, angle: float, direction: int) -> None:
        ball_y = self._ball_y()

        # Track frames spent in any active (non-IDLE) phase.
        if self._phase != self.IDLE:
            self._phase_frames += 1

        # ---- IDLE ---------------------------------------------------
        if self._phase == self.IDLE:
            if direction == 0 and angle < self.descending_threshold:
                self._phase = self.SQUATTING
                self._squat_achieved = False
                self._ball_at_target_achieved = False
                self._throw_frame_count = 0
                self._phase_frames = 0
                self.is_started = True
                self.outcome = ''
                logging.debug("Rep attempt started — descending (angle=%.1f)", angle)

        # ---- SQUATTING ----------------------------------------------
        elif self._phase == self.SQUATTING:
            if angle <= self.end_point:
                if not self._squat_achieved:
                    logging.debug("Squat depth achieved (angle=%.1f <= end_point=%d)", angle, self.end_point)
                self._squat_achieved = True

            if direction == 1:
                # Athlete is coming back up — watch for the throw.
                if self._ball_moving_up():
                    self._phase = self.THROWING
                    self._phase_frames = 0
                    logging.debug(
                        "→ THROWING (ball moving up, squat_achieved=%s, angle=%.1f)",
                        self._squat_achieved, angle,
                    )
                elif angle >= self.start_point:
                    # Fully stood up without a visible ball throw.
                    if not self._squat_achieved:
                        logging.info(
                            "No-rep: stood up without squat depth (min angle seen not <= %d)",
                            self.end_point,
                        )
                        self._record_no_rep("not deep enough")
                    else:
                        # Stood up, ball not yet detected moving — transition anyway.
                        self._phase = self.THROWING
                        self._phase_frames = 0
                        logging.debug("→ THROWING (stood up, no ball detected yet)")

        # ---- THROWING -----------------------------------------------
        elif self._phase == self.THROWING:
            if ball_y is not None and self._ball_moving_up():
                self._throw_frame_count += 1

            # Track the highest point (smallest Y) the ball has reached this throw.
            # This lets us confirm target was reached even when YOLO misses the apex.
            if ball_y is not None:
                if self._throw_min_y is None or ball_y < self._throw_min_y:
                    self._throw_min_y = ball_y

            # Use the best Y seen this throw (not just current frame) for target check.
            peak_y = self._throw_min_y if self._throw_min_y is not None else ball_y
            if self.target_y_px is not None and peak_y is not None:
                if peak_y <= self.target_y_px + self.ball_height_tolerance_px:
                    self._ball_at_target_achieved = True
                    self._phase = self.BALL_AT_TARGET
                    self._phase_frames = 0
                    # Record this peak for target recalibration.
                    self._peak_samples.append(peak_y)
                    logging.debug("Ball reached target zone: peak_y=%d target_y=%d", peak_y, self.target_y_px)

            # Ball has started falling without reaching the target zone.
            # Use throw_min_y so we're judging the highest point achieved, not current position.
            if (
                self._phase == self.THROWING
                and self._throw_frame_count >= self.min_throw_frames
                and not self._ball_moving_up()
                and not self._ball_at_target_achieved
                and self.target_y_px is not None
                and self._throw_min_y is not None
            ):
                if self._throw_min_y > self.target_y_px + self.ball_height_tolerance_px:
                    self._record_no_rep("ball didn't reach target")

            # Ball was thrown but then lost (CSRT unavailable / occlusion at peak).
            # Advance optimistically rather than getting stuck in this phase.
            if (
                self._phase == self.THROWING
                and not self._ball_at_target_achieved
                and self._throw_frame_count >= self.min_throw_frames
                and ball_y is None
                and self._ball_loss_frames >= self._MAX_BALL_LOSS_FRAMES
            ):
                logging.debug("Ball lost after throw — advancing to BALL_AT_TARGET optimistically")
                self._ball_at_target_achieved = True
                self._phase = self.BALL_AT_TARGET
                self._phase_frames = 0

            # Safety timeout: stuck in THROWING with no resolution → reset silently.
            if self._phase == self.THROWING and self._phase_frames > self._THROWING_TIMEOUT_FRAMES:
                logging.debug("THROWING timeout — resetting phase")
                self._reset_phase()

        # ---- BALL_AT_TARGET -----------------------------------------
        elif self._phase == self.BALL_AT_TARGET:
            # Wait for ball to start descending.
            if ball_y is not None and not self._ball_moving_up():
                logging.debug("→ CATCHING (ball descending from target, ball_y=%s)", ball_y)
                self._phase = self.CATCHING
                self._phase_frames = 0

            # Ball lost at peak (no CSRT) — assume it's on the way down.
            if (
                self._phase == self.BALL_AT_TARGET
                and ball_y is None
                and self._ball_loss_frames >= self._MAX_BALL_LOSS_FRAMES
            ):
                logging.debug("→ CATCHING (ball lost at peak — assuming descent)")
                self._phase = self.CATCHING
                self._phase_frames = 0

            # Safety timeout.
            if self._phase == self.BALL_AT_TARGET and self._phase_frames > self._TARGET_TIMEOUT_FRAMES:
                logging.debug("→ CATCHING (BALL_AT_TARGET timeout)")
                self._phase = self.CATCHING
                self._phase_frames = 0

        # ---- CATCHING -----------------------------------------------
        elif self._phase == self.CATCHING:
            caught = False

            if ball_y is not None:
                # Primary: ball has descended to raised-wrist level.
                # Wall balls are caught above the shoulder joint, so we use
                # the wrist landmark (which rises to receive the ball).
                if self._wrist_y_px is not None and ball_y >= self._wrist_y_px:
                    caught = True

                # Secondary: ball has dropped a meaningful distance below the
                # target — reliable even without accurate landmark data.
                if not caught and self.target_y_px is not None:
                    if ball_y > self.target_y_px + (self.ball_height_tolerance_px * 2):
                        caught = True

                # Tertiary fallback: ball is at or below shoulder joint.
                if not caught and self._shoulder_y_px is not None:
                    if ball_y >= self._shoulder_y_px:
                        caught = True

            if caught:
                logging.debug(
                    "Catch detected: ball_y=%s wrist_y=%s shoulder_y=%s",
                    ball_y, self._wrist_y_px, self._shoulder_y_px,
                )
                self._finalise_rep()
                self._reset_phase()

            elif self._ball_loss_frames >= self._MAX_BALL_LOSS_FRAMES:
                # Ball invisible while being held — count as good if criteria met.
                if self._squat_achieved and self._ball_at_target_achieved:
                    logging.info(
                        "Ball lost during catch; squat+target criteria met — counting as good rep"
                    )
                    self._finalise_rep()
                else:
                    self._record_no_rep("ball dropped")
                self._reset_phase()

            elif self._phase_frames >= self._CATCHING_TIMEOUT_FRAMES:
                # No catch signal detected — finalise based on what was achieved.
                logging.info(
                    "CATCHING timeout after %d frames "
                    "(wrist_y=%s ball_y=%s) — finalising rep",
                    self._phase_frames, self._wrist_y_px, ball_y,
                )
                self._finalise_rep()
                self._reset_phase()

    def _finalise_rep(self) -> None:
        """Count or reject the completed rep cycle based on achieved criteria."""
        if self._squat_achieved and self._ball_at_target_achieved:
            self.count += 1
            self.outcome = 'good rep'
            logging.info(
                "Rep #%d counted  ✓  (squat_depth=OK, ball_at_target=OK)",
                self.count,
            )
            self._rep_log.append({
                'rep_number': self.count + self.no_rep,
                'is_good_rep': True,
                'no_rep_reason': None,
                'rep_timestamp': int(self._frame_counter / self._video_fps),
            })
        else:
            reasons = []
            if not self._squat_achieved:
                reasons.append("not deep enough")
            if not self._ball_at_target_achieved:
                reasons.append("ball didn't reach target")
            reason = " + ".join(reasons)
            self._record_no_rep(reason)

    # Maps reason strings to ScoreBreakdown.no_rep_reason codes.
    _NO_REP_CODE_MAP = {
        'not deep enough': 'D',
        'ball didn\'t reach target': 'T',
        'ball dropped': 'T',
        'not deep enough + ball didn\'t reach target': 'D',
    }

    def _record_no_rep(self, reason: str) -> None:
        self.no_rep += 1
        self.outcome = reason
        logging.info(
            "No-rep #%d  ✗  reason: %s  "
            "(squat_depth=%s, ball_at_target=%s)",
            self.no_rep,
            reason,
            "OK" if self._squat_achieved else "FAIL",
            "OK" if self._ball_at_target_achieved else "FAIL",
        )
        self._rep_log.append({
            'rep_number': self.count + self.no_rep,
            'is_good_rep': False,
            'no_rep_reason': self._NO_REP_CODE_MAP.get(reason, 'T'),
            'rep_timestamp': int(self._frame_counter / self._video_fps),
        })
        self._reset_phase()

    def _reset_phase(self) -> None:
        self._phase = self.IDLE
        self._squat_achieved = False
        self._ball_at_target_achieved = False
        self._throw_frame_count = 0
        self._phase_frames = 0
        self._throw_min_y = None
        self._ball_positions.clear()
        self._ball_loss_frames = 0
        self.is_started = False
