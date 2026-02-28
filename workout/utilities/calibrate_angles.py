"""
Calibration Tool for CrossFit Judge
Helps determine optimal angle thresholds for each movement
"""
import cv2
import json
import numpy as np
import PoseModule as pm
from collections import defaultdict


class AngleCalibrator:
    """
    Tool to help calibrate angle thresholds for movements
    Records min/max angles during different phases
    """

    def __init__(self, video_source, movement_type):
        """
        Args:
            video_source: Path to video or camera index
            movement_type: Type of movement being calibrated
        """
        self.video = cv2.VideoCapture(video_source)
        self.movement_type = movement_type
        self.detector = pm.PoseDetector()

        # Recording state
        self.is_recording = False
        self.phase = None  # 'bottom', 'top', or None
        self.recorded_angles = defaultdict(list)

        self.paused = False

    def get_joint_points_for_movement(self, movement_type):
        """
        Get the appropriate joint indices for measuring angles

        Returns:
            tuple: (p1_idx, p2_idx, p3_idx, description)
        """
        joints = {
            'squat': (24, 26, 28, "Hip-Knee-Ankle (Right)"),
            'push_up': (12, 14, 16, "Shoulder-Elbow-Wrist (Right)"),
            'pull_up': (12, 14, 16, "Shoulder-Elbow-Wrist (Right)"),
            'toes_to_bar': (24, 26, 28, "Hip-Knee-Ankle (Right)"),
        }

        return joints.get(movement_type, (24, 26, 28, "Hip-Knee-Ankle (Right)"))

    def draw_ui(self, img, angle, lmList):
        """Draw UI elements for calibration"""
        h, w = img.shape[:2]

        # Title
        cv2.putText(
            img, f'Calibrating: {self.movement_type.upper()}',
            (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 3
        )

        # Current angle
        cv2.putText(
            img, f'Current Angle: {int(angle)}',
            (20, 80), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2
        )

        # Recording status
        if self.is_recording:
            color = (0, 0, 255)  # Red when recording
            status = f'RECORDING {self.phase.upper()}'
            cv2.circle(img, (w - 150, 40), 15, color, -1)
        else:
            color = (200, 200, 200)
            status = 'Ready to Record'

        cv2.putText(
            img, status,
            (20, 120), cv2.FONT_HERSHEY_PLAIN, 2, color, 2
        )

        # Instructions
        instructions = [
            "Instructions:",
            "1. Get into BOTTOM position",
            "2. Press 'B' to record bottom angles",
            "3. Get into TOP position",
            "4. Press 'T' to record top angles",
            "5. Press 'S' to save calibration",
            "",
            "SPACE: Pause | Q: Quit"
        ]

        y_offset = h - 250
        for i, line in enumerate(instructions):
            cv2.putText(
                img, line,
                (20, y_offset + i * 25), cv2.FONT_HERSHEY_PLAIN, 1.2, (200, 200, 200), 1
            )

        # Show recorded values
        if self.recorded_angles:
            y = 160
            cv2.putText(
                img, "Recorded:",
                (20, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2
            )
            y += 30

            for phase, angles in self.recorded_angles.items():
                if angles:
                    avg = np.mean(angles)
                    min_a = np.min(angles)
                    max_a = np.max(angles)
                    cv2.putText(
                        img, f"{phase}: {avg:.1f} (range: {min_a:.1f}-{max_a:.1f})",
                        (20, y), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 1
                    )
                    y += 25

    def record_phase(self, phase, angle):
        """Start recording angles for a phase"""
        self.phase = phase
        self.is_recording = True
        print(f"\nRecording {phase} position... (Recording for 2 seconds)")

    def stop_recording(self):
        """Stop recording"""
        if self.is_recording and self.phase:
            angles = self.recorded_angles[self.phase]
            if angles:
                avg = np.mean(angles)
                print(f"Recorded {len(angles)} frames for {self.phase}")
                print(f"Average angle: {avg:.1f}°")
                print(f"Range: {np.min(angles):.1f}° - {np.max(angles):.1f}°")

        self.is_recording = False
        self.phase = None

    def calculate_recommendations(self):
        """Calculate recommended thresholds based on recorded angles"""
        recommendations = {}

        if 'bottom' in self.recorded_angles and 'top' in self.recorded_angles:
            bottom_angles = self.recorded_angles['bottom']
            top_angles = self.recorded_angles['top']

            bottom_avg = np.mean(bottom_angles)
            bottom_std = np.std(bottom_angles)
            top_avg = np.mean(top_angles)
            top_std = np.std(top_angles)

            # Calculate thresholds with some margin
            recommendations['end_point'] = int(bottom_avg + bottom_std * 1.5)
            recommendations['start_point'] = int(top_avg - top_std * 1.5)

            # Calculate direction change thresholds (midpoint +/- margin)
            midpoint = (bottom_avg + top_avg) / 2
            margin = (top_avg - bottom_avg) * 0.2  # 20% margin

            recommendations['descending_threshold'] = int(midpoint + margin)
            recommendations['ascending_threshold'] = int(midpoint + margin)

            print("\n" + "=" * 60)
            print("RECOMMENDED THRESHOLDS")
            print("=" * 60)
            print(f"\nBottom Position: {bottom_avg:.1f}° (std: {bottom_std:.1f})")
            print(f"Top Position: {top_avg:.1f}° (std: {top_std:.1f})")
            print(f"\nRecommended values for config.json:")
            print(json.dumps({self.movement_type: recommendations}, indent=2))
            print("\n" + "=" * 60)

        return recommendations

    def save_calibration(self, filename='calibration_data.json'):
        """Save calibration data to file"""
        recommendations = self.calculate_recommendations()

        if recommendations:
            # Load existing config if it exists
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {}

            # Update with new calibration
            config[self.movement_type] = recommendations

            # Save
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"\n✅ Calibration saved to {filename}")
            return True
        else:
            print("\n❌ Need to record both top and bottom positions first!")
            return False

    def run(self):
        """Main calibration loop"""
        print("\n" + "=" * 60)
        print(f"ANGLE CALIBRATION TOOL - {self.movement_type.upper()}")
        print("=" * 60)

        p1, p2, p3, joint_desc = self.get_joint_points_for_movement(self.movement_type)
        print(f"\nMeasuring: {joint_desc}")
        print("\nFollow the on-screen instructions to calibrate.")

        frame_count = 0
        recording_start_frame = 0
        recording_duration_frames = 60  # Record for 60 frames (~2 seconds at 30fps)

        while True:
            if not self.paused:
                success, img = self.video.read()

                if not success:
                    print("End of video or camera error")
                    break

                # Get pose
                img = self.detector.getPose(img, draw=True)
                lmList = self.detector.getPosition(img, draw=False)

                if len(lmList) != 0:
                    # Get angle
                    angle = self.detector.getAngle(img, p1, p2, p3, lmList=lmList)

                    # Record if active
                    if self.is_recording:
                        self.recorded_angles[self.phase].append(angle)
                        frame_count += 1

                        # Stop recording after duration
                        if frame_count >= recording_duration_frames:
                            self.stop_recording()
                            frame_count = 0

                    # Draw angle on image
                    self.detector.drawAngle(img, p1, p2, p3, lmList)

                    # Draw UI
                    self.draw_ui(img, angle, lmList)

                cv2.imshow("Calibration Tool", img)
            else:
                cv2.imshow("Calibration Tool", img)

            # Handle keyboard input
            key = cv2.waitKey(1)

            if key == ord('b') or key == ord('B'):
                # Record bottom position
                if not self.is_recording and len(lmList) != 0:
                    angle = self.detector.getAngle(None, p1, p2, p3, lmList=lmList)
                    self.record_phase('bottom', angle)
                    frame_count = 0

            elif key == ord('t') or key == ord('T'):
                # Record top position
                if not self.is_recording and len(lmList) != 0:
                    angle = self.detector.getAngle(None, p1, p2, p3, lmList=lmList)
                    self.record_phase('top', angle)
                    frame_count = 0

            elif key == ord('s') or key == ord('S'):
                # Save calibration
                self.save_calibration()

            elif key == 32:  # Space
                self.paused = not self.paused
                if self.is_recording:
                    self.stop_recording()

            elif key == ord('q') or key == 27:  # Q or ESC
                break

        self.video.release()
        cv2.destroyAllWindows()


def main():
    """Main entry point for calibration tool"""
    print("\n" + "=" * 60)
    print("CROSSFIT JUDGE - ANGLE CALIBRATION TOOL")
    print("=" * 60)

    print("\nAvailable movements:")
    print("  1. squat")
    print("  2. push_up")
    print("  3. pull_up")
    print("  4. toes_to_bar")

    movement = input("\nEnter movement type to calibrate: ").strip().lower()

    if movement not in ['squat', 'push_up', 'pull_up', 'toes_to_bar']:
        print("Invalid movement type!")
        return

    video_source = input("Enter video path (or press Enter for webcam): ").strip()

    if not video_source:
        video_source = 0

    calibrator = AngleCalibrator(video_source, movement)
    calibrator.run()

    print("\nCalibration complete!")


if __name__ == "__main__":
    main()
