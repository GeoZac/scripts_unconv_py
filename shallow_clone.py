from sys import argv


def shallow_clone(manifest_file: str):
    with open(manifest_file, "r") as file:
        xml_content = file.readlines()

    modified_content = []

    for line in xml_content:
        if "prebuilts/" in line and "clone-depth" not in line:
            line = line.replace(" />", 'clone-depth="1" />')

        modified_content.append(line)

    with open(manifest_file, "w") as file:
        file.writelines(modified_content)


if __name__ == "__main__":
    if len(argv) > 1:
        shallow_clone(argv[1])
    else:
        raise ValueError(
            "Pass mainfest file to slim down",
        )
