import sys
from app_config import *
from requests import Response, get


def print_as_header(header):
    print("*******************************")
    print(header)
    print("*******************************")


def handle_app_found(reponse: Response):
    status_code = reponse.status_code
    if status_code == 404:
        print("App not found")
    sys.exit()


def run_version_check():
    print_as_header("Version check")
    response = get(
        BASE_URL + VERS_CHK,
    )
    if response.status_code != 200:
        handle_app_found(response)
    print("Status code", response.status_code)
    print("App version", response.content.decode())


def run_app_checks():
    run_version_check()


if __name__ == "__main__":
    run_app_checks()
