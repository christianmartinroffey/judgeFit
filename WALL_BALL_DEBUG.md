# Wall Ball Analysis — Debug Reference

## Pipeline Overview

```
Frontend (video URL)
  → Celery task: workout/tasks.py :: analyse_video()
    → workout/utilities/workout_analyser.py :: analyse_workout_video()
      → detects all components are wall_ball → dispatches to WallBallAnalyser
        → workout/utilities/wall_ball_analyser.py :: WallBallAnalyser
          ├── PoseModule (MediaPipe) — squat angle per frame
          ├── GymObjectDetector (YOLOv8) — ball position per frame
          ├── TargetDetector — calibrates target Y from first 30 frames
          └── WallBallCounter — state machine, counts reps
```

---

## Key Files

| File | Purpose |
|------|---------|
| `workout/tasks.py` | Celery task entry point |
| `workout/utilities/workout_analyser.py` | Routes wall ball workouts to WallBallAnalyser |
| `workout/utilities/wall_ball_analyser.py` | Orchestrates per-frame pipeline |
| `workout/utilities/movement_counters.py` | `WallBallCounter` — state machine + rep logic |
| `workout/utilities/target_detector.py` | Auto-detects target Y from video frames |
| `workout/utilities/object_detector.py` | YOLOv8 ball detection + CSRT tracking |
| `static/config/movement_analysis_criteria.json` | All thresholds (edit here first when debugging) |
| `test_wall_ball.py` | Interactive local video viewer |

---

## State Machine

A rep cycles through five phases in order:

```
IDLE → SQUATTING → THROWING → BALL_AT_TARGET → CATCHING → (rep counted) → IDLE
```

### IDLE
- Waiting for the athlete to begin squatting.
- Transition out: `direction == 0` (descending) AND `angle < descending_threshold (110°)`.

### SQUATTING
- Tracking squat depth.
- `_squat_achieved = True` when `angle <= end_point (65°)`.
- Transition to THROWING when: ball detected moving upward (`_ball_moving_up()`)
  OR athlete fully stands (`angle >= start_point 165°`) without ball detection.
- No-rep logged here if: athlete stands up fully without squat depth achieved.

### THROWING
- Tracking ball trajectory upward.
- `_throw_frame_count` increments each frame ball is detected moving up.
- `_throw_min_y` tracks the lowest Y (highest screen position) the ball reaches — used for
  the target check even if YOLO misses the exact apex frame.
- Transition to BALL_AT_TARGET when: `_throw_min_y <= target_y_px + ball_height_tolerance_px (40px)`.
- No-rep if: ball starts descending AND `_throw_min_y > target_y_px + tolerance` (ball never reached zone).
- **Timeouts:**
  - If ball thrown (`_throw_frame_count >= 3`) but then lost for 20+ frames → advance to BALL_AT_TARGET optimistically.
  - If stuck for 120+ frames with no resolution → silent reset to IDLE.

### BALL_AT_TARGET
- Ball has been confirmed in the target zone. Waiting for it to start descending.
- Transition to CATCHING when: `ball_y is not None AND NOT _ball_moving_up()`.
- **Timeouts:**
  - Ball lost for 20+ frames → advance to CATCHING.
  - Stuck for 60+ frames → advance to CATCHING.

### CATCHING
- Waiting for the ball to return to the athlete's hands.
- **Catch is detected (in priority order):**
  1. `ball_y >= wrist_y` — ball has descended to wrist level (primary, most accurate).
  2. `ball_y > target_y_px + (2 × tolerance)` — ball dropped meaningful distance from target.
  3. `ball_y >= shoulder_y` — fallback.
- On catch: `_finalise_rep()` — counts good rep if both `_squat_achieved` AND `_ball_at_target_achieved`.
- **Timeouts:**
  - Ball invisible for 20+ frames AND both criteria met → count as good rep (ball held by athlete).
  - Ball invisible for 20+ frames AND criteria NOT met → no-rep "ball dropped".
  - Stuck for 90+ frames → `_finalise_rep()` regardless.

> **Most common stuck point:** CATCHING used to have no timeout and used `ball_y >= shoulder_y`
> as its only catch signal. Wall balls are caught above the shoulder joint, so this never fired.
> The machine silently hung here for all reps after the first 1-2.

---

## Valid Rep Criteria

Both of these must be true for a rep to count:

| Criterion | How it's checked |
|-----------|-----------------|
| **Squat depth** | Hip-knee-ankle angle ≤ `end_point` (65°) at any point during SQUATTING |
| **Ball at target** | `_throw_min_y ≤ target_y_px + ball_height_tolerance_px` at any point during THROWING |

---

## Configuration — `static/config/movement_analysis_criteria.json`

