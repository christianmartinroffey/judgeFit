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

    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True, null=True)
    modality = models.CharField(max_length=2, choices=MODALITY_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, blank=True, null=True)
    body_part = models.CharField(max_length=50, blank=True, null=True)
    equipment = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name
