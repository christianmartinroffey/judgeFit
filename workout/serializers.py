from rest_framework import serializers

from workout.models import Workout, WorkoutComponent, Video


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