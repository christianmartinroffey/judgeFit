"""
Rep counters for barbell movements (clean and jerk, snatch, and their hang variants).

Architecture
------------
BaseBarbellCounter drives a phase state machine:

    IDLE → GROUNDED (full only) → PULLING → AT_SHOULDER (C&J only) → OVERHEAD → rep

BarbellAnalyser calls:
  1. counter.get_vision_check_needed(lmList)  — pose-triggered; returns what to ask
  2. counter.update_barbell_confirmed(pos)    — after vision model responds
  3. counter.process(angle, lmList, detector, direction)  — every frame

CleanAndJerkCounter and SnatcCounter are thin wrappers that set the two
construction flags (requires_ground_touch, requires_front_rack).
"""
import logging

from workout.utilities.movement_validators import check_hip_extension, check_overhead_lockout
from workout.utilities.movement_counters import BaseCounter

logger = logging.getLogger(__name__)


class BaseBarbellCounter(BaseCounter):
    IDLE = 'idle'
    GROUNDED = 'grounded'       # full movements: bar confirmed on ground
    PULLING = 'pulling'          # bar being lifted
    AT_SHOULDER = 'at_shoulder'  # C&J only: bar confirmed in front rack
    OVERHEAD = 'overhead'        # bar overhead; checking arm lockout

    _OVERHEAD_TIMEOUT_FRAMES = 60

    def __init__(self, criteria: dict, requires_ground_touch: bool = True, requires_front_rack: bool = False):
        super().__init__(criteria)
        self.requires_ground_touch = requires_ground_touch
        self.requires_front_rack = requires_front_rack

        self.overhead_angle_threshold = criteria.get('overhead_angle_threshold', 160)
        self.hip_extension_threshold = criteria.get('hip_extension_threshold', 155)
        self.ground_tolerance_px = criteria.get('ground_tolerance_px', 60)
        self.shoulder_tolerance_px = criteria.get('shoulder_tolerance_px', 70)
        self.overhead_threshold_px = criteria.get('overhead_threshold_px', 100)

        self._phase = self.IDLE
        self._phase_frames = 0
        self._ground_confirmed = False
        self._shoulder_confirmed = False
        self._overhead_confirmed = False
        self._lockout_confirmed = False
        self._rep_log: list[dict] = []
        self._frame_counter = 0
        self._video_fps = 30.0

    def set_fps(self, fps: float) -> None:
        self._video_fps = fps if fps > 0 else 30.0

    def get_stats(self) -> dict:
        stats = super().get_stats()
        stats['rep_log'] = self._rep_log
        return stats

    # ------------------------------------------------------------------
    # Vision model interface (called by BarbellAnalyser)
    # ------------------------------------------------------------------

    def get_vision_check_needed(self, lmList) -> str | None:
        """
        Returns which barbell position to check via the vision model, or None.
        BarbellAnalyser calls this per frame and throttles the actual API calls.
        """
        if not lmList or len(lmList) < 29:
            return None

        wrist_y = min(lmList[15][2], lmList[16][2])
        shoulder_y = (lmList[11][2] + lmList[12][2]) / 2
        ankle_y = (lmList[27][2] + lmList[28][2]) / 2

        # Full movement, IDLE: check if bar is on the ground
        if self._phase == self.IDLE and self.requires_ground_touch:
            if abs(wrist_y - ankle_y) < self.ground_tolerance_px:
                return 'ground'

        # Hang movement, PULLING: check if bar accidentally touched ground (no-rep)
        if self._phase == self.PULLING and not self.requires_ground_touch:
            if abs(wrist_y - ankle_y) < self.ground_tolerance_px:
                return 'ground'

        # C&J only: check for front rack when wrist is near shoulder height
        if self._phase == self.PULLING and self.requires_front_rack and not self._shoulder_confirmed:
            if abs(wrist_y - shoulder_y) < self.shoulder_tolerance_px:
                return 'shoulder'

        # Any active phase: check for overhead when wrist is well above shoulder
        if self._phase in (self.GROUNDED, self.PULLING, self.AT_SHOULDER):
            if shoulder_y - wrist_y > self.overhead_threshold_px:
                return 'overhead'

        return None

    def update_barbell_confirmed(self, position: str) -> None:
        """Called by BarbellAnalyser after the vision model returns a YES answer."""
        if position == 'ground':
            if self._phase == self.IDLE and self.requires_ground_touch:
                logger.info("[%s] Bar confirmed on ground → GROUNDED", self.__class__.__name__)
                self._ground_confirmed = True
                self._phase = self.GROUNDED
                self._phase_frames = 0
                self.is_started = True
            elif self._phase == self.PULLING and not self.requires_ground_touch:
                logger.info("[%s] Ground contact during hang rep → no-rep", self.__class__.__name__)
                self._record_no_rep('bar touched ground during hang movement', 'T')

        elif position == 'shoulder':
            if self._phase == self.PULLING and self.requires_front_rack:
                logger.info("[%s] Front rack confirmed → AT_SHOULDER", self.__class__.__name__)
                self._shoulder_confirmed = True
                self._phase = self.AT_SHOULDER
                self._phase_frames = 0

        elif position == 'overhead':
            if self._phase in (self.GROUNDED, self.PULLING, self.AT_SHOULDER):
                logger.info("[%s] Bar overhead confirmed → OVERHEAD (phase was %s)", self.__class__.__name__, self._phase)
                self._overhead_confirmed = True
                self._phase = self.OVERHEAD
                self._phase_frames = 0

    # ------------------------------------------------------------------
    # Per-frame processing
    # ------------------------------------------------------------------

    def process(self, angle: float, lmList: list, detector, direction: int) -> dict:
        self._frame_counter += 1
        if self._phase != self.IDLE:
            self._phase_frames += 1

        if not lmList or len(lmList) < 29:
            self.previous_angle = int(angle) if angle else self.previous_angle
            return self.get_stats()

        wrist_y = min(lmList[15][2], lmList[16][2])
        shoulder_y = (lmList[11][2] + lmList[12][2]) / 2
        ankle_y = (lmList[27][2] + lmList[28][2]) / 2
        hip_y = (lmList[23][2] + lmList[24][2]) / 2

        # IDLE → PULLING for hang movements (wrists drop near hip, direction descending)
        if self._phase == self.IDLE and not self.requires_ground_touch:
            if direction == 0 and wrist_y > hip_y - 30:
                logger.debug("[%s] Hang pull started", self.__class__.__name__)
                self._phase = self.PULLING
                self._phase_frames = 0
                self.is_started = True

        # GROUNDED → PULLING when bar visibly lifted (wrist rises above ankle)
        elif self._phase == self.GROUNDED:
            if ankle_y - wrist_y > self.ground_tolerance_px * 1.5:
                logger.debug("[%s] Bar lifted → PULLING", self.__class__.__name__)
                self._phase = self.PULLING
                self._phase_frames = 0

        # OVERHEAD: validate lockout per frame; timeout if athlete takes too long
        elif self._phase == self.OVERHEAD:
            lockout_ok, lockout_reason = check_overhead_lockout(
                lmList, detector, self.overhead_angle_threshold
            )
            hip_ok, _ = check_hip_extension(lmList, detector, self.hip_extension_threshold)

            if lockout_ok and hip_ok:
                self._lockout_confirmed = True
                self._finalise_rep()
            elif self._phase_frames > self._OVERHEAD_TIMEOUT_FRAMES:
                logger.info("[%s] Overhead timeout — finalising without lockout", self.__class__.__name__)
                self._finalise_rep()
            elif wrist_y > shoulder_y + 40 and self._phase_frames > 10:
                # Wrist dropped back below shoulder — bar came down without lockout
                logger.info("[%s] Wrist descended from overhead — finalising", self.__class__.__name__)
                self._finalise_rep()

        self.previous_angle = int(angle)
        return self.get_stats()

    def reset(self):
        super().reset()
        self._reset_phase()
        self._rep_log = []
        self._frame_counter = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    # Maps failure reasons to ScoreBreakdown.no_rep_reason codes.
    # E = Did not reach full extension, T = Did not hit target/position
    _NO_REP_CODES = {
        'arms not locked out': 'E',
        'bar did not reach overhead': 'E',
        'bar did not touch ground': 'T',
        'no front rack': 'T',
        'bar touched ground during hang movement': 'T',
    }

    def _finalise_rep(self) -> None:
        reasons = []
        if self.requires_ground_touch and not self._ground_confirmed:
            reasons.append('bar did not touch ground')
        if self.requires_front_rack and not self._shoulder_confirmed:
            reasons.append('no front rack')
        if not self._overhead_confirmed:
            reasons.append('bar did not reach overhead')
        if not self._lockout_confirmed:
            reasons.append('arms not locked out')

        if not reasons:
            self.count += 1
            self.outcome = 'good rep'
            logger.info("[%s] Rep #%d counted ✓", self.__class__.__name__, self.count)
            self._rep_log.append({
                'rep_number': self.count + self.no_rep,
                'is_good_rep': True,
                'no_rep_reason': None,
                'rep_timestamp': round(self._frame_counter / self._video_fps, 2),
            })
        else:
            # Use the code for the first (primary) reason
            code = self._NO_REP_CODES.get(reasons[0], 'T')
            self._record_no_rep(reasons[0], code)

        self._reset_phase()

    def _record_no_rep(self, reason: str, code: str = 'T') -> None:
        self.no_rep += 1
        self.outcome = reason
        logger.info("[%s] No-rep #%d ✗ reason: %s", self.__class__.__name__, self.no_rep, reason)
        self._rep_log.append({
            'rep_number': self.count + self.no_rep,
            'is_good_rep': False,
            'no_rep_reason': code,
            'rep_timestamp': round(self._frame_counter / self._video_fps, 2),
        })
        self._reset_phase()

    def _reset_phase(self) -> None:
        self._phase = self.IDLE
        self._phase_frames = 0
        self._ground_confirmed = False
        self._shoulder_confirmed = False
        self._overhead_confirmed = False
        self._lockout_confirmed = False
        self.is_started = False


class CleanAndJerkCounter(BaseBarbellCounter):
    """
    Clean and jerk counter.
    hang=True → hang clean and jerk (bar must NOT touch the ground).
    hang=False → full clean and jerk (bar MUST touch the ground each rep).
    """

    def __init__(self, criteria: dict, hang: bool = False):
        super().__init__(criteria, requires_ground_touch=not hang, requires_front_rack=True)


class SnatchCounter(BaseBarbellCounter):
    """
    Snatch counter.
    hang=True → hang snatch (bar must NOT touch the ground).
    hang=False → full snatch (bar MUST touch the ground each rep).
    No front rack required — bar goes overhead in one pull.
    """

    def __init__(self, criteria: dict, hang: bool = False):
        super().__init__(criteria, requires_ground_touch=not hang, requires_front_rack=False)
