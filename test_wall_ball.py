"""
Interactive wall ball checker — mirrors the pullupChecker / toestobarChecker style.

Opens a video file and processes it frame by frame, displaying:
  - Pose skeleton
  - Detected ball (orange box + centroid)
  - Target Y line (green)
  - Rep count, no-rep count, current phase, last outcome
  - Squat angle

Console output logs every rep and no-rep as they happen.

Controls:
  Space  — pause / resume
  q / ESC — quit
  s      — step one frame while paused

Edit the constants below to point at your video.
"""
import os
import sys

import cv2

# Allow imports from the project root without Django setup.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Config ────────────────────────────────────────────────────────────────────
VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'static', 'videos', 'wallball.mp4')

# Set to the Y pixel of the target line to skip auto-detection.
MANUAL_TARGET_Y = None

# Slow the playback down — ms to wait between frames (1 = full speed, 30 = ~33 fps).
FRAME_DELAY_MS = 1
# ──────────────────────────────────────────────────────────────────────────────


def _torso_bbox(lmList):
    try:
        xs = [lmList[i][1] for i in (11, 12, 23, 24)]
        ys = [lmList[i][2] for i in (11, 12, 23, 24)]
        pad = 30
        return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
    except (IndexError, TypeError):
        return None


def draw_overlay(img, stats, phase, target_detector, tolerance, ball, angle, frame_idx, paused):
    target_y = target_detector.target_y_px
    # Always draw circle / search-region debug info
    target_detector.draw_debug(img)
    h, w = img.shape[:2]

    # Target zone — semi-transparent band showing the acceptance zone
    if target_y is not None:
        zone_top = max(target_y - tolerance, 0)
        zone_bot = min(target_y + tolerance, h - 1)

        overlay = img.copy()
        cv2.rectangle(overlay, (0, zone_top), (w, zone_bot), (0, 255, 0), -1)
        cv2.addWeighted(overlay, 0.20, img, 0.80, 0, img)

        cv2.line(img, (0, target_y), (w, target_y), (0, 255, 0), 3)

        label_y = max(zone_top - 6, 16)
        cv2.putText(img, f'Target y={target_y}  (tol ±{tolerance}px)',
                    (10, label_y), cv2.FONT_HERSHEY_PLAIN, 1.4, (0, 255, 0), 2)

    # Ball detection — orange box, centroid dot, live Y vs target
    if ball:
        cx, cy = ball['centroid']
        x1, y1, x2, y2 = ball['bbox']

        # Colour the box green if ball is inside the target zone, otherwise orange
        if target_y is not None and cy <= target_y + tolerance:
            box_colour = (0, 255, 0)
        else:
            box_colour = (0, 165, 255)

        cv2.rectangle(img, (x1, y1), (x2, y2), box_colour, 2)
        cv2.circle(img, (cx, cy), 6, box_colour, -1)

        conf = ball.get('confidence')
        conf_label = f'{conf:.2f}' if conf else 'tracked'
        cv2.putText(img, conf_label, (x1, max(y1 - 6, 12)),
                    cv2.FONT_HERSHEY_PLAIN, 1.2, box_colour, 2)

        # Show live ball Y vs target threshold
        if target_y is not None:
            needed = target_y + tolerance
            diff = cy - needed  # positive = below threshold (not there yet), negative = reached
            diff_label = f'ball y={cy}  need <={needed}  ({"OK" if diff <= 0 else f"+{diff}px short"})'
            cv2.putText(img, diff_label, (10, h - 40),
                        cv2.FONT_HERSHEY_PLAIN, 1.3,
                        (0, 255, 0) if diff <= 0 else (0, 165, 255), 2)

    # Stats panel (top-left)
    cv2.putText(img, f'Reps:    {stats["count"]}',
                (20, 60), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 220, 0), 3)
    cv2.putText(img, f'No-reps: {stats["no_rep"]}',
                (20, 110), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 0, 220), 3)
    cv2.putText(img, f'Phase:   {phase}',
                (20, 155), cv2.FONT_HERSHEY_PLAIN, 1.8, (0, 220, 220), 2)
    if angle is not None:
        cv2.putText(img, f'Angle:   {int(angle)}',
                    (20, 195), cv2.FONT_HERSHEY_PLAIN, 1.8, (220, 220, 0), 2)
    outcome = stats.get('outcome', '')
    if outcome:
        colour = (0, 220, 0) if outcome == 'good rep' else (0, 0, 220)
        cv2.putText(img, f'Outcome: {outcome}',
                    (20, 235), cv2.FONT_HERSHEY_PLAIN, 1.8, colour, 2)

    # Frame counter + pause indicator (bottom-left)
    cv2.putText(img, f'Frame {frame_idx}{"  [PAUSED]" if paused else ""}',
                (20, h - 15), cv2.FONT_HERSHEY_PLAIN, 1.4, (180, 180, 180), 2)


