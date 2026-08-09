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
    WorkoutComponentSerializer, VideoSerializer, VideoScore, VideoReviewSerializer,
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

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """
        Ranked leaderboard for this workout: each athlete's best (highest
        good_reps, then total_reps, then earliest) completed+valid submission.
        """
        videos = Video.objects.filter(
            workout_id=pk, is_deleted=False, score__status=Score.COMPLETE,
        ).select_related('athlete', 'score').order_by(
            '-score__good_reps', '-score__total_reps', 'score__created_at'
        )

        best_by_athlete = {}
        for video in videos:
            if video.athlete_id not in best_by_athlete:
                best_by_athlete[video.athlete_id] = video

        ranked = sorted(
            best_by_athlete.values(),
            key=lambda v: (-(v.score.good_reps or 0), -(v.score.total_reps or 0), v.score.created_at),
        )

        data = [
            {
                'rank': i + 1,
                'athlete_id': v.athlete_id,
                'athlete_name': f'{v.athlete.name} {v.athlete.surname}'.strip(),
                'good_reps': v.score.good_reps,
                'total_reps': v.score.total_reps,
                'no_reps': v.score.no_reps,
                'is_valid': v.score.is_valid,
                'is_scaled': v.score.is_scaled,
                'video_id': str(v.id),
            }
            for i, v in enumerate(ranked)
        ]
        return Response(data)


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

    def get_permissions(self):
        if self.action in ('review_queue', 'approve', 'reject'):
            return [IsCompetitionAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        base = Video.objects.order_by('-created_at').select_related(
            'athlete', 'competition', 'workout', 'score'
        ).prefetch_related('score__scorebreakdown_set')

        # Admins can retrieve any single video (e.g. from the review queue);
        # `list` stays self-scoped even for admins so "My videos" still means mine.
        if self.action == 'retrieve' and getattr(self.request.user, 'is_competition_admin', False):
            return base
        return base.filter(athlete__email=self.request.user.email)

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

    @action(detail=False, methods=['get'])
    def review_queue(self, request):
        """All non-deleted submissions, for competition-admin review. Not
        scoped to the requesting user, unlike the default list action."""
        queryset = Video.objects.filter(is_deleted=False).order_by('-created_at').select_related(
            'athlete', 'competition', 'workout', 'score'
        ).prefetch_related('score__scorebreakdown_set')

        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        competition_param = request.query_params.get('competition')
        if competition_param:
            queryset = queryset.filter(competition_id=competition_param)

        page = self.paginate_queryset(queryset)
        serializer = VideoReviewSerializer(page if page is not None else queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        video = Video.objects.filter(pk=pk).first()
        if video is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        video.status = Video.APPROVED
        video.save()
        return Response({'id': str(video.id), 'status': video.status})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        video = Video.objects.filter(pk=pk).first()
        if video is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        video.status = Video.REJECTED
        video.save()
        return Response({'id': str(video.id), 'status': video.status})