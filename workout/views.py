import logging

from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from athlete.views import IsCompetitionAdmin
from workout.models import Workout, WorkoutComponent, Video, Score, Movement
from workout.serializers import (
    WorkoutSerializer, WorkoutDetailSerializer,
    WorkoutComponentSerializer, VideoSerializer, VideoScore,
    MovementSerializer,
)
from workout.tasks import analyse_video


class MovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movement.objects.all().order_by('name')
    serializer_class = MovementSerializer

    def get_permissions(self):
        return [IsAuthenticated()]


class WorkoutsViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return WorkoutDetailSerializer
        return WorkoutSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'activate'):
            return [IsCompetitionAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Workout.objects.all()
        name = self.request.query_params.get('name', None)
        competition = self.request.query_params.get('competition', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        if competition is not None:
            queryset = queryset.filter(competition_id=competition)
        return queryset

    def update(self, request, *args, **kwargs):
        if self.get_object().is_active:
            return Response({'detail': 'Cannot edit an active workout.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if self.get_object().is_active:
            return Response({'detail': 'Cannot edit an active workout.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        workout = self.get_object()
        workout.is_active = True
        workout.save()
        return Response({'id': workout.id, 'is_active': workout.is_active})


class WorkoutComponentsViewSet(viewsets.ModelViewSet):
    queryset = WorkoutComponent.objects.all()
    serializer_class = WorkoutComponentSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCompetitionAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = WorkoutComponent.objects.all()
        workout = self.request.query_params.get('workout', None)
        if workout is not None:
            queryset = queryset.filter(workout_id=workout)
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