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
        return Video.objects.filter(
            athlete__email=self.request.user.email
        ).order_by('-created_at').select_related('competition', 'workout', 'score').prefetch_related('score__scorebreakdown_set')

    def create(self, request, *args, **kwargs):
        from athlete.models import Athlete

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            athlete = Athlete.objects.get(email=request.user.email)
        except Athlete.DoesNotExist:
            return Response(
                {'detail': 'No athlete profile found. Please create your profile first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a Score record first so the task has an ID to update
        new_score = Score.objects.create(score='')

        video_url = request.data.get('videoURL')
        video = serializer.save(athlete=athlete, score=new_score, urlPath=video_url)

        # Queue the analysis
        analyse_video.delay(str(new_score.id), video.urlPath)

        return Response(
            {'id': str(new_score.id), 'status': 'queued'},
            status=status.HTTP_202_ACCEPTED
        )


    # @action(detail=True, methods=['get'])
    # def status(self, request, pk=None):
    #     score = self.get_object()
    #     return Response({
    #         'id': str(score.id),
    #         'status': score.status,
    #         'total_reps': score.total_reps,
    #         'no_reps': score.no_reps,
    #         'movement_breakdown': score.movement_breakdown,
    #     })