Judge - Movement Detection & Counting
An automated CrossFit movement detection and rep counting system using computer vision and pose estimation.
Features

Automatic Movement Detection: Identifies squat, push-up, pull-up, and toes-to-bar movements
Real-time Rep Counting: Counts valid reps based on CrossFit competition standards
No-Rep Detection: Identifies and counts invalid reps with specific reasons
Modular Architecture: Easy to add new movements or modify counting rules

Architecture
Video Input
    ↓
Pose Detection (MediaPipe)
    ↓
Movement Classification (Rule-based)
    ↓
Movement-Specific Counting Logic
    ↓
Rep Count + No-Rep Reasons
Installation

Install required packages:

bashpip install opencv-python mediapipe numpy

Ensure you have your existing modules:

PoseModule.py - Your pose detection module
utilities/utils.py - Contains load_movement_criteria()


Place the new files in your project:

movement_classifier.py
movement_counters.py


Usage
Basic Usage

from utilities.utils import load_movement_criteria

# Load criteria
criteria = load_movement_criteria()

# Initialize with video file
judge = CrossFitJudge('../static/videos/airsquat.mp4', criteria)

# Or use webcam
# judge = CrossFitJudge(0, criteria)

# Run the judge
judge.run()
Controls


SPACE: Pause/Resume video
Q or ESC: Quit application

How It Works
1. Movement Classification
The MovementClassifier uses rule-based detection on pose landmarks:
Squats:

Body mostly vertical (body_angle < 30°)
Arms not overhead
Hands not on ground

Push-ups:

Body horizontal (body_angle > 60°)
Hands on ground level
Horizontal body alignment

Pull-ups:

Arms overhead
Hanging position (wrists above shoulders)
Minimal leg movement

Toes-to-Bar:

Arms overhead
Hanging position
Large leg movement range (ankles near shoulders)

2. Rep Counting
Each movement has its own counter with specific rules:
Squat Counter:

Must reach full depth (knee angle ≤ 60°)
Must reach full extension (knee angle ≥ 165°)
No-reps: "not deep enough", "no full extension"

Push-up Counter:

Must lower chest to ground (elbow angle ≤ 60°)
Must fully lock out arms (elbow angle ≥ 165°)
No-reps: "not low enough", "no lockout"

Pull-up Counter:

Chin must clear bar (angle ≤ 10°)
Must reach full arm extension (angle ≥ 170°)
No-reps: "chin not over bar", "no full extension"

Toes-to-Bar Counter:

Toes must touch bar (angle ≤ 10°)
Must return to full extension (angle ≥ 170°)
No-reps: "toes not to bar", "no full extension"

3. Confidence Buffering
To prevent flickering between movements:

Maintains a 15-frame buffer of detections
Requires 60% confidence to classify a movement
Requires 20 consecutive frames to switch movements

Configuration
Movement criteria are loaded from your JSON config file:
json{
    "squat": {
        "descending_threshold": 110,
        "ascending_threshold": 110,
        "start_point": 165,
        "end_point": 60
    },
    "push_up": {
        "descending_threshold": 90,
        "ascending_threshold": 160,
        "start_point": 165,
        "end_point": 60
    },
    "pull_up": {
        "descending_threshold": 30,
        "ascending_threshold": 150,
        "full_extension_threshold": 170,
        "regular_full_range_threshold": 10
    },
    "toes_to_bar": {
        "descending_threshold": 30,
        "ascending_threshold": 150,
        "full_extension_threshold": 170,
        "full_range_threshold": 10
    }
}
Testing Plan for Competition
Phase 1: Controlled Testing (Week 1-2)

Single Movement Videos

Test each movement type individually
Record 10+ reps of perfect form
Record 10+ reps with common faults
Verify accuracy vs manual count


Edge Cases

Partial reps
Fast tempo vs slow tempo
Different athlete body types
Different camera angles


Metrics to Track

True Positive Rate (correct good reps)
False Positive Rate (incorrectly counted no-reps)
False Negative Rate (missed good reps)
True Negative Rate (correctly identified no-reps)



Phase 2: Mixed Movement Testing (Week 3)

Transition Testing

Record videos switching between movements
Verify movement detection switches correctly
Check rep counts don't carry over


AMRAP Testing

Test with typical CrossFit AMRAP workouts
Example: "Cindy" (5 pull-ups, 10 push-ups, 15 squats)
Compare to manual judge count



Phase 3: Live Testing (Week 4)

Controlled Competition

Small group of athletes
Single camera angle (optimize placement)
Compare AI judge vs human judge
Collect athlete feedback


Refinement

Adjust thresholds based on results
Fix common misclassifications
Improve UI/feedback



Phase 4: Competition Deployment (Week 5+)
Recommended Setup:

Fixed camera position (front 45° angle)
Good lighting
Consistent background
Camera height at athlete's hip level
Distance: 2-3 meters from movement area

Success Criteria:

95%+ accuracy on movement detection
90%+ accuracy on rep counting
<2 second latency for rep confirmation
Clear no-rep feedback for athletes

Known Limitations

Camera Angle Dependency: Works best with consistent front-facing angles
Occlusion: May lose tracking if body parts are hidden
Multiple Athletes: Currently designed for single athlete tracking
Lighting: Requires adequate lighting for pose detection
Complex Movements: Thrusters and muscle-ups need multi-phase detection (future work)

Adding New Movements
To add a new movement:

Add to Classifier (movement_classifier.py):

python# In _classify_from_features method
if <your_conditions>:
    return 'your_movement'

Create Counter (movement_counters.py):

pythonclass YourMovementCounter(BaseCounter):
    def process(self, angle, lmList, detector, direction):
        # Your counting logic
        pass

Register Counter (crossfit_judge.py):

pythonself.counters = {
    # ...existing counters...
    'your_movement': YourMovementCounter(criteria.get('your_movement', {}))
}

Add Angle Logic (crossfit_judge.py):

python# In get_angle_for_movement method
elif movement_type == 'your_movement':
    # Define which joints to measure
    angle = self.detector.getAngle(...)
    return angle, p1, p2, p3
Next Steps for ML-Based Classification
Once you have enough data from competition testing:

Collect Training Data

Record 50+ reps of each movement
Various athletes, angles, speeds
Label each frame with movement type


Extract Features

Pose landmark sequences (5-10 frames)
Joint angles over time
Movement velocity patterns


Train Classifier

Random Forest or XGBoost for speed
Simple LSTM for temporal patterns
Target: 98%+ accuracy


Deploy

Replace _classify_from_features with ML model
Keep rule-based as fallback
A/B test in competition



Troubleshooting
Problem: Movement not detected

Check camera angle - should see full body
Verify adequate lighting
Check pose detection is working (green skeleton visible)

Problem: Incorrect rep counts

Adjust thresholds in config JSON
Check angle measurements are correct
Verify movement-specific logic

Problem: Switching between movements incorrectly

Increase min_stable_frames in classifier
Adjust classification rules to be more specific
Check feature extraction accuracy

Contributing
Key areas for improvement:

Multi-athlete tracking
Better angle detection for various body types
Complex movement support (thrusters, muscle-ups)
Mobile app integration
Real-time feedback overlay

License
[Your License Here]