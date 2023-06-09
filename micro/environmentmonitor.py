import re
import network
import ntptime
import ujson
import urequests
import utime as time
from machine import Pin, I2C

from dht import DHT11, InvalidChecksum, InvalidPulseCount
from envtmonitorconfig import SSID, PASSWORD, ENDPOINT_URL, ACCESS_TOKEN, SENSOR_SYSTEM_ID, ACCESS_POINTS
from pico_i2c_lcd import I2cLcd
from sh1106 import SH1106_I2C

WIDTH = 128
HEIGHT = 64

try:
    i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=200000)
    print("I2C Address      : " + hex(i2c.scan()[0]).upper())
    print("I2C Configuration: " + str(i2c))
    oled = SH1106_I2C(WIDTH, HEIGHT, i2c)
except IndexError:
    oled = None

try:
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    print("I2C Address      : " + hex(i2c.scan()[0]).upper())
    print("I2C Configuration: " + str(i2c))
    I2C_ADDR = i2c.scan()[0]
    lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)
except IndexError:
    lcd = None


def push_to_lcd_display(text_string, timeout=5):
    lcd.backlight_on()
    lcd.putstr(text_string)
    time.sleep(timeout)
    lcd.clear()
    lcd.backlight_off()


def push_to_display(text_string, timeout=5):
    if lcd:
        push_to_lcd_display(text_string)
    if not oled:
        return
    oled.text(text_string, 5, 5)
    oled.show()
    time.sleep(timeout)
    oled.fill(0)
    oled.show()


def match_available_ap_with_scan_results(results):
    if SSID is not None and PASSWORD is not None:
        return SSID, PASSWORD
    for result in results:
        ap_name = result[0].decode('UTF-8')
        if any(re.search(known_ap, ap_name) for known_ap in ACCESS_POINTS):
            ssid_name = ap_name
            ssid_pass = ACCESS_POINTS[ap_name]
            return ssid_name, ssid_pass


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
scan_results = network.WLAN.scan(wlan)
print(scan_results)
ssid, password = match_available_ap_with_scan_results(scan_results)
while wlan.isconnected() is False:
    wlan.connect(ssid, password)
    print(wlan.ifconfig())
    time.sleep(10)
    push_to_display(wlan.ifconfig()[3])

push_to_display("Setting time")
try:
    # if needed, overwrite default time server
    ntptime.host = "1.europe.pool.ntp.org"
    push_to_display("Syncing time")
    print("Local time before synchronization：%s" % str(time.localtime()))
    ntptime.settime()
    print("Local time after synchronization：%s" % str(time.localtime()))
    push_to_display("Time set from NTP")
except:
    print("Error syncing time")
    push_to_display("Time failed")


def upload_to_render(sensor_data):
    if wlan.isconnected() is False:
        push_to_display("No network")
        return False

    local_datetime = time.localtime()
    timestamp = time.mktime(local_datetime)
    current_time = local_datetime

    # Format the tuple into a string in the format "YYYY-MM-DDTHH:MM:SS"
    time_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
        current_time[0],
        current_time[1],
        current_time[2],
        current_time[3],
        current_time[4],
        current_time[5],
    )

    hint = "Current UTC time    "
    push_to_display(hint + time_string)

    print("Timestring: ", time_string)

    url = ENDPOINT_URL

    # Set the headers and payload for the POST request
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + ACCESS_TOKEN,
    }

    payload = {
        "temperature": sensor_data.temperature,
        "humidity": sensor_data.humidity,
        "timestamp": time_string,
        "sensorSystem": {
            "id": SENSOR_SYSTEM_ID
        }
    }

    data_str = ujson.dumps(payload)

    # Make the POST request
    push_to_display("Posting data to web application")
    try:
        response = urequests.post(url, headers=headers, data=data_str)
    except Exception:
        return False

    # Print the response
    print(response.content)
    if not response.status_code == 201:
        print(response.status_code)
        push_to_display("API Request failed")
        return False

    json_format = response.json()
    print(str(json_format['entity']['timestamp']).split("T")[1])
    string_0 = "Success! POSTed data"
    string_1 = "Temperature:    " + str(json_format['entity']['temperature'])
    string_2 = "Humidity   :    " + str(json_format['entity']['humidity'])
    string_3 = "UTC Time   :" + \
               str(json_format['entity']['timestamp']).split("T")[1].strip("Z")
    string_4 = "Sensor System : " + \
               str(json_format['entity']['sensorSystem']['id'])
    string = string_0 + string_1 + string_2 + string_3
    push_to_display(string, timeout=10)

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
        success = upload_to_render(sensor)

        if success:
            time.sleep(5 * 50)
    except InvalidChecksum:
        print("Sensor failed to provide readings")
    except InvalidPulseCount:
        print("Sensor failed to provide readings")
