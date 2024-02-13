from rest_framework import status, viewsets
from rest_framework.response import Response

from athlete.serializers import AthleteSerializer
from athlete.models import Athlete


class AthleteViewSet(viewsets.ModelViewSet):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer

    def get_queryset(self):
        queryset = Athlete.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset
