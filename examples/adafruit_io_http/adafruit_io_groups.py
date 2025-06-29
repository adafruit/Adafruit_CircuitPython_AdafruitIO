# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Adafruit IO HTTP API - Group Interactions
# Documentation: https://io.adafruit.com/api/docs/#groups
# adafruit_circuitpython_adafruitio with an esp32spi_socket
from os import getenv

import adafruit_connection_manager
import adafruit_datetime as datetime
import adafruit_requests
import board
import busio
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut

from adafruit_io.adafruit_io import IO_HTTP

# Get WiFi details and Adafruit IO keys, ensure these are setup in settings.toml
# (visit io.adafruit.com if you need to create an account, or if you need your Adafruit IO key.)
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# If you have an externally connected ESP32:
# esp32_cs = DigitalInOut(board.D9)
# esp32_ready = DigitalInOut(board.D10)
# esp32_reset = DigitalInOut(board.D5)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(ssid, password)
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ap_info.ssid, "utf-8"), "\tRSSI:", esp.ap_info.rssi)

# If you are using a wifi based mcu use this instead of esp code above, remove the from
# adafruit_esp32spi import line, optionally esp.connect(ssid, password)
# import wifi
# esp = wifi.radio

# Initialize a requests session
pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
requests = adafruit_requests.Session(pool, ssl_context)

# If you are testing on python with blinka, use real requests below and comment out above:
# import os, datetime, requests as real_requests
# from adafruit_io.adafruit_io import IO_HTTP
# requests = real_requests.Session()

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

# Create a new group
print("Creating a new Adafruit IO Group...")
sensor_group = io.create_new_group("envsensors", "a group of environmental sensors")

# Create the 'temperature' feed in the group
print("Creating feed temperature inside group...")
io.create_feed_in_group(sensor_group["key"], "temperature")

# Create the 'humidity' feed then add to group (it will still be in Default group too)
print("Creating feed humidity then adding to group...")
humidity_feed = io.create_new_feed("humidity", "a feed for humidity data")
io.add_feed_to_group(sensor_group["key"], humidity_feed["key"])

# show humidity feed is in two groups
print("Getting fresh humidity feed info... (notice groups)")
print(io.get_feed(humidity_feed["key"]))

# fetch current time
print("Fetching current time from IO... ", end="")
year, month, day, hour, minute, second, *_ = io.receive_time(timezone="UTC")
old_time = datetime.datetime(year, month, day, hour, minute, second)
print(old_time.isoformat())

# Publish data for multiple feeds to a group, use different timestamps for no reason
print("Publishing batch data to group feeds with created_at set 99minutes ago...")
thetime = old_time - datetime.timedelta(minutes=99)
print(thetime)

io.send_group_data(
    group_key=sensor_group["key"],
    feeds_and_data=[
        {"key": "temperature", "value": 20.0},
        {"key": "humidity", "value": 40.0},
    ],
    metadata={
        "lat": 50.1858942,
        "lon": -4.9677478,
        "ele": 4,
        "created_at": thetime.isoformat(),
    },
)

# Get info from the group
print("Getting fresh group info... (notice created_at vs updated_at)")
sensor_group = io.get_group("envsensors")  # refresh data via HTTP API
print(sensor_group)

# Delete the group
print("Deleting group...")
io.delete_group("envsensors")

# Delete the remaining humidity feed (it was in Two Groups so not deleted with our group)
print("Deleting feed humidity (still in default group)...")
io.delete_feed(humidity_feed["key"])
