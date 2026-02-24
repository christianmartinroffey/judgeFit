import logging
import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Movement(models.Model):
    GYMNASTICS = 'G'
    MONOSTRUCTURAL = 'M'
    WEIGHTLIFTING = 'W'

    MODALITY_CHOICES = (
        (GYMNASTICS, 'Gymnastics'),
        (MONOSTRUCTURAL, 'Monostructural'),
        (WEIGHTLIFTING, 'Weightlifting'),
    )

    STRENGTH = 'ST'
    CARDIO = 'CA'
    PLYOMETRICS = 'PL'
    OLYMPIC_LIFTING = 'OL'
    POWER_LIFTING = 'PO'
    STRONGMAN = 'SM'
    OTHER = 'OT'
    STRETCHING = 'SC'

    TYPE_CHOICES = (
        (STRENGTH, 'Strength'),
        (CARDIO, 'Cardio'),
        (PLYOMETRICS, 'Plyometrics'),
        (OLYMPIC_LIFTING, 'Olympic Lifting'),
        (POWER_LIFTING, 'Power Lifting'),
        (STRONGMAN, 'Strongman'),
        (OTHER, 'Other'),
        (STRETCHING, 'Stretching'),
    )

    name = models.CharField(max_length=75)
    description = models.TextField(max_length=1500, blank=True, null=True)
    modality = models.CharField(max_length=2, choices=MODALITY_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, blank=True, null=True)
    body_part = models.CharField(max_length=50, blank=True, null=True)
    equipment = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Workout(models.Model):
    AMRAP = 'AMRAP'
    FOR_TIME = 'FT'
    FOR_WEIGHT = 'FW'
    WORKOUT_TYPE_CHOICES = [
        (AMRAP, 'As Many Reps As Possible'),
        (FOR_TIME, 'For Time'),
        (FOR_WEIGHT, 'For Weight'),
    ]

    name = models.CharField(max_length=75)
    description = models.TextField(max_length=1500, blank=True, null=True)
    type = models.CharField(max_length=5, choices=WORKOUT_TYPE_CHOICES)
    total_reps = models.IntegerField(blank=True, null=True)
    time_cap = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class WorkoutComponent(models.Model):
    workout = models.ForeignKey(Workout, related_name='components', on_delete=models.CASCADE)
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    reps = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)  # in lbs
    height = models.IntegerField(blank=True, null=True)  # in inches
    # TODO when ML has been developed to register numbers set the variations field
    # variations = JSONField(blank=True, null=True)  # Store gender-specific or other variations

    class Meta:
        ordering = ['sequence']

    def save(self, *args, **kwargs):
        if WorkoutComponent.objects.filter(workout=self.workout, sequence=self.sequence).exclude(pk=self.pk).exists():
            raise ValidationError('A component with this sequence already exists for the workout.')
        super(WorkoutComponent, self).save(*args, **kwargs)

    @staticmethod
    def get_workout_details_for_athlete(workout_id, athlete_gender):
        workout_components = WorkoutComponent.objects.filter(workout_id=workout_id)
        adjusted_components = []

        for component in workout_components:
            adjustments = component.variations.get(athlete_gender, {})  # Fetch adjustments for gender
            # Create a copy of the component with adjustments applied
            adjusted_component = {
                "movement": component.movement.name,
                "reps": component.reps,
                "weight": adjustments.get("weight", component.weight),  # Use adjusted weight if present
                # Add more fields as needed
            }
            adjusted_components.append(adjusted_component)

        return adjusted_components


class Score(models.Model):
    is_valid = models.BooleanField(default=True)
    total_reps = models.IntegerField(blank=True, null=True)
    no_reps = models.IntegerField(blank=True, null=True)
    score = models.CharField(max_length=100)  # Flexible field to store different types of scores
    created_at = models.DateTimeField(auto_now_add=True)
    is_scaled = models.BooleanField(default=False)


    @staticmethod
    def create_score(is_valid, total_reps, no_reps, is_scaled):
        Score.objects.create(
            is_valid=is_valid,
            total_reps=total_reps,
            no_reps=no_reps,
            is_scaled=is_scaled
        )


class Video(models.Model):
    SUBMITTED = 'S'  # uploaded but not yet processed - i.e. queued
    PROCESSING = 'P'  # system is processing i.e. judgefit
    ERROR = 'E'  # error with the processing (system)
    APPROVED = 'A'  # approved by judgefit / competition manager
    REJECTED = 'R'  # rejected by judgefit / competition manager

    STATUS_CHOICES = (
        (SUBMITTED, 'Submitted'),
        (PROCESSING, 'Processing'),
        (ERROR, 'Error'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    athlete = models.ForeignKey('athlete.Athlete', on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=SUBMITTED)
    is_deleted = models.BooleanField(default=False)
    score = models.OneToOneField(Score, default=None, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    competition = models.ForeignKey('athlete.Competition', on_delete=models.CASCADE, blank=True, null=True)


    def process_video(self, video, workout):
        # check if workout exists
        # use name - there will be a dropdown of workout names

        # depending on the workout call the specific pose util module to check the workout

        # get the score from the processed video

        # call save_score to save the score and create relation to athlete

        return

    '''
        #TODO note for the structure the system needs to register the type of movement
        if the athlete does less reps than needed and doesn't correct then the system needs to be able to move onto the next movement
    '''

    # TODO: there is the option to have the user upload video to youtube and then have the
    # system process that instead of uploading
