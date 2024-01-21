from django.core.management.base import BaseCommand
from workout.models import Movement
import csv


class Command(BaseCommand):
    help = 'add movements via csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert CSV data to match the Movements model fields
                modality = row['modality']
                type = row['type']
                body_part = row['body_part']
                equipment = row['equipment']

                print(f"Importing row: {row}")

                # Create Movements object
                movement = Movement(
                    name=row['name'],
                    description=row['description'],
                    modality=modality,
                    type=type,
                    body_part=body_part,
                    equipment=equipment
                )
                movement.save()

            print("Import completed.")

        self.stdout.write(self.style.SUCCESS('Successfully imported movements from CSV'))
