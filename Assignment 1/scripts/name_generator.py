import json
import random
import os

config_folder = os.path.join(os.path.dirname(__file__), "..", "config") # GPT Line
first_names = os.path.join(config_folder, "first-names.json")
last_names = os.path.join(config_folder, "last-names.json")

_FIRST_NAMES = None
_LAST_NAMES = None

def _read_json_array(path):
    # return a list of strings loaded from a JSON file at path
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Couldn't find {path}. Make sure you're running the program from within the folder that contains this script"
        ) from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
    
    return data

def _ensure_loaded():
    global _FIRST_NAMES, _LAST_NAMES

    if _FIRST_NAMES is None:
        _FIRST_NAMES = _read_json_array(first_names)
    if _LAST_NAMES is None:
        _LAST_NAMES = _read_json_array(last_names)

def random_full_name(seperator=" ", titlecase=True, rng=None):
# return a random full name
    # returns = "Alice Johnson"

    _ensure_loaded()

    chooser = rng.choice if rng is not None else random.choice

    first = chooser(_FIRST_NAMES)
    last = chooser(_LAST_NAMES)

    if titlecase:
        first = first.title()
        last = last.title()

    return f"{first}{seperator}{last}"