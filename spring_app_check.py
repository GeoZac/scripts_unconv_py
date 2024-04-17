import sys
from app_config import *
from requests import Response, get, post
from json import dumps
from app_utils import display_sensor_table, get_expiry_duration

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


def fetch_sensor_token(sensor_id, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    response = get(
        BASE_URL + SEN_AUTH + sensor_id,
        timeout=HTTP_TIMEOUT,
        headers=headers,
    )
    if response.status_code == 200:
        resp_json = response.json()
        print(
            sensor_id,
            resp_json["authToken"],
            resp_json["expiry"],
            get_expiry_duration(
                resp_json["expiry"],
            ),
            sep="\t",
        )


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
        timeout=HTTP_TIMEOUT,
    )
    if response.status_code != 200:
        handle_app_found(response)
    print("Status code :", response.status_code)
    print("App version :", response.content.decode())


def login():
    creads = {
        "username": USERNAME,
        "password": PASSWORD,
    }

    response = post(
        BASE_URL + AUTH_END,
        dumps(creads),
        timeout=HTTP_TIMEOUT,
    )
    if response.status_code != 200:
        handle_improper_login(response)
    json_resp = response.json()
    unconv_user = json_resp["unconvUser"]
    print_as_header("Logged in as user")
    print("Username:", unconv_user["username"])
    print("E-mail  :", unconv_user["email"])
    token = json_resp["token"]

    return token, unconv_user


def list_sensor_auth_tokens(sensors, token):
    print_as_header("Sensor auth tokens")
    for sensor in sensors:
        sensor_id = sensor["id"]
        fetch_sensor_token(
            sensor_id,
            token,
        )


def list_sensor_systems(user_id, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    response = get(
        BASE_URL + USER_SEN + user_id,
        headers=headers,
        timeout=HTTP_TIMEOUT,
    )
    json_resp = response.json()
    print_as_header("Sensor Info")
    print("Sensor Count:", json_resp["totalElements"])
    display_sensor_table(json_resp["data"])
    return json_resp["data"]


def run_app_checks():
    run_version_check()
    token, user = login()
    sensors = list_sensor_systems(
        user["id"],
        token,
    )
    list_sensor_auth_tokens(
        sensors,
        token,
    )


if __name__ == "__main__":
    run_app_checks()
