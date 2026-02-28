"""
Test script for validating CrossFit Judge accuracy
Compares automated counts against manual ground truth
"""
import json
from judge import Judge
from workout.utilities.utils import load_movement_criteria


class JudgeValidator:
    """Validates judge accuracy against ground truth"""

    def __init__(self, video_path, ground_truth):
        """
        Args:
            video_path: Path to test video
            ground_truth: Dict with expected results
                {
                    'movement': 'squat',
                    'good_reps': 10,
                    'no_reps': 2,
                    'no_rep_reasons': {
                        'not deep enough': 1,
                        'no full extension': 1
                    }
                }
        """
        self.video_path = video_path
        self.ground_truth = ground_truth
        self.criteria = load_movement_criteria()

    def run_test(self):
        """Run the judge and collect results"""
        print(f"\n{'=' * 60}")
        print(f"Testing: {self.video_path}")
        print(f"Expected Movement: {self.ground_truth['movement']}")
        print(f"{'=' * 60}\n")

        judge = Judge(self.video_path, self.criteria)

        # Run judge (you'll need to quit manually or it will process full video)
        judge.run()

        # Get results
        expected_movement = self.ground_truth['movement']
        counter = judge.counters[expected_movement]
        stats = counter.get_stats()

        # Compare results
        results = self.compare_results(stats)
        self.print_results(results)

        return results

    def compare_results(self, actual_stats):
        """Compare actual results to ground truth"""
        results = {
            'video': self.video_path,
            'movement': self.ground_truth['movement'],
            'expected': self.ground_truth,
            'actual': actual_stats,
            'accuracy': {}
        }

        # Calculate accuracy metrics
        expected_good = self.ground_truth['good_reps']
        actual_good = actual_stats['count']
        expected_no_rep = self.ground_truth['no_reps']
        actual_no_rep = actual_stats['no_rep']

        # Good rep accuracy
        if expected_good > 0:
            good_rep_accuracy = min(actual_good / expected_good, 1.0) * 100
        else:
            good_rep_accuracy = 100.0 if actual_good == 0 else 0.0

        # No-rep accuracy
        if expected_no_rep > 0:
            no_rep_accuracy = min(actual_no_rep / expected_no_rep, 1.0) * 100
        else:
            no_rep_accuracy = 100.0 if actual_no_rep == 0 else 0.0

        # Overall accuracy
        total_expected = expected_good + expected_no_rep
        total_actual = actual_good + actual_no_rep

        if total_expected > 0:
            overall_accuracy = (
                                       min(actual_good, expected_good) +
                                       min(actual_no_rep, expected_no_rep)
                               ) / total_expected * 100
        else:
            overall_accuracy = 0.0

        results['accuracy'] = {
            'good_reps': good_rep_accuracy,
            'no_reps': no_rep_accuracy,
            'overall': overall_accuracy
        }

        return results

    def print_results(self, results):
        """Print comparison results"""
        print(f"\n{'=' * 60}")
        print("RESULTS")
        print(f"{'=' * 60}")

        print(f"\nMovement: {results['movement']}")

        print(f"\nGood Reps:")
        print(f"  Expected: {results['expected']['good_reps']}")
        print(f"  Actual:   {results['actual']['count']}")
        print(f"  Accuracy: {results['accuracy']['good_reps']:.1f}%")

        print(f"\nNo-Reps:")
        print(f"  Expected: {results['expected']['no_reps']}")
        print(f"  Actual:   {results['actual']['no_rep']}")
        print(f"  Accuracy: {results['accuracy']['no_reps']:.1f}%")

        print(f"\nOverall Accuracy: {results['accuracy']['overall']:.1f}%")

        # Pass/Fail
        threshold = 85.0  # 85% accuracy threshold
        if results['accuracy']['overall'] >= threshold:
            print(f"\n✅ PASS (>={threshold}% accuracy)")
        else:
            print(f"\n❌ FAIL (<{threshold}% accuracy)")

        print(f"\n{'=' * 60}\n")


class TestSuite:
    """Run multiple tests and generate report"""

    def __init__(self):
        self.tests = []
        self.results = []

    def add_test(self, video_path, ground_truth):
        """Add a test case"""
        self.tests.append({
            'video_path': video_path,
            'ground_truth': ground_truth
        })

    def run_all(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("CROSSFIT JUDGE TEST SUITE")
        print("=" * 60)
        print(f"\nRunning {len(self.tests)} tests...\n")

        for i, test in enumerate(self.tests, 1):
            print(f"\n{'#' * 60}")
            print(f"Test {i}/{len(self.tests)}")
            print(f"{'#' * 60}")

            validator = JudgeValidator(
                test['video_path'],
                test['ground_truth']
            )
            result = validator.run_test()
            self.results.append(result)

        # Generate summary report
        self.print_summary()

    def print_summary(self):
        """Print summary of all tests"""
        print("\n" + "=" * 60)
        print("TEST SUITE SUMMARY")
        print("=" * 60)

        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r['accuracy']['overall'] >= 85.0)
        failed = total_tests - passed

        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed} ({passed / total_tests * 100:.1f}%)")
        print(f"Failed: {failed} ({failed / total_tests * 100:.1f}%)")

        # Average accuracy per movement
        print("\nAccuracy by Movement:")
        movement_accuracies = {}
        for result in self.results:
            movement = result['movement']
            accuracy = result['accuracy']['overall']

            if movement not in movement_accuracies:
                movement_accuracies[movement] = []
            movement_accuracies[movement].append(accuracy)

        for movement, accuracies in movement_accuracies.items():
            avg_accuracy = sum(accuracies) / len(accuracies)
            print(f"  {movement}: {avg_accuracy:.1f}%")

        # Overall average
        overall_avg = sum(r['accuracy']['overall'] for r in self.results) / total_tests
        print(f"\nOverall Average Accuracy: {overall_avg:.1f}%")

        print("\n" + "=" * 60 + "\n")

    def export_results(self, filename='test_results.json'):
        """Export results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results exported to {filename}")


# Example usage
def example_test():
    """Example of how to run tests"""

    # Create test suite
    suite = TestSuite()

    # Add test cases
    # Test 1: Perfect squats
    # suite.add_test(
    #     video_path='../static/videos/airsquat.mp4',
    #     ground_truth={
    #         'movement': 'squat',
    #         'good_reps': 6,  # Expected good reps
    #         'no_reps': 0  # Expected no-reps
    #     }
    # )
    #
    # # Test 2: Squats with faults
    # suite.add_test(
    #     video_path='../static/videos/airsquat2.mp4',
    #     ground_truth={
    #         'movement': 'squat',
    #         'good_reps': 5,
    #         'no_reps': 3
    #     }
    # )

    # Test 3: Push-ups
    suite.add_test(
        video_path='../../static/videos/pushup.mp4',
        ground_truth={
            'movement': 'push_up',
            'good_reps': 10,
            'no_reps': 2
        }
    )

    # # Test 4: Burpees
    # suite.add_test(
    #     video_path='../static/videos/pushup.mp4',
    #     ground_truth={
    #         'movement': 'burpee',
    #         'good_reps': 10,
    #         'no_reps': 2
    #     }
    # )


    # Run all tests
    suite.run_all()

    # Export results
    suite.export_results('test_results.json')


if __name__ == "__main__":
    # Run example test
    print("CrossFit Judge Validation Script")
    print("-" * 60)
    print("\nThis script helps you validate judge accuracy.")
    print("Update the ground_truth values with manual counts.")
    print("\nPress 'q' or ESC to end each test video.\n")

    input("Press Enter to start testing...")

    example_test()
