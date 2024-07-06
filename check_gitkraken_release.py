import requests

BASE_URL = "https://release.axocdn.com/linux/gitkraken-amd64.rpm"

response = requests.head(
    BASE_URL,
    timeout=5,
)

resp_headers = response.headers
print(
    resp_headers['last-modified']
)
