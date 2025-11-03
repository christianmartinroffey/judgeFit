from rest_framework import status, viewsets
from rest_framework.response import Response

from athlete.serializers import AthleteSerializer, CompetitionSerializer
from athlete.models import Athlete, Competition


class AthleteViewSet(viewsets.ModelViewSet):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer

    def get_queryset(self):
        queryset = Athlete.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        queryset = Athlete.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset

class VideoSubmit(viewsets.ModelViewSet):


    def perform_create(self, serializer):
        video = self.video

        # check if the workout exists, should be a dropdown

        # if the workout does not exist then return

        # if there is a duplicate workout for the athlete then check they want to overwrite it
        # (handle this on the frontend?)

        # if it all checks out ie:
        # athlete exists
        # workout exists and is not duplicate
        # competition exists
        # then call process_video method

        return

