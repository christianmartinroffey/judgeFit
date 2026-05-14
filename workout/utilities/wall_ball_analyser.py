"""
WallBallAnalyser: Coordinates pose detection, ball detection, and target
detection specifically for wall ball shot analysis.

Produces the same output dict shape as WorkoutAnalyser.analyse() so it
is a drop-in replacement for the Celery task.
"""
import logging
import os
import json
from datetime import datetime
from pathlib import Path

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
        debug_dir: str | None = None,
    ):
        self.video = cv2.VideoCapture(video_path)
        self.video_path = video_path
        self.expected_reps = expected_reps
        self.criteria = criteria
        self.calibration_frames = calibration_frames
        self.debug_dir = _prepare_debug_dir(debug_dir)

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
        self.counter = WallBallCounter(wall_ball_criteria)
        if target_y_px is not None:
            self.counter.set_target_y(target_y_px)

        self._frame_idx: int = 0
        self._diagnostics = _new_diagnostics(video_path, expected_reps)
        self._last_count = 0
        self._last_no_rep = 0
        self._last_phase = self.counter.get_debug_state()['phase']

        # Pass video FPS to the counter so it can convert frame numbers to seconds.
        fps = self.video.get(cv2.CAP_PROP_FPS)
        self.counter.set_fps(fps if fps > 0 else 30.0)

        # If no manual target given, run a ball-trajectory pre-scan to find the
        # target height before the main loop starts.  This is more reliable than
        # image-based detection (rig bars, ceiling lines, etc.) because the ball
        # literally travels to the target every rep.
        if target_y_px is None:
            scanned = self._pre_scan_target_from_ball()
            if scanned is not None:
                logger.info(
                    "Target detected from ball trajectory pre-scan: y=%d px", scanned
                )
                self.target_detector.target_y_px = scanned
                self.target_detector.is_calibrated = True
                self.counter.set_target_y(scanned)

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
        _pose_detected = 0
        _pose_missing = 0
        _angle_errors = 0
        _min_angle = float('inf')
        _max_angle = float('-inf')

        while True:
            success, img = self.video.read()
            if not success or img is None:
                break
            has_frames = True

            result = self._process_frame(img)

            # Accumulate diagnostics returned from _process_frame
            if result:
                if result.get('pose_missing'):
                    _pose_missing += 1
                elif result.get('angle_error'):
                    _angle_errors += 1
                else:
                    _pose_detected += 1
                    a = result.get('angle')
                    if a is not None:
                        _min_angle = min(_min_angle, a)
                        _max_angle = max(_max_angle, a)

            self._frame_idx += 1

        self.video.release()

        # Diagnostic summary — always logged so you can see what happened
        logger.info(
            "Pose diagnostics: frames_with_pose=%d  frames_no_pose=%d  "
            "angle_errors=%d  angle_range=[%.1f, %.1f]",
            _pose_detected, _pose_missing, _angle_errors,
            _min_angle if _min_angle != float('inf') else -1,
            _max_angle if _max_angle != float('-inf') else -1,
        )
        if _pose_detected == 0:
            logger.warning(
                "No pose was detected in any frame. Check that the athlete is "
                "visible and MediaPipe can track them (single person, good lighting, "
                "side-on or front-on camera angle)."
            )
        elif _min_angle > 110:
            logger.warning(
                "Squat angle never dropped below descending_threshold (110°). "
                "Minimum angle seen: %.1f°. Possible causes: "
                "(1) MediaPipe is tracking a background person who never squats, "
                "(2) camera angle makes the squat look shallow — try lowering "
                "descending_threshold in movement_analysis_criteria.json.",
                _min_angle,
            )

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
            'rep_log': stats.get('rep_log', []),
            'good_reps': total_reps,
            'attempted_reps': total_reps + total_no_reps,
            'diagnostics': self._finalise_diagnostics(),
        }

    # ------------------------------------------------------------------
    # Internal frame processing
    # ------------------------------------------------------------------

    def _pre_scan_target_from_ball(
        self,
        max_frames: int = 600,
        min_detections: int = 15,
        peak_percentile: float = 8.0,
    ) -> int | None:
        """
        Quick ball-only pass over the first ``max_frames`` frames.

        Collects every ball centroid Y detected by YOLO, then takes the
        ``peak_percentile``-th percentile of those values as the target height.

        The ball spends most of its time either in the athlete's hands (mid-frame)
        or in flight (rising and falling).  The top ~8% of Y values correspond to
        the ball's highest flight positions, which cluster around the target height.

        Args:
            max_frames:       How many frames to scan (default 600 ≈ 20 s at 30 fps).
            min_detections:   Minimum ball detections required to trust the result.
            peak_percentile:  Percentile of ball-Y distribution used as target estimate.

        Returns:
            Target Y in pixels, or None if insufficient ball data was found.
        """
        import numpy as np

        if not self.video.isOpened():
            return None

        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ball_ys: list[int] = []
        frame_idx = 0

        logger.info("Ball trajectory pre-scan: scanning up to %d frames…", max_frames)

        while frame_idx < max_frames:
            success, img = self.video.read()
            if not success or img is None:
                break

            # Ball detection only — no pose needed here.
            detection = self.object_detector.detect(img, frame_idx, athlete_torso_bbox=None)
            ball = detection.get('ball')
            if ball and ball.get('centroid'):
                ball_ys.append(ball['centroid'][1])

            frame_idx += 1

        # Reset video to start for the main analysis loop.
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self._frame_idx = 0
        self.object_detector.reset_tracker()

        if len(ball_ys) < min_detections:
            logger.warning(
                "Ball trajectory pre-scan: only %d detections in %d frames "
                "(need %d) — falling back to image-based target detection.",
                len(ball_ys), frame_idx, min_detections,
            )
            return None

        target_y = int(np.percentile(ball_ys, peak_percentile))
        logger.info(
            "Ball trajectory pre-scan complete: %d detections, "
            "ball Y range [%d, %d], target estimate y=%d (p%.0f)",
            len(ball_ys), min(ball_ys), max(ball_ys), target_y, peak_percentile,
        )
        return target_y

    def _process_frame(self, img) -> dict:
        """Process one frame. Returns a small diagnostic dict for the analyse() summary."""
        raw_img = img.copy() if self.debug_dir else None
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
        ball = detection.get('ball')
        self.counter.update_ball_position(ball)

        # 4. Squat angle + counter
        if not lmList:
            self._record_frame_diagnostics(None, None, detection, None)
            return {'pose_missing': True}

        try:
            hip, knee, ankle = self.pose_detector.getLandmarkIndices(lmList, is_squat=True)
            angle = self.pose_detector.getAngle(None, hip, knee, ankle)
        except Exception as exc:
            logger.debug("Angle computation failed on frame %d: %s", self._frame_idx, exc)
            self._record_frame_diagnostics(lmList, None, detection, athlete_torso_bbox)
            return {'angle_error': True}

        wall_ball_criteria = self.criteria.get('wall_ball', {})
        direction = self.pose_detector.checkDirectionFromAngle(
            angle,
            wall_ball_criteria.get('descending_threshold', 110),
            wall_ball_criteria.get('ascending_threshold', 110),
            self.counter.previous_angle,
            downward_movement=True,
        )

        self.counter.process(angle, lmList, self.pose_detector, direction)
        self._record_frame_diagnostics(lmList, angle, detection, athlete_torso_bbox)
        self._maybe_save_event_snapshot(raw_img, angle, ball, athlete_torso_bbox)

        # 5. Dynamic target recalibration from observed ball peaks.
        self._maybe_recalibrate_target()

        return {'angle': angle}

    def _record_frame_diagnostics(
        self,
        lmList: list | None,
        angle: float | None,
        detection: dict,
        athlete_torso_bbox: tuple | None,
    ) -> None:
        """Collect cheap per-frame metrics for post-run debugging."""
        diag = self._diagnostics
        diag['frames_processed'] += 1

        ball = detection.get('ball')
        source = detection.get('source', 'none')
        diag['ball_detection_sources'][source] = diag['ball_detection_sources'].get(source, 0) + 1
        if ball:
            diag['frames_with_ball'] += 1
        else:
            diag['frames_without_ball'] += 1

        if lmList:
            diag['frames_with_pose'] += 1
        else:
            diag['frames_without_pose'] += 1

        if angle is not None:
            diag['angle_min'] = angle if diag['angle_min'] is None else min(diag['angle_min'], angle)
            diag['angle_max'] = angle if diag['angle_max'] is None else max(diag['angle_max'], angle)

        state = self.counter.get_debug_state()
        phase = state['phase']
        diag['phase_frame_counts'][phase] = diag['phase_frame_counts'].get(phase, 0) + 1
        if phase != self._last_phase:
            diag['phase_transitions'].append({
                'frame': self._frame_idx,
                'from': self._last_phase,
                'to': phase,
                'angle': round(angle, 2) if angle is not None else None,
                'ball_y': state['ball_y'],
                'target_y_px': state['target_y_px'],
            })
            self._last_phase = phase

        sample_every = int(self.criteria.get('wall_ball', {}).get('debug_sample_every_n_frames', 30))
        if sample_every > 0 and self._frame_idx % sample_every == 0:
            diag['frame_samples'].append({
                'frame': self._frame_idx,
                'angle': round(angle, 2) if angle is not None else None,
                'ball': ball,
                'ball_source': source,
                'torso_bbox': athlete_torso_bbox,
                **state,
            })

    def _maybe_save_event_snapshot(
        self,
        raw_img,
        angle: float | None,
        ball: dict | None,
        athlete_torso_bbox: tuple | None,
    ) -> None:
        """Save timestamped overlay images when reps/no-reps are recorded."""
        if raw_img is None or not self.debug_dir:
            self._last_count = self.counter.count
            self._last_no_rep = self.counter.no_rep
            return

        event = None
        if self.counter.count > self._last_count:
            event = f"good_rep_{self.counter.count:03d}"
        elif self.counter.no_rep > self._last_no_rep:
            event = f"no_rep_{self.counter.no_rep:03d}"

        self._last_count = self.counter.count
        self._last_no_rep = self.counter.no_rep

        if event is None:
            return

        overlay = raw_img.copy()
        _draw_debug_overlay(
            overlay,
            frame_idx=self._frame_idx,
            angle=angle,
            ball=ball,
            target_y_px=self.target_detector.target_y_px,
            tolerance=self.counter.ball_height_tolerance_px,
            torso_bbox=athlete_torso_bbox,
            state=self.counter.get_debug_state(),
        )
        path = self.debug_dir / f"{self._frame_idx:06d}_{event}.jpg"
        cv2.imwrite(str(path), overlay)
        self._diagnostics['artifacts'].append(str(path))

    def _finalise_diagnostics(self) -> dict:
        self._diagnostics['target_y_px'] = self.target_detector.target_y_px
        self._diagnostics['rep_log'] = self.counter.get_stats().get('rep_log', [])
        if self.debug_dir:
            path = self.debug_dir / 'wall_ball_diagnostics.json'
            path.write_text(json.dumps(self._diagnostics, indent=2), encoding='utf-8')
            self._diagnostics['artifacts'].append(str(path))
            self._diagnostics['debug_dir'] = str(self.debug_dir)
        return self._diagnostics

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
    debug_dir: str | None = None,
) -> dict:
    """
    Download/locate a video and run wall ball analysis.

    Args:
        video_url:      YouTube URL or local file path.
        expected_reps:  Target rep count for validity check.
        target_y_px:    Optional manual target Y coordinate (skips auto-detect).
        debug_dir:      Optional directory for diagnostics JSON and event snapshots.

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
            debug_dir=debug_dir,
        )
        return analyser.analyse()
    finally:
        if cleanup and os.path.exists(video_path):
            os.unlink(video_path)


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

def _prepare_debug_dir(debug_dir: str | None) -> Path | None:
    """Create a diagnostics directory when explicitly requested."""
    configured = debug_dir or os.getenv('JUDGEFIT_WALLBALL_DEBUG_DIR')
    if not configured:
        return None

    path = Path(configured) / datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
    path.mkdir(parents=True, exist_ok=True)
    return path


def _new_diagnostics(video_path: str, expected_reps: int | None) -> dict:
    return {
        'video_path': video_path,
        'expected_reps': expected_reps,
        'frames_processed': 0,
        'frames_with_pose': 0,
        'frames_without_pose': 0,
        'frames_with_ball': 0,
        'frames_without_ball': 0,
        'ball_detection_sources': {},
        'angle_min': None,
        'angle_max': None,
        'target_y_px': None,
        'phase_frame_counts': {},
        'phase_transitions': [],
        'frame_samples': [],
        'rep_log': [],
        'artifacts': [],
    }


def _draw_debug_overlay(
    img,
    frame_idx: int,
    angle: float | None,
    ball: dict | None,
    target_y_px: int | None,
    tolerance: int,
    torso_bbox: tuple | None,
    state: dict,
) -> None:
    """Draw a compact event snapshot overlay for audit/debugging."""
    h, w = img.shape[:2]

    if target_y_px is not None:
        zone_top = max(target_y_px - tolerance, 0)
        zone_bot = min(target_y_px + tolerance, h - 1)
        cv2.rectangle(img, (0, zone_top), (w, zone_bot), (0, 80, 0), -1)
        cv2.line(img, (0, target_y_px), (w, target_y_px), (0, 255, 0), 2)

    if torso_bbox:
        x1, y1, x2, y2 = [int(v) for v in torso_bbox]
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)

    if ball:
        x1, y1, x2, y2 = ball['bbox']
        cx, cy = ball['centroid']
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 165, 255), 2)
        cv2.circle(img, (cx, cy), 5, (0, 165, 255), -1)

    lines = [
        f"frame={frame_idx}",
        f"phase={state['phase']}",
        f"good={state['count']} no_rep={state['no_rep']}",
        f"angle={angle:.1f}" if angle is not None else "angle=None",
        f"target_y={target_y_px}",
        f"ball_y={state['ball_y']}",
        f"outcome={state['outcome']}",
    ]
    for i, text in enumerate(lines):
        y = 28 + (i * 24)
        cv2.putText(img, text, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4)
        cv2.putText(img, text, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

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
