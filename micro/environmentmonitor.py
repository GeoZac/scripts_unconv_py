import network
import ujson
import urequests
import utime as time
from dht import DHT11, InvalidPulseCount
from machine import Pin

from envtmonitorconfig import SSID, PASSWORD, ENDPOINT_URL

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
foo = network.WLAN.scan(wlan)
print(foo)
while wlan.isconnected() is False:
    wlan.connect(tmconfig.SSID, tmconfig.PASSWORD)
    print(wlan.ifconfig())
    time.sleep(10)


def upload_to_render(sensor_data):
    if wlan.isconnected() is False:
        return

    local_datetime = time.localtime()
    timestamp = time.mktime(local_datetime)
    current_time = local_datetime

    # Format the tuple into a string in the format "YYYY-MM-DDTHH:MM:SS"
    time_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        current_time[0],
        current_time[1],
        current_time[2],
        current_time[3],
        current_time[4],
        current_time[5],
    )

    print("Timestring: ", time_string)

    url = tmconfig.ENDPOINT_URL

    # Set the headers and payload for the POST request
    headers = {"Content-Type": "application/json"}

    payload = {
        "temperature": sensor_data.temperature,
        "humidity": sensor_data.humidity,
        "timestamp": time_string,
    }

    data_str = ujson.dumps(payload)

    # Make the POST request
    try:
        response = urequests.post(url, headers=headers, data=data_str)
    except Exception:
        return False

    # Print the response
    print(response.content)

    # Release the resources associated with the response
    response.close()

    return True


while True:
    time.sleep(1)
    pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
    sensor = DHT11(pin)
    try:
        t = sensor.temperature
        h = sensor.humidity
        print("Temperature: {}".format(sensor.temperature))
        print("Humidity: {}".format(sensor.humidity))

        print("Initiate  upload")
        sucess = upload_to_render(sensor)

        if sucess:
            time.sleep(5 * 50)
    except InvalidPulseCount:
        print("Sensor failed to provide readings")
