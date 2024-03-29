import json
import os


def traverse_json_keys(data, parent_key=""):
    if isinstance(data, dict):
        yield parent_key
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            yield from traverse_json_keys(value, new_key)
    elif isinstance(data, list):
        yield parent_key
        for index, item in enumerate(data):
            new_key = f"{parent_key}[{index}]" if parent_key else f"[{index}]"
            yield from traverse_json_keys(item, new_key)
    else:
        if parent_key:
            yield parent_key


def json_traverser(
    file_name="violations.json",
):
    script_dir = os.path.dirname(__file__)

    file_path = os.path.join(script_dir, file_name)

    data = None
    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    results = traverse_json_keys(data)
    for result in results:
        print(result)


if __name__ == "__main__":
    json_traverser()
