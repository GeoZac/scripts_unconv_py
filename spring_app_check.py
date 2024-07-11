import sys
from app_config import *
from app_constants import VERS_CHK, AUTH_END, USER_SEN, SEN_AUTH, SENS_RDS, RECE_RDS
from requests import Response, get, post
from json import dumps
from app_utils import display_sensor_table, get_expiry_duration, shuffle_string

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


def test_username_checks():
    headers = {
        "Content-Type": "application/json",
    }
    usernames = [
        USERNAME,
    ]
    for i in range(0, 5):
        usernames.append(
            generate_random_string(
                length=7,
            )
        )
    for username in usernames:
        response = get(
            BASE_URL + USNM_CHK + username,
            timeout=HTTP_TIMEOUT,
            headers=headers,
        )
        print(
            username,
            "-",
            response.json()["available"],
            sep="\t",
        )


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
    elif response.status_code == 204:
        print(
            sensor_id,
            "No SensorAuthToken generated",
            sep="\t"
        )


def handle_improper_login(
    response: Response,
    should_exit: bool = True,
):
    status_code = response.status_code
    print(status_code)
    if status_code == 400:
        print("Check credentials")

    if not should_exit:
        return
    sys.exit()


def fetch_readings(sensor_id, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    params = {
        "pageNo": 0,
        "sortDir": "desc",
        "sortBy": "timestamp",
        "pageSize": 100,
    }
    response = get(
        BASE_URL + SENS_RDS + sensor_id,
        headers=headers,
        timeout=HTTP_TIMEOUT,
        params=params,
    )
    resp_json = response.json()


def list_recent_readings(user_id, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    response = get(
        BASE_URL + RECE_RDS + user_id,
        headers=headers,
        timeout=HTTP_TIMEOUT,
    )
    json_resp = response.json()
    print_as_header("Recent readings")
    print("Time elapsed:", response.elapsed)
    print("Readings count:", len(json_resp))
    for item in json_resp:
        print(
            item["timestamp"],
            item["temperature"],
            item["humidity"],
            item["sensorSystem"]["id"],
            item["sensorSystem"]["sensorName"],
            sep="\t",
        )
    return None


def run_version_check():
    print_as_header("Version check")
    response = get(
        BASE_URL + VERS_CHK,
        timeout=HTTP_TIMEOUT,
    )
    if response.status_code != 200:
        handle_app_found(response)
    print("Status code :", response.status_code)
    print("Time elapsed:", response.elapsed)
    print("App version :", response.content.decode())


def test_unathorised_login():
    creads = {
        "username": USERNAME,
        "password": shuffle_string(
            PASSWORD,
        ),
    }

    response = post(
        BASE_URL + AUTH_END,
        dumps(creads),
        timeout=HTTP_TIMEOUT,
    )
    if response.status_code != 200:
        handle_improper_login(
            response,
            False,
        )


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
    print("Time elapsed:", response.elapsed)
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
    print("Time elapsed:", response.elapsed)
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
