import json
import os

CONTENT_TYPE = "application/problem+json"


def assertions_convertor(
    file_name="violations.json",
):
    script_dir = os.path.dirname(__file__)

    file_path = os.path.join(script_dir, file_name)

    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    java_code = "\n"

    java_code += (
        f'\t.andExpect(header().string("Content-Type", is("{CONTENT_TYPE}")))\n'
    )
    java_code += f"\t.andExpect(jsonPath(\"$.type\", is(\"{data['type']}\")))\n"
    java_code += f"\t.andExpect(jsonPath(\"$.title\", is(\"{data['title']}\")))\n"
    java_code += f"\t.andExpect(jsonPath(\"$.status\", is({data['status']})))\n"
    java_code += f"\t.andExpect(jsonPath(\"$.violations\", hasSize({len(data['violations'])})))\n"

    count = 0
    for violation in data["violations"]:
        java_code += f"\t.andExpect(jsonPath(\"$.violations[{count}].field\", is(\"{violation['field']}\")))\n"
        java_code += f"\t.andExpect(jsonPath(\"$.violations[{count}].message\",is(\"{violation['message']}\")))\n"
        count += 1

    print(java_code)


if __name__ == "__main__":
    assertions_convertor()
