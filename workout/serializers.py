from rest_framework import serializers

from athlete.models import Competition
from workout.models import Workout, WorkoutComponent, Video, Score


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = '__all__'


class WorkoutComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutComponent
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VideoScore(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


    #competition = serializers.PrimaryKeyRelatedField(queryset=Competition.objects.all()).field_name('name')
    #workout = serializers.PrimaryKeyRelatedField(queryset=Workout.objects.all()).field_name('name')
    score = Score.objects.all().values_list(
        'is_valid',
        'score',
        'is_scaled',
        'no_reps',
        'total_reps'
    )
    random = "some random"