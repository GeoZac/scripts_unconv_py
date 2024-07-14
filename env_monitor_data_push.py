import requests

from env_monitor_secrets import BASE_URL, AUTH_KEY


def env_monitor_data_push():
    post_url = BASE_URL + "EnvironmentalReading"
    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "access_token": AUTH_KEY,
    }
    requests.post(
        post_url,
        data=None,
        headers=headers,
        params=params,
    )


if __name__ == "__main__":
    env_monitor_data_push()
