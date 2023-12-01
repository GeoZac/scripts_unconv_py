import re
import sys

method_pattern = re.compile(r"\b\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+\s*)?\{")


def document_helper(test_file):
    with open(test_file, "r", encoding="utf-8") as file:
        java_code = [line.strip() for line in file.readlines()]
    found_test = False
    for line in java_code:
        if "@Test" in line:
            found_test = True
            continue

        if found_test:
            match = method_pattern.search(line)

            if match:
                method_name = match.group(1)
                print(method_name)
            found_test = False


if __name__ == "__main__":
    document_helper(sys.argv[1])
