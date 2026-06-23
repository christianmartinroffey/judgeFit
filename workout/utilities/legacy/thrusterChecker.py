"""
Thruster movement analysis.

A thruster is a front squat driven directly into an overhead press.
A valid rep requires:
  1. Full squat depth  — hip-knee-ankle angle <= end_point (65°)
  2. Overhead lockout  — at the top:
       a. Arm angle (shoulder-elbow-wrist) >= overhead_angle_threshold (160°)
       b. Wrist, elbow, shoulder, hip, knee x-coordinates within alignment_tolerance (50 px)
          confirming the barbell is directly overhead and landmarks are vertically stacked.
"""
import os

import cv2
import workout.utilities.PoseModule as pm
from workout.utilities.utils import load_movement_criteria, download_youtube_video

criteria = load_movement_criteria()
thruster_criteria = criteria.get('thruster', {})

descending_threshold = thruster_criteria.get('descending_threshold', 110)
ascending_threshold = thruster_criteria.get('ascending_threshold', 110)
start_point = thruster_criteria.get('start_point', 165)
end_point = thruster_criteria.get('end_point', 65)
overhead_angle_threshold = thruster_criteria.get('overhead_angle_threshold', 160)
alignment_tolerance = thruster_criteria.get('alignment_tolerance', 50)

detector = pm.PoseDetector()


def _pick_side(lmList):
    """Return (wrist, elbow, shoulder, hip, knee) indices for the more visible side."""
    if lmList[23][3] > lmList[24][3]:
        return 15, 13, 11, 23, 25  # left side
    return 16, 14, 12, 24, 26      # right side


def _check_overhead(lmList):
    """
    Return True when the athlete has a valid overhead position:
      - Arm (shoulder-elbow-wrist) angle >= overhead_angle_threshold
      - x-spread of wrist, elbow, shoulder, hip, knee <= alignment_tolerance
    """
    wrist, elbow, shoulder, hip, knee = _pick_side(lmList)

    arm_angle = detector.getAngle(None, shoulder, elbow, wrist)
    if arm_angle < overhead_angle_threshold:
        return False

    xs = [lmList[i][1] for i in (wrist, elbow, shoulder, hip, knee)]
    return (max(xs) - min(xs)) <= alignment_tolerance


def process_movement(video_url):
    stream_url = download_youtube_video(video_url)
    video = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)

    if not video.isOpened():
        raise Exception('Could not open video stream')

    count = 0
    no_rep = 0
    is_valid = True
    is_scaled = False

    direction = None
    is_started = False
    full_depth = False
    overhead_lockout = False
    outcome = ''
    previous_angle = 0
    video_exists = False

    while True:
        video_exists = True
        success, img = video.read()
        if not success or img is None:
            break

        img = detector.getPose(img, draw=False)
        lmList = detector.getPosition(img, draw=False)

        if len(lmList) == 0:
            continue

        # Primary angle: hip-knee-ankle (drives squat phase)
        hip_idx, knee_idx, ankle_idx = detector.getLandmarkIndices(lmList, is_squat=True)
        angle = detector.getAngle(img, hip_idx, knee_idx, ankle_idx)

        direction = detector.checkDirectionFromAngle(
            angle,
            descending_threshold,
            ascending_threshold,
            previous_angle,
            downward_movement=True,
        )

        # Descending — going into the squat
        if direction == 0 and angle < descending_threshold:
            if not is_started:
                is_started = True
                full_depth = False
                overhead_lockout = False
                outcome = ''

            if angle <= end_point:
                full_depth = True

        # Ascending — driving up and pressing overhead
        elif direction == 1 and is_started:
            if angle >= start_point:
                if _check_overhead(lmList):
                    overhead_lockout = True

            # Had depth but no lockout — heading back down
            if full_depth and not overhead_lockout:
                if angle < previous_angle:
                    no_rep += 1
                    outcome = 'no overhead lockout'
                    is_started = False
                    full_depth = False

            # Locked out but not deep enough
            elif not full_depth and overhead_lockout:
                if angle > previous_angle:
                    no_rep += 1
                    outcome = 'not deep enough'
                    is_started = False
                    overhead_lockout = False

        # Valid rep
        if full_depth and overhead_lockout:
            count += 1
            outcome = 'good rep'
            is_started = False
            full_depth = False
            overhead_lockout = False

        previous_angle = int(angle)

        print(
            int(angle), direction, outcome,
            'overhead_lockout', overhead_lockout,
            'full_depth', full_depth,
            'reps', count,
            'no_reps', no_rep,
        )

    os.unlink(stream_url)

    return {
        'total_reps': count,
        'no_reps': no_rep,
        'is_valid': video_exists,
        'is_scaled': is_scaled,
    }
