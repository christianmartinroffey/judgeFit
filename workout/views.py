import logging

from rest_framework import status, viewsets
from rest_framework.response import Response

from workout.models import Workout, WorkoutComponent, Video
from workout.serializers import WorkoutSerializer, WorkoutComponentSerializer, VideoSerializer


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

    def get_queryset(self):
        queryset = Video.objects.all()
        if not queryset.exists():
            return None
        return queryset


    def create(self, request, *args, **kwargs):
        logging.info(request)
        logging.info(f"input {self}")

        Video.objects.get_or_create(ur)
        # check if the workout exists, should be a dropdown

        # if the workout does not exist then return

        # if there is a duplicate workout for the athlete then check they want to overwrite it
        # (handle this on the frontend?)

        # if it all checks out ie:
        # athlete exists
        # workout exists and is not duplicate
        # competition exists
        # then call process_video method

        return Response(status=status.HTTP_201_CREATED)

