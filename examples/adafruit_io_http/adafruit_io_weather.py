# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example of using the Adafruit IO+ Weather Service
# adafruit_circuitpython_adafruitio with an esp32spi_socket
from os import getenv

import adafruit_connection_manager
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

# Initialize a requests session
pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
requests = adafruit_requests.Session(pool, ssl_context)

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

# Weather Location ID
# (to obtain this value, visit
# https://io.adafruit.com/services/weather
# and copy over the location ID)
location_id = 2127

print("Getting forecast from IO...")
# Fetch the specified record with current weather
# and all available forecast information.
forecast = io.receive_weather(location_id)

# Get today's forecast
current_forecast = forecast["current"]
print("It is {0} and {1}*F.".format(current_forecast["summary"], current_forecast["temperature"]))
print("with a humidity of {0}%".format(current_forecast["humidity"] * 100))

# Get tomorrow's forecast
tom_forecast = forecast["forecast_days_1"]
print(
    "\nTomorrow has a low of {0}*F and a high of {1}*F.".format(
        tom_forecast["temperatureLow"], tom_forecast["temperatureHigh"]
    )
)
print("with a humidity of {0}%".format(tom_forecast["humidity"] * 100))
