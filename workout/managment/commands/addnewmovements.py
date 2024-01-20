import csv
from workout.models import Movement

def import_movements_from_csv(csv_file_path):
    with open("/Users/christianmartin-roffey/Downloads/gym_exercise_movements.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert CSV data to match the Movements model fields
            modality = row['modality']
            type = row['type']
            body_part = row['body_part']
            equipment = row['equipment']

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

if __name__ == "__main__":
    csv_file_path = '/Users/christianmartin-roffey/Downloads/gym_exercise_movements.csv'
    import_movements_from_csv(csv_file_path)