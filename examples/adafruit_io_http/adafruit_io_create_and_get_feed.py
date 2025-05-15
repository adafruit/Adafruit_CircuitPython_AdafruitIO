# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
Example using create_and_get_feed. Creates a new feed if it does not exist and sends to it, or
sends to an existing feed once it has been created.
"""

from os import getenv

import adafruit_connection_manager
import adafruit_requests
import microcontroller
import wifi

from adafruit_io.adafruit_io import IO_HTTP

# Get WiFi details and Adafruit IO keys, ensure these are setup in settings.toml
# (visit io.adafruit.com if you need to create an account, or if you need your Adafruit IO key.)
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

# Connect to Wi-Fi using credentials from settings.toml
wifi.radio.connect(ssid, password)
print(f"Connected to {ssid}!")
print("IP:", wifi.radio.ipv4_address)

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

# Create temperature variable using the CPU temperature and print the current value.
temperature = microcontroller.cpu.temperature
print(f"Current CPU temperature: {temperature} C")

# Create and get feed.
io.send_data(io.create_and_get_feed("cpu-temperature-feed")["key"], temperature)
