import json
import os
from pathlib import Path

JSON_EXTENSION = ".json"
CURRENT_DIR = Path(__file__).resolve().parent
RES_PATH = CURRENT_DIR.parent.parent / "res"

def open_json_file(filename: str):
    file_path = os.path.join(RES_PATH, filename + JSON_EXTENSION)
    with open(file_path, 'r', encoding='utf-8') as file:
        data_dictionary = json.load(file)
    return data_dictionary


def save_json_file(filename: str, dictionary: dict):
    file_path = os.path.join(RES_PATH, filename + JSON_EXTENSION)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(dictionary, file, indent=4, ensure_ascii=False)
