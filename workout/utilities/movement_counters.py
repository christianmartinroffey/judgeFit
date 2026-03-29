"""
Movement-specific rep counters for CrossFit movements
Each counter implements the specific rules for counting valid reps
"""
from abc import ABC, abstractmethod


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
