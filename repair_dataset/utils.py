import json

def load_data_json(json_path:str) -> dict:
    with open(json_path, 'r') as f:
        return json.load(f)