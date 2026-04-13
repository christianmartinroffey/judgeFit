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
        components = []
        try:
            video = score.video  # reverse OneToOneField from Video.score
            workout = video.workout
            workout_type = workout.type
            components = list(workout.components.select_related('movement').order_by('round', 'sequence'))
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

        # Create per-rep ScoreBreakdown records if the analyser produced a rep log.
        rep_log = result.get('rep_log', [])
        if rep_log:
            from workout.models import ScoreBreakdown
            try:
                # Resolve the Movement FK — use the first wall_ball component.
                movement_obj = None
                for component in components:
                    if 'wall' in component.movement.name.lower():
                        movement_obj = component.movement
                        break
                if movement_obj is None and components:
                    movement_obj = components[0].movement

                if movement_obj is not None:
                    ScoreBreakdown.objects.bulk_create([
                        ScoreBreakdown(
                            score=score,
                            is_good_rep=rep['is_good_rep'],
                            movement=movement_obj,
                            no_rep_reason=rep.get('no_rep_reason'),
                            rep_number=rep.get('rep_number'),
                            rep_timestamp=rep.get('rep_timestamp'),
                        )
                        for rep in rep_log
                    ])
                    logger.info(
                        "Created %d ScoreBreakdown records for score %s",
                        len(rep_log), score_id,
                    )
            except Exception as breakdown_err:
                logger.warning(
                    "Could not create ScoreBreakdown records for score %s: %s",
                    score_id, breakdown_err,
                )

    except Exception as e:
        logger.error("Task failed for score %s: %s", score_id, e)
        score.status = Score.FAILED
        score.save()
        raise