```json
"wall_ball": {
    "descending_threshold": 110,      // angle below which descent is detected
    "ascending_threshold": 110,       // angle above which ascent is detected
    "start_point": 165,               // angle = fully standing (throws transition trigger)
    "end_point": 65,                  // angle = squat deep enough for valid rep
    "ball_height_tolerance_px": 40,   // how many px below target_y still counts as "at target"
    "min_throw_frames": 3,            // min frames ball must be seen moving up to count as a throw
    "ball_confidence_threshold": 0.35,// YOLO minimum confidence to accept a ball detection
    "calibration_frames": 30,         // frames used for target auto-detection
    "detect_every_n_frames": 3        // run YOLO every N frames (CSRT bridges between)
}
```

### What to adjust when reps are wrong

| Symptom | Parameter to change |
|---------|-------------------|
| Good squats marked "not deep enough" | Increase `end_point` (e.g. 70–80) |
| Shallow squats counting as valid | Decrease `end_point` (e.g. 55–60) |
| Ball clearly reaching target but "didn't reach target" | Increase `ball_height_tolerance_px` (try 60–80) |
| Ball nowhere near target but counting | Decrease `ball_height_tolerance_px` |
| State machine not detecting squats at all | Decrease `descending_threshold` (e.g. 100) |

---

## Target Detection

Target detection runs in three stages. Each stage is tried in order; whichever succeeds first wins.

### Stage 1 — Ball trajectory pre-scan (primary, most reliable)

Before the main analysis loop starts, `WallBallAnalyser._pre_scan_target_from_ball()` scans the
first 600 frames (~20 s at 30 fps) using YOLO ball detection only (no pose needed). It collects
every ball centroid Y, then takes the **8th percentile** of those values as the target height.

**Why this works:** The ball spends most of its time at mid-frame (held, squatting) or lower
(rising and descending). Only at the apex of each throw does it reach the actual target. The bottom
~8% of Y values (smallest Y = highest on screen) cluster tightly around the target height.

Log lines to look for:
```
Ball trajectory pre-scan: scanning up to 600 frames…
Ball trajectory pre-scan complete: 87 detections, ball Y range [91, 312], target estimate y=97 (p8)
Target detected from ball trajectory pre-scan: y=97 px
```

Requires at least **15 ball detections** in the scan window to trust the result. If YOLO doesn't
find the ball enough (e.g. first 600 frames are pre-workout setup with no throws), it logs a warning
and falls through to Stage 2.

### Stage 2 — Image-based detection (fallback)

`TargetDetector` runs on the first 30 frames and tries three methods in order:
1. **Circle detection** (HoughCircles) — for round disc targets on a rig.
2. **Horizontal line detection** (Canny + HoughLinesP) — for tape lines on a wall.
3. **Colour segmentation** — for coloured targets (green, yellow, red, blue).

Commits when 5 consistent candidates are found OR after 30 frames.

**Common failure — locks onto a rig bar:** The first 30 frames often show no throwing. Horizontal
rig bars and ceiling edges register as strong lines and can win over the actual target disc.
If `Target calibrated at y=NNN` appears in the logs very early (frames 0–5), and the pre-scan
didn't run (no ball detected), the detector locked onto background.

**How to identify:** Run `test_wall_ball.py` — a green band is drawn at the detected target zone.
If the band sits on a rig bar rather than the actual target, it's miscalibrated.

### Stage 3 — Dynamic recalibration during analysis (correction)

After 3 throws have been observed during the main loop, `WallBallAnalyser._maybe_recalibrate_target()`
recalculates `target_y_px` from the median ball peak across those throws. This corrects a bad
Stage 2 result that slipped through. Fires once per video.

Log line to look for:
```
Recalibrating target from ball peaks: y=160 → y=94  (samples=[91, 94, 97])
```

### Manual target override

Use this when all three automatic stages are failing and you know the correct value.

**For local testing (`test_wall_ball.py`):**
```python
MANUAL_TARGET_Y = 94   # set to None for auto-detection
```

**For YouTube submission flow (`workout/utilities/workout_analyser.py` ~line 400):**
```python
_MANUAL_TARGET_Y = 94   # set to None to use automatic detection
analyser = WallBallAnalyser(
    video_path,
    ...
    target_y_px=_MANUAL_TARGET_Y,
)
```

**How to find the correct Y value:**
1. Run `test_wall_ball.py` on a local copy of the video.
2. Press Space to pause when the ball is at the target.
3. Read the `ball y=NNN` value from the bottom of the frame — that is your target Y.

---

## Ball Detection

**YOLO model:** `static/models/yolov8n.pt` — COCO class 32 ("sports ball").

**CSRT tracker:** Bridges frames between YOLO runs. If unavailable (OpenCV build without
`cv2.legacy`), YOLO runs every `detect_every_n_frames` (3) frames only with no inter-frame
tracking. Log warning: `CSRT tracker unavailable; falling back to YOLO-only mode.`

**False positive filtering:** Detections whose centroid falls inside the athlete's torso bounding
box (derived from shoulder/hip landmarks) are discarded.

**`_throw_min_y` tracking:** Rather than checking if the ball is at target height on a single
YOLO frame (which may miss the apex), the counter tracks the minimum Y seen across the entire
THROWING phase. This means YOLO only needs to detect the ball near the target once — not on
exactly the right frame.

