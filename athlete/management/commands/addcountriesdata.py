import datetime

from django.core.management.base import BaseCommand

from athlete.models import Country
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
                # Convert CSV data to match the countries model fields
                name = row['name']
                router_code = row['router_code']
                code = row['code']

                print(f"Importing row: {row}")

                # Create countries object
                country = Country(
                    name=name,
                    router_code=router_code,
                    code=code
                )
                country.save()

            print("Import completed.")

        self.stdout.write(self.style.SUCCESS('Successfully imported countries from CSV'))
