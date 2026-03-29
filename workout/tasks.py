from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def analyse_video(self, score_id, video_url):
    from workout.models import Score
    from workout.utilities.workout_analyser import analyse_workout_video
    from workout.utilities.squatChecker import process_movement

    score = Score.objects.get(id=score_id)
    score.status = Score.PROCESSING
    score.save()

    try:
        # Load workout context from the linked Video → Workout → WorkoutComponents
        workout_components = []
        workout_type = 'FT'
        try:
            video = score.video  # reverse OneToOneField from Video.score
            workout = video.workout
            workout_type = workout.type
            components = workout.components.select_related('movement').order_by('round', 'sequence')
            workout_components = [
                {
                    'movement': component.movement.name,
                    'expected_reps': component.reps,
                    'round': component.round,
                    'sequence': component.sequence,
                }
                for component in components
            ]
        except Exception as ctx_err:
            logger.warning(
                "Could not load workout context for score %s — falling back to "
                "single-movement analysis. Error: %s",
                score_id, ctx_err,
            )

        if workout_components:
            result = analyse_workout_video(video_url, workout_components, workout_type)
        else:
            # Fallback: single-movement squat analysis (no workout plan available)
            result = process_movement(video_url)
            result.setdefault('breakdown', [])
            result.setdefault('rounds_completed', 0)

        score.total_reps = result['total_reps']
        score.no_reps = result['no_reps']
        score.is_valid = result['is_valid']
        score.is_scaled = result['is_scaled']
        score.movement_breakdown = result.get('breakdown', [])
        score.status = Score.COMPLETE
        score.save()

    except Exception as e:
        logger.error("Task failed for score %s: %s", score_id, e)
        score.status = Score.FAILED
        score.save()
        raise