def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"Video not found: {VIDEO_PATH}")
        print("Update VIDEO_PATH at the top of this file.")
        sys.exit(1)

    import workout.utilities.PoseModule as pm
    from workout.utilities.movement_counters import WallBallCounter
    from workout.utilities.object_detector import GymObjectDetector
    from workout.utilities.target_detector import TargetDetector
    from workout.utilities.utils import load_movement_criteria

    criteria = load_movement_criteria()
    wall_ball_criteria = criteria.get('wall_ball', {})

    pose_detector = pm.PoseDetector()
    object_detector = GymObjectDetector(
        detect_every_n_frames=wall_ball_criteria.get('detect_every_n_frames', 3),
        confidence_threshold=wall_ball_criteria.get('ball_confidence_threshold', 0.35),
    )
    target_detector = TargetDetector(
        calibration_frames=wall_ball_criteria.get('calibration_frames', 30),
        manual_target_y=MANUAL_TARGET_Y,
    )
    counter = WallBallCounter(wall_ball_criteria)
    if MANUAL_TARGET_Y is not None:
        counter.set_target_y(MANUAL_TARGET_Y)

    video = cv2.VideoCapture(VIDEO_PATH)
    if not video.isOpened():
        print(f"Could not open video: {VIDEO_PATH}")
        sys.exit(1)

    print(f"Opened: {VIDEO_PATH}")
    print("Space = pause/resume  |  s = step frame  |  q / ESC = quit")
    print("-" * 60)

    frame_idx = 0
    paused = False
    prev_count = 0
    prev_no_rep = 0
    current_angle = None
    img = None  # last decoded frame (used while paused)

    while True:
        step = False

        key = cv2.waitKey(FRAME_DELAY_MS) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == 32:          # Space
            paused = not paused
        elif key == ord('s'):    # Step one frame
            step = True

        if paused and not step:
            if img is not None:
                cv2.imshow('Wall Ball Checker', img)
            continue

        success, img = video.read()
        if not success or img is None:
            print("\nEnd of video.")
            break

        # ── Pose detection ────────────────────────────────────────────
        img = pose_detector.getPose(img, draw=True)
        lmList = pose_detector.getPosition(img, draw=False)

        # ── Target calibration ────────────────────────────────────────
        if not target_detector.is_calibrated:
            wrist_y = lmList[15][2] if lmList and len(lmList) > 16 else None
            target_detector.update(img, frame_idx, wrist_y)
            if target_detector.is_calibrated and target_detector.target_y_px:
                counter.set_target_y(target_detector.target_y_px)
                print(f"[Frame {frame_idx}] Target calibrated at y={target_detector.target_y_px}px")

        # ── Ball detection ────────────────────────────────────────────
        torso_bbox = _torso_bbox(lmList) if lmList else None
        detection = object_detector.detect(img, frame_idx, torso_bbox)
        ball = detection.get('ball')
        counter.update_ball_position(ball)

        # ── Squat angle + counter ─────────────────────────────────────
        current_angle = None
        if lmList:
            try:
                hip, knee, ankle = pose_detector.getLandmarkIndices(lmList, is_squat=True)
                current_angle = pose_detector.getAngle(None, hip, knee, ankle)
                direction = pose_detector.checkDirectionFromAngle(
                    current_angle,
                    wall_ball_criteria.get('descending_threshold', 110),
                    wall_ball_criteria.get('ascending_threshold', 110),
                    counter.previous_angle,
                    downward_movement=True,
                )
                counter.process(current_angle, lmList, pose_detector, direction)
            except Exception as exc:
                print(f"[Frame {frame_idx}] Pose error: {exc}")

        # ── Dynamic target recalibration from ball peaks ──────────────
        peak_samples = counter._peak_samples
        if not getattr(counter, '_test_recalibrated', False) and len(peak_samples) >= 3:
            import statistics
            observed = int(statistics.median(peak_samples))
            old_target = target_detector.target_y_px
            if old_target is None or abs(observed - old_target) > 20:
                target_detector.target_y_px = observed
                counter.set_target_y(observed)
                print(f"[Frame {frame_idx}] Target recalibrated from ball peaks: "
                      f"y={old_target} → y={observed}  (samples={peak_samples[-5:]})")
            counter._test_recalibrated = True

        stats = counter.get_stats()

        # ── Console logging ───────────────────────────────────────────
        if stats['count'] > prev_count:
            print(f"[Frame {frame_idx:5d}]  GOOD REP  #{stats['count']}")
            prev_count = stats['count']
        if stats['no_rep'] > prev_no_rep:
            print(f"[Frame {frame_idx:5d}]  NO REP    #{stats['no_rep']}  — {counter.outcome}")
            prev_no_rep = stats['no_rep']

        # ── Display ───────────────────────────────────────────────────
        draw_overlay(
            img, stats, counter._phase,
            target_detector, counter.ball_height_tolerance_px,
            ball, current_angle, frame_idx, paused,
        )
        cv2.imshow('Wall Ball Checker', img)

        frame_idx += 1

    video.release()
    cv2.destroyAllWindows()

    stats = counter.get_stats()
    print("-" * 60)
    print(f"Final:  {stats['count']} reps,  {stats['no_rep']} no-reps")
    if target_detector.target_y_px:
        print(f"Target: y={target_detector.target_y_px}px")
    else:
        print("Target: not detected — set MANUAL_TARGET_Y to override")


if __name__ == '__main__':
    main()
