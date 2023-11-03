def traverse_json_keys(data, parent_key=""):
    if isinstance(data, dict):
        print(parent_key)
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            traverse_json_keys(value, new_key)
    elif isinstance(data, list):
        print(parent_key)
        for index, item in enumerate(data):
            new_key = f"{parent_key}[{index}]" if parent_key else f"[{index}]"
            traverse_json_keys(item, new_key)
    else:
        if parent_key:
            print(parent_key)
