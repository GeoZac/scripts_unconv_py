import sys
from app_config import *
from requests import Response, get, post
from json import dumps

HTTP_TIMEOUT = 5


def print_as_header(header):
    print("*******************************")
    print(header)
    print("*******************************")


def handle_app_found(reponse: Response):
    status_code = reponse.status_code
    if status_code == 404:
        print("App not found")
    sys.exit()


def handle_improper_login(response: Response):
    status_code = response.status_code
    print(status_code)
    if status_code == 400:
        print("Check credentials")
    sys.exit()


def run_version_check():
    print_as_header("Version check")
    response = get(
        BASE_URL + VERS_CHK,
        timeout= HTTP_TIMEOUT
    )
    if response.status_code != 200:
        handle_app_found(response)
    print("Status code", response.status_code)
    print("App version", response.content.decode())


def login():
    creads = {"username": USERNAME, "password": PASSWORD}

    response = post(BASE_URL + AUTH_END, dumps(creads), timeout=HTTP_TIMEOUT)
    if response.status_code != 200:
        handle_improper_login(response)
    json_resp = response.json()
    unconv_user = json_resp["unconvUser"]
    print_as_header("Logged in as user")
    print("Username", unconv_user["username"])
    print("E-mail  ", unconv_user["email"])
    token = json_resp["token"]

    return token, unconv_user


def run_app_checks():
    run_version_check()
    token, user = login()


if __name__ == "__main__":
    run_app_checks()
