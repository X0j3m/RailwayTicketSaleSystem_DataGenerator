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

def append_save_json_file(filename: str, dictionary: dict | list):
    file_path = os.path.join(RES_PATH, filename + JSON_EXTENSION)

    data = []

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                data = []

    if isinstance(dictionary, list):
        data.extend(dictionary)
    else:
        data.append(dictionary)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)