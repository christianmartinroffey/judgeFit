"""
Management command to seed common CrossFit benchmark workouts.

Usage:
    python manage.py seed_workouts
    python manage.py seed_workouts --clear   # wipe existing seeded data first
"""
from django.core.management.base import BaseCommand
from django.db import connection

from workout.models import Movement, Workout, WorkoutComponent


# ---------------------------------------------------------------------------
# Movement definitions
# ---------------------------------------------------------------------------
MOVEMENTS = [
    {
        'name': 'Thruster',
        'description': 'Front squat into overhead press in one movement.',
        'modality': 'W',
        'type': 'OL',
        'body_part': 'Full Body',
        'equipment': 'Barbell',
    },
    {
        'name': 'Pull-up',
        'description': 'Hang from a bar and pull chin above the bar.',
        'modality': 'G',
        'type': 'ST',
        'body_part': 'Upper Body',
        'equipment': 'Pull-up Bar',
    },
    {
        'name': 'Push-up',
        'description': 'Chest to ground then full lockout.',
        'modality': 'G',
        'type': 'ST',
        'body_part': 'Upper Body',
        'equipment': 'None',
    },
    {
        'name': 'Air Squat',
        'description': 'Bodyweight squat below parallel with full hip and knee extension at top.',
        'modality': 'G',
        'type': 'ST',
        'body_part': 'Lower Body',
        'equipment': 'None',
    },
    {
        'name': 'Handstand Push-up',
        'description': 'Inverted push-up against a wall, head to floor and full lockout.',
        'modality': 'G',
        'type': 'ST',
        'body_part': 'Upper Body',
        'equipment': 'Wall',
    },
    {
        'name': 'Pistol Squat',
        'description': 'Single-leg squat to full depth and back to standing.',
        'modality': 'G',
        'type': 'ST',
        'body_part': 'Lower Body',
        'equipment': 'None',
    },
    {
        'name': 'Sit-up',
        'description': 'Abmat sit-up from flat on the floor to vertical.',
        'modality': 'G',
        'type': 'ST',
        'body_part': 'Core',
        'equipment': 'Abmat',
    },
]

# ---------------------------------------------------------------------------
# Workout + component definitions
# Each component: {round, sequence, movement_name, reps}
# ---------------------------------------------------------------------------
WORKOUTS = [
    {
        'name': 'Fran',
        'description': '21-15-9 reps for time of Thrusters and Pull-ups.',
        'type': 'FT',
        'time_cap': 600,  # 10 minutes
        'components': [
            {'round': 1, 'sequence': 1, 'movement': 'Thruster', 'reps': 21},
            {'round': 1, 'sequence': 2, 'movement': 'Pull-up',  'reps': 21},
            {'round': 2, 'sequence': 1, 'movement': 'Thruster', 'reps': 15},
            {'round': 2, 'sequence': 2, 'movement': 'Pull-up',  'reps': 15},
            {'round': 3, 'sequence': 1, 'movement': 'Thruster', 'reps': 9},
            {'round': 3, 'sequence': 2, 'movement': 'Pull-up',  'reps': 9},
        ],
    },
    {
        'name': 'Cindy',
        'description': '20-minute AMRAP of 5 Pull-ups, 10 Push-ups, 15 Air Squats.',
        'type': 'AMRAP',
        'time_cap': 1200,  # 20 minutes
        'components': [
            {'round': 1, 'sequence': 1, 'movement': 'Pull-up',   'reps': 5},
            {'round': 1, 'sequence': 2, 'movement': 'Push-up',   'reps': 10},
            {'round': 1, 'sequence': 3, 'movement': 'Air Squat', 'reps': 15},
        ],
    },
    {
        'name': 'Mary',
        'description': '20-minute AMRAP of 5 Handstand Push-ups, 10 Pistol Squats, 15 Pull-ups.',
        'type': 'AMRAP',
        'time_cap': 1200,  # 20 minutes
        'components': [
            {'round': 1, 'sequence': 1, 'movement': 'Handstand Push-up', 'reps': 5},
            {'round': 1, 'sequence': 2, 'movement': 'Pistol Squat',      'reps': 10},
            {'round': 1, 'sequence': 3, 'movement': 'Pull-up',           'reps': 15},
        ],
    },
    {
        'name': 'Barbara',
        'description': '5 rounds for time of 20 Pull-ups, 30 Push-ups, 40 Sit-ups, 45 Air Squats.',
        'type': 'FT',
        'time_cap': 3600,  # 60 minutes
        'components': [
            {'round': r, 'sequence': s, 'movement': m, 'reps': reps}
            for r in range(1, 6)
            for s, m, reps in [
                (1, 'Pull-up',   20),
                (2, 'Push-up',   30),
                (3, 'Sit-up',    40),
                (4, 'Air Squat', 45),
            ]
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed common CrossFit benchmark workouts (Fran, Cindy, Mary, Barbara).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing seeded workouts before re-creating them.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            names = [w['name'] for w in WORKOUTS]
            deleted, _ = Workout.objects.filter(name__in=names).delete()
            self.stdout.write(self.style.WARNING(f'Cleared {deleted} existing workout(s).'))

        # Resync PostgreSQL sequences so inserts don't collide with existing rows
        for table, seq in [
            ('workout_workout', 'workout_workout_id_seq'),
            ('workout_movement', 'workout_movement_id_seq'),
            ('workout_workoutcomponent', 'workout_workoutcomponent_id_seq'),
        ]:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table}), 1))"
                )

        # Ensure all movements exist
        movement_map = {}
        for m in MOVEMENTS:
            obj, created = Movement.objects.get_or_create(
                name=m['name'],
                defaults={k: v for k, v in m.items() if k != 'name'},
            )
            movement_map[m['name']] = obj
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Movement "{obj.name}" — {status}')

        # Create workouts and their components
        for w in WORKOUTS:
            workout, created = Workout.objects.get_or_create(
                name=w['name'],
                defaults={
                    'description': w['description'],
                    'type': w['type'],
                    'time_cap': w.get('time_cap'),
                },
            )
            if not created:
                self.stdout.write(self.style.WARNING(
                    f'\nWorkout "{workout.name}" already exists — skipping components. '
                    f'Run with --clear to reseed.'
                ))
                continue

            self.stdout.write(self.style.SUCCESS(f'\nWorkout "{workout.name}" created.'))

            for c in w['components']:
                WorkoutComponent.objects.create(
                    workout=workout,
                    movement=movement_map[c['movement']],
                    round=c['round'],
                    sequence=c['sequence'],
                    reps=c['reps'],
                )
                self.stdout.write(
                    f'  Round {c["round"]} / Seq {c["sequence"]}: '
                    f'{c["reps"]}x {c["movement"]}'
                )

        self.stdout.write(self.style.SUCCESS('\nDone.'))
