# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Turn on and off a LED from your Adafruit IO Dashboard.
# adafruit_circuitpython_adafruitio with an esp32spi_socket
import time
from os import getenv

import adafruit_connection_manager
import adafruit_requests
import board
import busio
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut, Direction

from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

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

# Initialize a requests session
pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
requests = adafruit_requests.Session(pool, ssl_context)

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

try:
    # Get the 'digital' feed from Adafruit IO
    digital_feed = io.get_feed("digital")
except AdafruitIO_RequestError:
    # If no 'digital' feed exists, create one
    digital_feed = io.create_new_feed("digital")

# Set up LED
LED = DigitalInOut(board.D13)
LED.direction = Direction.OUTPUT

while True:
    # Get data from 'digital' feed
    print("getting data from IO...")
    feed_data = io.receive_data(digital_feed["key"])

    # Check if data is ON or OFF
    if int(feed_data["value"]) == 1:
        print("received <- ON\n")
    elif int(feed_data["value"]) == 0:
        print("received <= OFF\n")

    # Set the LED to the feed value
    LED.value = int(feed_data["value"])

    time.sleep(5)
