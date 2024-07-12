import requests

BASE_URL = "https://release.axocdn.com/linux/gitkraken-amd64.rpm"


def check_gitkraken_release():
    response = requests.head(
        BASE_URL,
        timeout=5,
    )

    resp_headers = response.headers
    print(
        resp_headers["last-modified"],
    )
    print(
        round(
            int(
                resp_headers["Content-Length"],
            )
            / (1024 * 1024),
            ndigits=2,
        ),
        "MB",
    )


if __name__ == "__main__":
    check_gitkraken_release()
