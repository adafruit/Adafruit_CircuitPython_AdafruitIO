# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# adafruit_circuitpython_adafruitio usage with native wifi networking
from os import getenv
from random import randint

import adafruit_connection_manager
import adafruit_requests
import wifi

from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

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

try:
    # Get the 'temperature' feed from Adafruit IO
    temperature_feed = io.get_feed("temperature")
except AdafruitIO_RequestError:
    # If no 'temperature' feed exists, create one
    temperature_feed = io.create_new_feed("temperature")

# Send random integer values to the feed
random_value = randint(0, 50)
print(f"Sending {random_value} to temperature feed...")
io.send_data(temperature_feed["key"], random_value)
print("Data sent!")

# Retrieve data value from the feed
print("Retrieving data from temperature feed...")
received_data = io.receive_data(temperature_feed["key"])
print("Data from temperature feed: ", received_data["value"])
