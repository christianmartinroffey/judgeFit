# Graph Report - .  (2026-06-12)

## Corpus Check
- 147 files · ~71,078 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 655 nodes · 997 edges · 85 communities (53 shown, 32 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 222 edges (avg confidence: 0.59)
- Token cost: 6,200 input · 1,850 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Django Admin Layer|Django Admin Layer]]
- [[_COMMUNITY_Movement Counter Framework|Movement Counter Framework]]
- [[_COMMUNITY_Frontend API Client|Frontend API Client]]
- [[_COMMUNITY_LLaVA Vision Client|LLaVA Vision Client]]
- [[_COMMUNITY_Movement Classification|Movement Classification]]
- [[_COMMUNITY_Competition UI Pages|Competition UI Pages]]
- [[_COMMUNITY_Video Judging Engine|Video Judging Engine]]
- [[_COMMUNITY_Docker Infrastructure|Docker Infrastructure]]
- [[_COMMUNITY_Wall Ball Analysis|Wall Ball Analysis]]
- [[_COMMUNITY_Pose Detection|Pose Detection]]
- [[_COMMUNITY_Angle Calibration|Angle Calibration]]
- [[_COMMUNITY_Target Line Detection|Target Line Detection]]
- [[_COMMUNITY_Django App Config|Django App Config]]
- [[_COMMUNITY_Next.js Layout|Next.js Layout]]
- [[_COMMUNITY_User Authentication|User Authentication]]
- [[_COMMUNITY_Standalone Pose Script|Standalone Pose Script]]
- [[_COMMUNITY_Agentic Judge Prototype|Agentic Judge Prototype]]
- [[_COMMUNITY_JWT Auth|JWT Auth]]
- [[_COMMUNITY_Auth API Views|Auth API Views]]
- [[_COMMUNITY_DB Migrations Init|DB Migrations Init]]
- [[_COMMUNITY_Django Management|Django Management]]
- [[_COMMUNITY_PostCSS Config|PostCSS Config]]
- [[_COMMUNITY_ESLint Config|ESLint Config]]
- [[_COMMUNITY_Next.js Config|Next.js Config]]
- [[_COMMUNITY_Migration Admin Role|Migration: Admin Role]]
- [[_COMMUNITY_Migration Athlete Role|Migration: Athlete Role]]
- [[_COMMUNITY_Migration Good Reps|Migration: Good Reps]]
- [[_COMMUNITY_Migration Score Refactor|Migration: Score Refactor]]
- [[_COMMUNITY_Migration Round Field|Migration: Round Field]]
- [[_COMMUNITY_Migration Score Status|Migration: Score Status]]
- [[_COMMUNITY_Migration Video URL|Migration: Video URL]]
- [[_COMMUNITY_Migration Score Valid|Migration: Score Valid]]
- [[_COMMUNITY_Migration Equipment|Migration: Equipment]]
- [[_COMMUNITY_Migration Score Breakdown|Migration: Score Breakdown]]
- [[_COMMUNITY_Migration Video ID|Migration: Video ID]]
- [[_COMMUNITY_ASGI Config|ASGI Config]]
- [[_COMMUNITY_Django Settings|Django Settings]]
- [[_COMMUNITY_URL Routing|URL Routing]]
- [[_COMMUNITY_WSGI Config|WSGI Config]]
- [[_COMMUNITY_Frame Processor|Frame Processor]]
- [[_COMMUNITY_Django REST Framework|Django REST Framework]]
- [[_COMMUNITY_Django SimpleJWT|Django SimpleJWT]]
- [[_COMMUNITY_CORS Headers|CORS Headers]]
- [[_COMMUNITY_yt-dlp Dependency|yt-dlp Dependency]]
- [[_COMMUNITY_NumPy Dependency|NumPy Dependency]]
- [[_COMMUNITY_JAX Dependency|JAX Dependency]]
- [[_COMMUNITY_SciPy Dependency|SciPy Dependency]]
- [[_COMMUNITY_Matplotlib Dependency|Matplotlib Dependency]]
- [[_COMMUNITY_sounddevice Dependency|sounddevice Dependency]]
- [[_COMMUNITY_Next.js Frontend|Next.js Frontend]]

## God Nodes (most connected - your core abstractions)
1. `apiFetch()` - 26 edges
2. `handleResponse()` - 24 edges
3. `getHeaders()` - 24 edges
4. `Athlete` - 21 edges
5. `WallBallAnalyser` - 20 edges
6. `WallBallCounter` - 19 edges
7. `Competition` - 18 edges
8. `WorkoutAnalyser` - 18 edges
9. `Workout` - 17 edges
10. `WorkoutComponent` - 16 edges

