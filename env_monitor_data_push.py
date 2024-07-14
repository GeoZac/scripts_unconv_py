import requests
import json
import sys

from env_monitor_secrets import BASE_URL, AUTH_KEY

def validate_payload(data):
    temp_value = data.get("temperature", None)
    humi_value = data.get("humidity", None)
    ssid_value = data['sensorSystem'].get("id", None)

    if not (temp_value and humi_value and ssid_value):
        print("Incomplete payload")
        sys.exit(0)

def env_monitor_data_push():
    post_data = {
        "temperature": None,
        "humidity": None,
        "sensorSystem": {
            "id": None,
        },
    }
    validate_payload(post_data)
    post_data_to_web_app(
        json.dumps(post_data),
    )


def post_data_to_web_app(data):
    post_url = BASE_URL + "EnvironmentalReading"
    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "access_token": AUTH_KEY,
    }
    requests.post(
        post_url,
        data=data,
        headers=headers,
        params=params,
    )


if __name__ == "__main__":
    env_monitor_data_push()
