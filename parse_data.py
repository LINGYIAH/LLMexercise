import json
import os

def load_items(filename):
    """read JSON file and return only the items list"""
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["items"]

def get_unclaimed_items(items):
    """only return items with status 'unclaimed'"""
    return [item for item in items if item["status"] == "unclaimed"]

def save_result(result, filename):
    """save JSON file, create directory if it doesn't exist"""
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)