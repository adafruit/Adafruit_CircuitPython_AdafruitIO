# SPDX-FileCopyrightText: 2024 Tyeth Gundry for Adafruit Industries
# SPDX-License-Identifier: MIT

# adafruit_circuitpython_adafruitio usage for batch data with a CPython socket.
import datetime
import socket
import ssl
from os import getenv
from random import randint

import adafruit_requests

from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

# Get WiFi details and Adafruit IO keys, ensure these are setup in settings.toml
# (visit io.adafruit.com if you need to create an account, or if you need your Adafruit IO key.)
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

requests = adafruit_requests.Session(socket, ssl.create_default_context())
# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

try:
    # Get the 'temperature' feed from Adafruit IO
    temperature_feed = io.get_feed("batch-temperature")
except AdafruitIO_RequestError:
    # If no 'temperature' feed exists, create one
    temperature_feed = io.create_new_feed("batch-temperature")

# Get current time from Adafruit IO time service (in UTC)
years, months, days, hours, minutes, seconds, *_ = io.receive_time("UTC")
current_time = datetime.datetime(years, months, days, hours, minutes, seconds)
print("Current time from Adafruit IO: ", current_time)

# Create random values at different timestamps to send to the feed
data = []
for i in range(5):
    random_value = randint(0, 50)
    time_offset = i - 5
    created_at = current_time + datetime.timedelta(seconds=time_offset)
    print(
        f"Adding datapoint {random_value} (at T:{time_offset}) to collection for batch-temperature feed..."  # noqa: E501
    )
    data.append(
        {
            "value": random_value,
            "created_at": created_at.isoformat(),  # optional metadata like lat, lon, ele, etc
        }
    )

# Send the data to the feed as a single batch
io.send_batch_data(temperature_feed["key"], data)
print("Data sent!")
print()
print(
    "View your feed graph at: https://io.adafruit.com/{0}/feeds/{1}".format(
        aio_username, temperature_feed["key"]
    )
)
print()

# Retrieve data value from the feed
print("Retrieving data from batch-temperature feed...")
received_data = io.receive_data(temperature_feed["key"])
print("Data from temperature feed: ", received_data["value"])
