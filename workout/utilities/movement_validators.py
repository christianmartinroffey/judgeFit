"""
Stateless MediaPipe joint validators.

Each function takes (lmList, detector) and returns (passed: bool, reason: str).
Usable by any movement counter — no barbell or equipment assumption.
"""


def _visible_side(lmList, left_idx, right_idx) -> str:
    l_vis = lmList[left_idx][3] if len(lmList[left_idx]) > 3 else 0
    r_vis = lmList[right_idx][3] if len(lmList[right_idx]) > 3 else 0
    return 'left' if l_vis >= r_vis else 'right'


def check_overhead_lockout(lmList, detector, threshold: float = 160.0) -> tuple[bool, str]:
    """Arm fully extended overhead (shoulder-elbow-wrist >= threshold)."""
    side = _visible_side(lmList, 11, 12)
    shoulder, elbow, wrist = (11, 13, 15) if side == 'left' else (12, 14, 16)
    angle = detector.getAngle(None, shoulder, elbow, wrist)
    if angle >= threshold:
        return True, ''
    return False, f'arm not locked out ({angle:.0f}° < {threshold:.0f}°)'


def check_hip_extension(lmList, detector, threshold: float = 155.0) -> tuple[bool, str]:
    """Athlete standing upright (hip-knee-ankle >= threshold)."""
    side = _visible_side(lmList, 23, 24)
    hip, knee, ankle = (23, 25, 27) if side == 'left' else (24, 26, 28)
    angle = detector.getAngle(None, hip, knee, ankle)
    if angle >= threshold:
        return True, ''
    return False, f'not standing ({angle:.0f}° < {threshold:.0f}°)'


def check_squat_depth(lmList, detector, threshold: float = 65.0) -> tuple[bool, str]:
    """Hip crease below knee (hip-knee-ankle <= threshold)."""
    side = _visible_side(lmList, 23, 24)
    hip, knee, ankle = (23, 25, 27) if side == 'left' else (24, 26, 28)
    angle = detector.getAngle(None, hip, knee, ankle)
    if angle <= threshold:
        return True, ''
    return False, f'not deep enough ({angle:.0f}° > {threshold:.0f}°)'


def check_elbow_lockout(lmList, detector, threshold: float = 160.0) -> tuple[bool, str]:
    """Elbow fully extended (shoulder-elbow-wrist >= threshold). For push-ups, press movements."""
    side = _visible_side(lmList, 11, 12)
    shoulder, elbow, wrist = (11, 13, 15) if side == 'left' else (12, 14, 16)
    angle = detector.getAngle(None, shoulder, elbow, wrist)
    if angle >= threshold:
        return True, ''
    return False, f'elbow not locked out ({angle:.0f}° < {threshold:.0f}°)'