## Surprising Connections (you probably didn't know these)
- `SquatCounter State Machine` --semantically_similar_to--> `Wall Ball Rep State Machine`  [INFERRED] [semantically similar]
  workout/utilities/system_architecture.md → WALL_BALL_DEBUG.md
- `Full Squat Form Reference Image` --conceptually_related_to--> `SquatCounter State Machine`  [INFERRED]
  static/images/full_squat.jpg → workout/utilities/system_architecture.md
- `main()` --calls--> `load_movement_criteria()`  [INFERRED]
  test_wall_ball.py → workout/utilities/utils.py
- `main()` --calls--> `TargetDetector`  [INFERRED]
  test_wall_ball.py → workout/utilities/target_detector.py
- `main()` --calls--> `WallBallCounter`  [INFERRED]
  test_wall_ball.py → workout/utilities/movement_counters.py

## Hyperedges (group relationships)
- **Wall Ball Analysis Pipeline** — wall_ball_debug_analysevideocelery, wall_ball_debug_analyseworkoutvideo, wall_ball_debug_wallballanalyser, wall_ball_debug_wallballcounter, wall_ball_debug_gymobjectdetector, wall_ball_debug_posemodule, wall_ball_debug_targetdetector [EXTRACTED 1.00]
- **Three-Stage Target Detection (pre-scan, image-based, dynamic recalibration)** — wall_ball_debug_prescan, wall_ball_debug_targetdetector, wall_ball_debug_recalibrate [EXTRACTED 1.00]
- **JudgeFit Docker Infrastructure** — docker_compose_db, docker_compose_redis, docker_compose_web, docker_compose_celery, docker_compose_celery_beat [EXTRACTED 1.00]

## Communities (85 total, 32 thin omitted)

### Community 0 - "Django Admin Layer"
Cohesion: 0.06
Nodes (44): AffiliateAdmin, AthleteAdmin, CompetitionAdmin, CountryAdmin, Affiliate, Athlete, Competition, Country (+36 more)

### Community 1 - "Movement Counter Framework"
Cohesion: 0.05
Nodes (31): ABC, Initialize the Judge          Args:             video_source: Path to video file, BaseCounter, PullUpCounter, PushUpCounter, Movement-specific rep counters for CrossFit movements Each counter implements th, Base class for all movement counters, Process push-up rep counting          Args:             angle: Current elbow ang (+23 more)

### Community 2 - "Frontend API Client"
Cohesion: 0.08
Nodes (39): createAthlete(), createMyProfile(), deleteAthlete(), getAthlete(), getAthletes(), getMyProfile(), updateAthlete(), updateMyProfile() (+31 more)

### Community 3 - "LLaVA Vision Client"
Cohesion: 0.06
Nodes (31): Exception, LLaVAClient, LLaVAClockDetectionError, LLaVATargetDetectionError, Single-frame query — returns raw model response., Try each prompt in sequence to locate a vertical position in the frame., Ask a YES/NO question across pre-encoded JPEG frames.          Sends all frames, process_movement() (+23 more)

### Community 4 - "Movement Classification"
Cohesion: 0.06
Nodes (28): MovementClassifier, Movement Classifier for CrossFit Movements Uses rule-based detection on MediaPip, Classifies CrossFit movements based on pose landmarks     Uses a confidence buff, Classify movement based on extracted features          Returns:             str, Args:             buffer_size: Number of frames to buffer for stable classificat, Reset the classifier state, Classify the current movement based on pose landmarks          Args:, Extract relevant features for movement classification          Returns: (+20 more)

### Community 5 - "Competition UI Pages"
Cohesion: 0.07
Nodes (10): CreateCompetitionProps, Competition, BreakdownSet, Score, ScoreBreakdown, Video, checkIsAdmin(), isAdminToken() (+2 more)

### Community 6 - "Video Judging Engine"
Cohesion: 0.08
Nodes (22): Judge, main(), Main application for movement detection and counting Integrates movement classif, Main application class for judging functional movements, Draw UI elements on the frame          Args:             img: Frame image, Main application loop, Get the appropriate angle measurement for the detected movement          Args:, Process a single frame: classify movement and count reps          Args: (+14 more)

### Community 7 - "Docker Infrastructure"
Cohesion: 0.06
Nodes (37): Celery Worker Service (Docker), Celery Beat Scheduler Service (Docker), PostgreSQL DB Service (Docker), Redis Service (Docker), Web Service (Django, Docker), Full Squat Form Reference Image, Celery, Django (+29 more)

### Community 8 - "Wall Ball Analysis"
Cohesion: 0.11
Nodes (15): draw_overlay(), main(), Interactive wall ball checker — mirrors the pullupChecker / toestobarChecker sty, _torso_bbox(), GymObjectDetector, _inside_bbox(), GymObjectDetector: YOLOv8-based gym equipment detection.  Uses YOLOv8n with COCO, Reset the CSRT tracker (call between reps or at start of new set). (+7 more)

### Community 9 - "Pose Detection"
Cohesion: 0.11
Nodes (5): PoseDetector, PoseProcessor, Determines the direction of movement based on the given angle and thresholds., Determines the correct landmarks based on athlete's visibility and orientation., main()

### Community 10 - "Angle Calibration"
Cohesion: 0.13
Nodes (12): AngleCalibrator, main(), Calibration Tool for CrossFit Judge Helps determine optimal angle thresholds for, Start recording angles for a phase, Tool to help calibrate angle thresholds for movements     Records min/max angles, Calculate recommended thresholds based on recorded angles, Save calibration data to file, Args:             video_source: Path to video or camera index             moveme (+4 more)

### Community 11 - "Target Line Detection"
Cohesion: 0.11
Nodes (11): TargetDetector: Locates the wall ball target in a video frame.  The target can b, Return True if the ball centroid is at or above the target line.          Lower, Draw the detected target line on a frame (for debugging)., Draw calibration debug info directly onto ``frame`` (in-place).          During, Pick the median candidate and mark calibration as complete., Use Canny edge detection + HoughLinesP to find a prominent horizontal         ta, Use HoughCircles to detect a circular rig/wall target.          Returns the Y co, Segment common tape colours (green, yellow, red, blue) and find the         topm (+3 more)

### Community 12 - "Django App Config"
Cohesion: 0.22
Nodes (5): AppConfig, AthleteConfig, PosesConfig, UsersConfig, WorkoutConfig

### Community 13 - "Next.js Layout"
Cohesion: 0.29
Nodes (3): geistMono, geistSans, metadata

### Community 14 - "User Authentication"
Cohesion: 0.33
Nodes (4): AbstractUser, UserAdmin, CustomUserAdmin, User

### Community 16 - "Agentic Judge Prototype"
Cohesion: 0.47
Nodes (5): extract_clip(), get_agent_review(), main(), Simulates the Programmatic 'Trigger':      Extracts a short clip from a larger v, Simulates the Agentic 'Judge':     Passes the localized clip to a Video-capable

### Community 17 - "JWT Auth"
Cohesion: 0.33
Nodes (4): TokenObtainPairSerializer, TokenObtainPairView, CustomTokenObtainPairSerializer, CustomTokenObtainPairView

### Community 18 - "Auth API Views"
Cohesion: 0.47
Nodes (3): APIView, MeView, RegisterView

## Knowledge Gaps
- **175 isolated node(s):** `Simulates the Programmatic 'Trigger':      Extracts a short clip from a larger v`, `Simulates the Agentic 'Judge':     Passes the localized clip to a Video-capable`, `Interactive wall ball checker — mirrors the pullupChecker / toestobarChecker sty`, `Run administrative tasks.`, `config` (+170 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `WallBallAnalyser` connect `LLaVA Vision Client` to `Wall Ball Analysis`, `Movement Counter Framework`, `Target Line Detection`, `Movement Classification`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `WorkoutAnalyser` connect `Movement Classification` to `Movement Counter Framework`, `LLaVA Vision Client`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `WallBallCounter` connect `Movement Counter Framework` to `Wall Ball Analysis`, `LLaVA Vision Client`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Athlete` (e.g. with `AthleteSerializer` and `Meta`) actually correct?**
  _`Athlete` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `WallBallAnalyser` (e.g. with `LLaVAClient` and `LLaVAClockDetectionError`) actually correct?**
  _`WallBallAnalyser` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Simulates the Programmatic 'Trigger':      Extracts a short clip from a larger v`, `Simulates the Agentic 'Judge':     Passes the localized clip to a Video-capable`, `Interactive wall ball checker — mirrors the pullupChecker / toestobarChecker sty` to the rest of the system?**
  _175 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Django Admin Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._