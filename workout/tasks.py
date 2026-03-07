from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def analyse_video(self, score_id, video_url):
    from workout.models import Score
    from workout.utilities.squatChecker import process_movement

    score = Score.objects.get(id=score_id)
    score.status = 'processing'
    score.save()

    try:
        result = process_movement(video_url)
        score.total_reps = result['total_reps']
        score.no_reps = result['no_reps']
        score.is_valid = result['is_valid']
        score.is_scaled = result['is_scaled']
        score.status = 'complete'
        score.save()
    except Exception as e:
        logger.error(f"Task failed for score {score_id}: {e}")
        score.status = 'failed'
        score.save()
        raise