from rest_framework import status, viewsets
from rest_framework.decorators import action
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

    @action(detail=False, methods=['get', 'post', 'patch'])
    def me(self, request):
        try:
            athlete = Athlete.objects.get(email=request.user.email)
        except Athlete.DoesNotExist:
            athlete = None

        if request.method == 'GET':
            if athlete is None:
                return Response(
                    {'detail': 'no_profile', 'user_email': request.user.email},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(self.get_serializer(athlete).data)

        if request.method == 'POST':
            if athlete is not None:
                return Response({'detail': 'Profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            data = {**request.data, 'email': request.user.email}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # PATCH
        if athlete is None:
            return Response({'detail': 'Athlete profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(athlete, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        queryset = Competition.objects.all()

        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset

