from rest_framework import serializers

from athlete.models import Athlete, Competition


class AthleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Athlete
        fields = '__all__'

    def create(self, validated_data):
        athlete, created = Athlete.objects.get_or_create(
            email=validated_data.get('email'),
            defaults=validated_data
        )
        return athlete

class CompetitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Competition
        fields = '__all__'
