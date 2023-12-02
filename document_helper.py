import re
import sys

method_pattern = re.compile(r"@Test\s*.*\s*void\s+(\w+)\s*\(\s*\)([\s\S]*?)\}")

METHOD_STUB = """
.andDo(
    document(
        "{document_name}",
        preprocessRequest(prettyPrint),
        preprocessResponse(prettyPrint))
)
"""


def document_helper(test_file):
    with open(test_file, "r", encoding="utf-8") as file:
        java_code = file.read()

    matches = re.finditer(method_pattern, java_code)

    found_test = False
    has_document = False

    for match in matches:
        if "@Test" in match:
            found_test = True
            has_document = False
            continue

        if "document(" in match:
            has_document = True
            continue

        if has_document:
            print("Already documented")

        if found_test:
            match = method_pattern.search(match)

            if match:
                method_name = match.group(1)
                print(METHOD_STUB.format(document_name=method_name))
            found_test = False


if __name__ == "__main__":
    document_helper(sys.argv[1])
