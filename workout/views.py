import logging

from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.response import Response

from workout.models import Workout, WorkoutComponent, Video, Score
from workout.serializers import WorkoutSerializer, WorkoutComponentSerializer, VideoSerializer, \
    VideoScore
from workout.tasks import analyse_video
from rest_framework.decorators import action


class WorkoutsViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

    def get_queryset(self):
        queryset = Workout.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class WorkoutComponentsViewSet(viewsets.ModelViewSet):
    queryset = WorkoutComponent.objects.all()
    serializer_class = WorkoutComponentSerializer

    def get_queryset(self):
        queryset = WorkoutComponent.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class VideosViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return VideoScore  # use this for reads
        return VideoSerializer  # use this for writes

    def get_queryset(self):
        return Video.objects.all().select_related('competition', 'workout', 'score')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        score = serializer.save()

        # Queue the analysis
        analyse_video.delay(str(score.id), score.video.url)

        return Response(
            {'id': str(score.id), 'status': 'queued'},
            status=status.HTTP_202_ACCEPTED
        )

    # def create(self, request, *args, **kwargs):
    #     video_url = request.data.get('videoURL')
    #
    #     # 1. Create the video object
    #     video, created = Video.objects.get_or_create(
    #         urlPath=video_url,
    #         athlete_id=1,
    #         workout_id=1,
    #         competition_id=1,
    #     )
    #
    #     # 2. Update status to processing
    #     video.status = Video.PROCESSING
    #     video.save()
    #
    #     # TODO when save has been successful / failed
    #     # return here to the FE and then call the process video method
    #     # asynchronously (celery task) and update the video status when done
    #
    #     try:
    #         # 3. Call process_video on the model, which calls process_movement
    #         result = Video.process_video(video_url)
    #
    #         # 4. Save the score and link it back to the video
    #         score = Score.create_score(
    #             is_valid=result['is_valid'],
    #             total_reps=result['total_reps'],
    #             no_reps=result['no_reps'],
    #             is_scaled=result['is_scaled'],
    #         )
    #         video.score = score
    #         video.status = Video.APPROVED
    #         video.save()
    #
    #     except Exception as e:
    #         video.status = Video.ERROR
    #         video.save()
    #         logging.error(f"Error processing video {video.id}: {e}")
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #     return Response({
    #         'video_id': str(video.id),
    #         'total_reps': result['total_reps'],
    #         'no_reps': result['no_reps'],
    #         'is_valid': result['is_valid'],
    #     }, status=status.HTTP_201_CREATED)
        # check if the workout exists, should be a dropdown

        # if the workout does not exist then return

        # if there is a duplicate workout for the athlete then check they want to overwrite it
        # (handle this on the frontend?)

        # if it all checks out ie:
        # athlete exists
        # workout exists and is not duplicate
        # competition exists
        # then call process_video method

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        score = self.get_object()
        return Response({
            'id': str(score.id),
            'status': score.status,
            'total_reps': score.total_reps,
            'no_reps': score.no_reps,
            'movement_breakdown': score.movement_breakdown,
        })