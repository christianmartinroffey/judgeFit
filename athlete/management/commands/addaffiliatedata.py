import datetime

from django.core.management.base import BaseCommand, CommandError

from athlete.models import Affiliate, Country
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
                state = row['state']
                crossfit_affiliate_since = row['crossfit_affiliate_since']
                if crossfit_affiliate_since:
                    crossfit_affiliate_since = datetime.datetime.fromisoformat(crossfit_affiliate_since.rstrip("Z")).date()

                photo = row['photo']

                country_code = row['country']
                try:
                    country = Country.objects.get(
                        code=country_code)  # Assuming 'code' is the field in Country model storing the country codes
                except Country.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Country with code {country_code} does not exist. Skipping row.'))
                    continue

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
                    crossfit_affiliate=True,
                    crossfit_affiliate_since=crossfit_affiliate_since,
                    photo=photo
                )
                affiliate.save()

            print("Import completed.")

        self.stdout.write(self.style.SUCCESS('Successfully imported affiliates from CSV'))
