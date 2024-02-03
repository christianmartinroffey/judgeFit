import datetime

from django.core.management.base import BaseCommand, CommandError

from athlete.models import Affiliate
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
                name = row['name']
                address = row['address']
                city = row['city']
                postal_code = row['postal_code']
                website = row['website']
                country = row['country']
                state = row['state']
                crossfit_affiliate = row['crossfit_affiliate']
                crossfit_affiliate_since = row['crossfit_affiliate_since']
                photo = row['photo']

                print(f"Importing row: {row}")

                # Create Movements object
                affiliate = Affiliate(
                    name=name,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    website=website,
                    country=country,
                    state=state,
                    crossfit_affiliate=crossfit_affiliate,
                    crossfit_affiliate_since=crossfit_affiliate_since,
                    photo=photo
                )
                affiliate.save()

            print("Import completed.")

        self.stdout.write(self.style.SUCCESS('Successfully imported affiliates from CSV'))
