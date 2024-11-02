import os
import sys

def check_test_files(root_dir):
    lib_dir = os.path.join(root_dir, "lib")
    test_dir = os.path.join(root_dir, "test")
    test_suffix = "_test.dart"

    lib_files = []
    for root, dirs, files in os.walk(lib_dir):
        for file in files:
            if file.endswith(".dart"):
                relative_path = os.path.relpath(os.path.join(root, file), lib_dir)
                lib_files.append(relative_path)

    missing_tests = []
    incorrect_test_files = []

    for lib_file in lib_files:
        test_file = os.path.join(test_dir, lib_file)

        if not os.path.exists(test_file):
            missing_tests.append(lib_file)
        else:
            test_file_name = os.path.basename(test_file)
            print(test_file_name)
            if not test_file_name.endswith(test_suffix):
                incorrect_test_files.append(test_file)

    if missing_tests:
        print("Files missing corresponding test files:")
        for file in missing_tests:
            print(f"  - {file}")
    else:
        print("All lib files have corresponding test files.")

    if incorrect_test_files:
        print("\nTest files without the correct suffix:")
        for file in incorrect_test_files:
            print(f"  - {file}")
    else:
        print("All test files have the correct '_test' suffix.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_tests.py <path_to_flutter_project>")
        sys.exit(1)

    root_directory = sys.argv[1]
    check_test_files(root_directory)
