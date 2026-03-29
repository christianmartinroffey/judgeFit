from rest_framework import serializers

from athlete.models import Athlete, Competition
from athlete.serializers import CompetitionSerializer
from workout.models import Workout, WorkoutComponent, Video, Score


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = '__all__'


class WorkoutComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutComponent
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['is_valid', 'score', 'is_scaled', 'no_reps', 'total_reps']


class VideoSerializer(serializers.ModelSerializer):
    # TODO Athlete is injected server-side for now (mock); not required from the frontend.
    athlete = serializers.PrimaryKeyRelatedField(
        queryset=Athlete.objects.all(), required=False
    )
    competition = serializers.PrimaryKeyRelatedField(
        queryset=Competition.objects.all(), required=False
    )
    workout = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(), required=False
    )

    class Meta:
        model = Video
        fields = '__all__'


class VideoScore(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    competition = serializers.SerializerMethodField()
    workout = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_competition(self, obj):
        return obj.competition.name

    def get_workout(self, obj):
        return obj.workout.name

    score = ScoreSerializer()

    def get_score(self, obj):
        if obj.score:
            return ScoreSerializer(obj.score).data
        return None

    class Meta:
        model = Video
        fields = '__all__'
