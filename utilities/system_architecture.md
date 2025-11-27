┌─────────────────────────────────────────────────────────────────┐
│                         VIDEO INPUT                              │
│                    (Camera or Video File)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POSE DETECTION                                │
│                   (MediaPipe + PoseModule)                       │
│  • Extracts 33 body landmarks per frame                          │
│  • Calculates joint angles                                       │
│  • Tracks body position in 3D space                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              MOVEMENT CLASSIFICATION                             │
│                (movement_classifier.py)                          │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Feature Extraction:                                  │       │
│  │  • Body orientation (vertical vs horizontal)          │       │
│  │  • Arm position (overhead, on ground, etc)            │       │
│  │  • Hip-shoulder-ankle alignment                       │       │
│  │  • Leg movement range                                 │       │
│  └──────────────────────────────────────────────────────┘       │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Rule-Based Classification:                           │       │
│  │  • Squat: Vertical body + hip movement                │       │
│  │  • Push-up: Horizontal body + hands on ground         │       │
│  │  • Pull-up: Hanging + minimal leg movement            │       │
│  │  • Toes-to-Bar: Hanging + large leg movement          │       │
│  └──────────────────────────────────────────────────────┘       │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Confidence Buffer (15 frames):                       │       │
│  │  • Prevents flickering between movements              │       │
│  │  • Requires 60% confidence to classify                │       │
│  │  • Needs 20 stable frames to switch                   │       │
│  └──────────────────────────────────────────────────────┘       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                REP COUNTING ROUTER                               │
│              (CrossFitJudge.process_frame)                       │
│  • Routes to appropriate counter based on movement               │
│  • Extracts relevant joint angles for that movement              │
│  • Determines movement direction (up/down)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
┌──────────────────────┐      ┌──────────────────────┐
│   MOVEMENT-SPECIFIC  │      │   MOVEMENT-SPECIFIC  │
│      COUNTER         │      │      COUNTER         │
│  (movement_counters) │ ...  │  (movement_counters) │
└──────────────────────┘      └──────────────────────┘

Example: SquatCounter
┌─────────────────────────────────────────────────────────────────┐
│                     SQUAT COUNTER LOGIC                          │
│                                                                   │
│  State Machine:                                                   │
│  ┌──────────┐     Angle < 110°      ┌──────────────┐            │
│  │  Start   │ ────────────────────► │  Descending  │            │
│  └──────────┘                        └──────┬───────┘            │
│                                             │                    │
│                                 Angle ≤ 60° │                    │
│                                             ▼                    │
│                                      ┌──────────────┐            │
│                                      │  Full Depth  │            │
│                                      └──────┬───────┘            │
│                                             │                    │
│                                             │ Direction = Up     │
│                                             ▼                    │
│                                      ┌──────────────┐            │
│                                      │  Ascending   │            │
│                                      └──────┬───────┘            │
│                                             │                    │
│                                Angle ≥ 165° │                    │
│                                             ▼                    │
│                                    ┌─────────────────┐           │
│                                    │ Full Extension  │           │
│                                    └────────┬────────┘           │
│                                             │                    │
│                          Both Depth + Ext   │                    │
│                                             ▼                    │
│                                       ┌──────────┐               │
│                                       │ GOOD REP │               │
│                                       └──────────┘               │
│                                                                   │
│  Failure Cases:                                                   │
│  • Not deep enough: Angle never reaches 60°                      │
│  • No full extension: Angle never reaches 165°                   │
│  • Early descent: Going back down before full extension          │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT                                    │
│  • Good Rep Count                                                │
│  • No-Rep Count                                                  │
│  • Outcome (reason for no-rep)                                   │
│  • Visual Feedback (angle overlay, text)                         │
└─────────────────────────────────────────────────────────────────┘