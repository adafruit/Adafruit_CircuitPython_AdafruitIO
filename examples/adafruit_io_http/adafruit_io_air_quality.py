# SPDX-FileCopyrightText: 2026 Adafruit Industries
# SPDX-License-Identifier: MIT

# Example of using the Adafruit IO+ Air Quality Service
# adafruit_circuitpython_adafruitio with an esp32spi_socket
from os import getenv

import adafruit_connection_manager
import adafruit_requests
import board
import busio
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut

from adafruit_io.adafruit_io import IO_HTTP

# # Get WiFi details and Adafruit IO keys, ensure these are setup in settings.toml
# # (visit io.adafruit.com if you need to create an account, or if you need your Adafruit IO key.)
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

# Air Quality Location ID
# (to obtain this value, visit
# https://io.adafruit.com/services/air_quality
# and copy over the location ID, or create a new location using create_air_quality)

# Example: Create a new air quality location
# new_location = io.create_air_quality(
#     "40.7128,-74.0060", name="New York City", provider="open_meteo"
# )
# location_id = new_location["id"]
# print(f"Created new air quality location with ID: {location_id}")

# Or use an existing location ID
location_id = 2

print("Getting air quality data from IO...")
# Fetch the specified record with current air quality
# and all available forecast information.
air_quality_data = io.receive_air_quality(location_id)

# Get current air quality
current = air_quality_data.get("current", {})
if current:
    print(f"Current Air Quality Index: {current.get('aqi', 'N/A')}")
    print(f"PM2.5: {current.get('pm2_5', 'N/A')} μg/m³")
    print(f"PM10: {current.get('pm10', 'N/A')} μg/m³")
    print(f"Ozone (O3): {current.get('ozone', 'N/A')} μg/m³")
    print(f"Nitrogen Dioxide (NO2): {current.get('nitrogen_dioxide', 'N/A')} μg/m³")

# Get hourly forecast
hourly = air_quality_data.get("hourly", [])
if hourly and len(hourly) > 0:
    next_hour = hourly[0]
    print(f"\nNext hour forecast:")
    print(f"PM2.5: {next_hour.get('pm2_5', 'N/A')} μg/m³")
    print(f"AQI: {next_hour.get('aqi', 'N/A')}")

# Get all air quality locations
print("\nAll air quality locations:")
all_locations = io.get_air_quality()
for loc in all_locations:
    print(f"  - {loc.get('name', 'Unnamed')} (ID: {loc['id']})")