---

## YOLO Confidence Threshold

Default: `0.35`. If ball is not being detected at all, lower to `0.25`. If getting false
positives (e.g. athlete's head detected as ball), raise to `0.45–0.50`.

Set in `static/config/movement_analysis_criteria.json` under `ball_confidence_threshold`,
or pass directly when constructing `GymObjectDetector`.

---

## Logging Reference

All key events log at INFO level and appear in the Celery worker output.

```
# Target calibration
Target calibrated at y=94 px
Target set at y=94 px after 12 frames
Recalibrating target from ball peaks: y=171 → y=94  (samples=[91, 94, 97])

# Per-rep state machine (INFO)
Rep attempt started — descending (angle=165.2)
Squat depth achieved (angle=62.1 <= end_point=65)
Rep #1 counted  ✓  (squat_depth=OK, ball_at_target=OK)
No-rep #1  ✗  reason: ball didn't reach target  (squat_depth=OK, ball_at_target=FAIL)
No-rep #2  ✗  reason: not deep enough  (squat_depth=FAIL, ball_at_target=OK)
Ball lost during catch; squat+target criteria met — counting as good rep
CATCHING timeout after 90 frames (wrist_y=210 ball_y=180) — finalising rep

# Phase transitions (DEBUG — only visible with --loglevel=debug)
→ THROWING (ball moving up, squat_achieved=True, angle=148.3)
Ball reached target zone: peak_y=97 target_y=94
→ CATCHING (ball descending from target, ball_y=130)
Catch detected: ball_y=215 wrist_y=220 shoulder_y=280
```

To see DEBUG logs, start Celery with:
```bash
celery -A judgeFit worker --loglevel=debug
```

---

## Running the Interactive Test Script

```bash
python test_wall_ball.py
```

Edit constants at the top of the file:
```python
VIDEO_PATH = 'static/videos/wallball.mp4'   # path to local video
MANUAL_TARGET_Y = None                       # or e.g. 94
FRAME_DELAY_MS = 1                           # 1 = full speed, 30 = ~33fps
```

**Controls:**
- `Space` — pause / resume
- `s` — step one frame while paused
- `q` / `ESC` — quit

**On-screen display:**
- Green band = target acceptance zone (`target_y ± tolerance`)
- Green circle outline = detected target disc (after calibration)
- Orange/green box = ball detection (turns green when inside target zone)
- Bottom bar = `ball y=NNN  need <=NNN  (+NNpx short)` or `OK`
- Top-left panel = reps, no-reps, current phase, squat angle, last outcome

**During calibration (first 30 frames):**
- Cyan dashed line = search region boundary (top 60% of frame)
- Blue circles = all circle candidates found this frame
- Magenta circle = best candidate being tracked

---

## Celery Task Flow

`workout/tasks.py`:
1. Sets `score.status = PROCESSING`
2. Loads `workout_components` from `score.video.workout.components`
3. Calls `analyse_workout_video(video_url, workout_components, workout_type)`
4. Writes result back to `score`: `total_reps`, `no_reps`, `is_valid`, `is_scaled`, `movement_breakdown`
5. Sets `score.status = COMPLETE` or `FAILED`

The `movement_breakdown` field contains a per-set breakdown list, e.g.:
```json
[{
    "round": 1,
    "sequence": 1,
    "movement": "wall_ball",
    "reps": 5,
    "no_reps": 0,
    "expected_reps": 10,
    "advance_reason": "video_end"
}]
```

---

## Common Symptoms and Fixes

### "0 reps, 0 no-reps logged"
State machine stuck in THROWING — ball never detected or YOLO-only mode with no ball
detection at all. Check:
- Is `static/models/yolov8n.pt` present?
- Is `ball_confidence_threshold` too high?
- Run test script and look for orange ball box on screen.

### "All reps are no-reps: ball didn't reach target"
Target is miscalibrated (locked onto rig bar instead of disc target).
Fix: run test script, check where green band is. Set `MANUAL_TARGET_Y` or
increase `ball_height_tolerance_px`.

### "Only 1–2 reps counted out of 5+"
State machine was getting stuck in CATCHING — `_CATCHING_TIMEOUT_FRAMES (90)` is the
safety net that now forces it out. If this is still happening, check the Celery log for
`CATCHING timeout` messages — if you see them for every rep, the wrist detection isn't
working and the timeout is carrying all the reps. Run test script to inspect pose landmarks.

### "No-rep: not deep enough" on good squats
Squat angle not reaching `end_point (65°)`. Possible causes:
- Camera angle makes pose estimation inaccurate (side-on is best).
- Athlete genuinely not hitting depth — check angle in test script (`Angle: NNN`).
- Raise `end_point` to 70–75 if camera angle is not ideal.

### "Target calibrated after 2 frames" in logs
Locked on to a background feature very early. Dynamic recalibration will correct this
after 3 throws, but if the miscalibrated target is causing no-reps before that point,
set `MANUAL_TARGET_Y` for the submission flow.
