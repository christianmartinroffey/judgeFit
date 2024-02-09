import json


def load_movement_criteria():
    file_path = '../static/config/movement_analysis_criteria.json'
    criteria = {}
    try:
        with open(file_path, 'r') as file:
            criteria = json.load(file)
    except Exception as e:
        print(f"Failed to load movement criteria: {e}")
    return criteria

