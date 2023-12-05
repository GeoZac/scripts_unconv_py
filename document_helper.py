from os import path
import glob
import re
import sys

method_pattern = re.compile(r"@Test\s*.*\s*void\s+(\w+)\s*\(\s*\)([\s\S]*?)\}")

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
    has_document = False
    total_tests = 0
    no_doc_count = 0

    for match in matches:
        total_tests += 1
        request_arg = ""
        method_name = match.group(1)
        method_content = match.group(2)

        if "document(" not in method_content:
            has_document = False
            no_doc_count += 1

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

    print(f"Total Tests: {total_tests}")
    print(f"Need docs  : {no_doc_count}")


def document_helper(argument):
    is_file = path.isfile(argument)
    if is_file:
        parse_file(argument)
    else:
        java_files = glob.glob(f"{argument}/*.java")
        for file_path in java_files:
            parse_file(file_path)


if __name__ == "__main__":
    document_helper(sys.argv[1])
