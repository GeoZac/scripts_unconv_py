from os import path
import glob
import re
import sys

method_pattern = re.compile(
    r"@Test\s*.*?\s*void\s+(\w+)\s*\(\s*\)([\s\S]*?)(?=@Test|$)"
)

FORMAT_CONTENT = "\n\tpreprocessRequest(prettyPrint),"
METHOD_STUB = """
.andDo(
    document(
        "{document_name}",{request_content}
        preprocessResponse(prettyPrint))
)
"""


def parse_file(test_file):
    with open(test_file, "r", encoding="utf-8") as file:
        java_code = file.read()

    matches = re.finditer(method_pattern, java_code)

    found_test = False
    total_tests = 0
    no_doc_count = 0
    mismatch_name = []

    for match in matches:
        has_document = True
        total_tests += 1
        request_arg = ""
        method_name = match.group(1)
        method_content = match.group(2)

        if "document(" not in method_content:
            has_document = False
            no_doc_count += 1
        else:
            doc_name = re.search(
                r'document\(\s*["\'](\w+)["\']',
                method_content,
            ).group(1)
            if doc_name != method_name:
                mismatch_name.append(f"{method_name}|{doc_name}")

        if "content(" in method_content:
            request_arg = FORMAT_CONTENT

        if has_document:
            continue

        print(
            METHOD_STUB.format(
                document_name=method_name,
                request_content=request_arg,
            )
        )

    print("-------------------------------------")
    print(f"Total Tests: {total_tests}")
    print(f"Need docs  : {no_doc_count}")
    print("-------------------------------------")

    return no_doc_count, total_tests, mismatch_name

def print_mismatched(items):
    if len(items) == 0:
        return
    print("Mismatched")
    for item in items:
        print(" <- ".join(item.split("|")))
    print("-------------------------------------")


def document_helper(argument):
    is_file = path.isfile(argument)
    if is_file:
        parse_file(argument)
    else:
        no_doc_count = 0
        total_tests = 0
        mismatched = []
        java_files = glob.glob(f"{argument}/*.java")
        for file_path in java_files:
            a, b, c = parse_file(file_path)
            no_doc_count += a
            total_tests += b
            mismatched.extend(c)

        print("-------------------------------------")
        print(f"Total Tests in dir: {total_tests}")
        print(f"Need docs in dir  : {no_doc_count}")
        print("-------------------------------------")
        print_mismatched(mismatched)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"usage: {sys.argv[0]} Java test file or directory with test files")
    document_helper(sys.argv[1])
