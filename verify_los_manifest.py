from sys import argv
import xml.etree.ElementTree as ET


def veify_los_remote(manifest_file: str):
    tree = ET.parse(manifest_file)
    root = tree.getroot()
    for item in root.findall("project"):
        name = item.attrib["name"]
        remote = None
        try:
            remote = item.attrib["remote"]
        except KeyError:
            pass
        if "LineageOS/" in name and remote is None:
            print("Missing remote => " + name)


if __name__ == "__main__":
    if len(argv) > 1:
        veify_los_remote(argv[1])
    else:
        raise ValueError(
            "Pass mainfest file to verify",
        )
