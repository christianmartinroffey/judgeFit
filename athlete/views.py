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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        queryset = Competition.objects.all()

        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset

