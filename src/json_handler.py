import json
import os

RES_PATH = "../res"
JSON_EXTENSION = ".json"


def open_json_file(filename: str):
    file_path = RES_PATH + "/" + filename + JSON_EXTENSION
    with open(file_path, 'r', encoding='utf-8') as file:
        data_dictionary = json.load(file)
    return data_dictionary


def save_json_file(filename: str, dictionary: dict):
    file_path = RES_PATH + "/" + filename + JSON_EXTENSION
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(dictionary, file, indent=4, ensure_ascii=False)
