# SPDX-FileCopyrightText: 2024 Tyeth Gundry for Adafruit Industries
# SPDX-License-Identifier: MIT

# retrieve user rate info via adafruit_circuitpython_adafruitio with native wifi networking
import time
from os import getenv

import adafruit_connection_manager
import adafruit_requests
import wifi

from adafruit_io.adafruit_io import IO_HTTP

# Get WiFi details and Adafruit IO keys, ensure these are setup in settings.toml
# (visit io.adafruit.com if you need to create an account, or if you need your Adafruit IO key.)
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

print("Connecting to %s" % ssid)
wifi.radio.connect(ssid, password)
print("Connected to %s!" % ssid)

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

print("===============\nUser Rate info:\n===============")
print("\n".join([f"{k:<30}\t=\t{v}" for (k, v) in io.get_user_rate_info().items()]))

print(f"Throttle limit: {io.get_throttle_limit()}")
print(f"Remaining throttle limit: {io.get_remaining_throttle_limit()}")


# # Uncomment these lines to retrieve all user info as one big json object:
# print("Waiting 5seconds before fetching full user info (a lot of JSON output)")
# time.sleep(5)
# try:
#     print("\n\nFull User info:")
#     print(io.get_user_info())
# except MemoryError as me:
#     print(
#         "Board ran out of memory when processing all that user info json."
#         + "This is expected on most boards (ESP32-S3 should work)"
#     )
#     raise me
# except Exception as e:
#     print("Unexpected error!")
#     raise e

print("\n\nDone!")
