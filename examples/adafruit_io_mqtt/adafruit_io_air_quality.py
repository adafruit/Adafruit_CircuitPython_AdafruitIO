# SPDX-FileCopyrightText: 2026 Adafruit Industries
# SPDX-License-Identifier: MIT

"""Example of subscribing to the Adafruit IO+ Air Quality Service over MQTT.

This feature is only available to Adafruit IO+ subscribers.

To obtain an Air Quality record ID, visit:
https://io.adafruit.com/services/air_quality
"""

import time
from os import getenv

import adafruit_connection_manager
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import board
import busio
import neopixel
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
from digitalio import DigitalInOut

from adafruit_io.adafruit_io import IO_MQTT

# Get WiFi details and Adafruit IO keys, ensure these are setup in settings.toml
# (visit io.adafruit.com if you need to create an account, or if you need your Adafruit IO key.)
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

### WiFi ###

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
"""Use below for Most Boards"""
status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)  # Uncomment for Most Boards
"""Uncomment below for ItsyBitsy M4"""
# status_pixel = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)
# Uncomment below for an externally defined RGB LED
# import adafruit_rgbled
# from adafruit_esp32spi import PWMOut
# RED_LED = PWMOut.PWMOut(esp, 26)
# GREEN_LED = PWMOut.PWMOut(esp, 27)
# BLUE_LED = PWMOut.PWMOut(esp, 25)
# status_pixel = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)
wifi = adafruit_esp32spi_wifimanager.WiFiManager(esp, ssid, password, status_pixel=status_pixel)

# Air Quality record ID
# (create or view records at https://io.adafruit.com/services/air_quality)
AIR_QUALITY_RECORD_ID = 0

# Available forecast types depend on the service.
# Typical values are "current", "forecast_today", and "forecast_tomorrow".
FORECAST_TYPES = ("current", "forecast_today", "forecast_tomorrow")


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to topics.
    print("Connected to Adafruit IO!")

    for forecast_type in FORECAST_TYPES:
        print(
            "Subscribing to air quality updates for record",
            AIR_QUALITY_RECORD_ID,
            "forecast:",
            forecast_type,
        )
        io.subscribe_to_air_quality(AIR_QUALITY_RECORD_ID, forecast_type)


def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")


def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new topic.
    print(f"Subscribed to {topic} with QOS level {granted_qos}")


def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a topic.
    print(f"Unsubscribed from {topic} with PID {pid}")


def message(client, feed_id, payload):
    # Message function will be called when a subscribed topic has a new value.
    # For integration topics, feed_id may be a short identifier like "air_quality".
    print(f"{feed_id} received new value: {payload}")


# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")

pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=aio_username,
    password=aio_key,
    socket_pool=pool,
    ssl_context=ssl_context,
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# Connect the callback methods defined above to Adafruit IO
io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_message = message

# Connect to Adafruit IO
io.connect()


# Start a blocking message loop...
# NOTE: Network reconnection is handled within this loop
try:
    while True:
        try:
            io.loop()
        except (ValueError, RuntimeError) as e:
            print("Failed to get data, retrying\n", e)
            wifi.reset()
            io.reconnect()
            continue
        time.sleep(1)
except KeyboardInterrupt:
    print("\nKeyboardInterrupt: unsubscribing from air quality topics and disconnecting...")
    for forecast_type in FORECAST_TYPES:
        try:
            io.unsubscribe_from_air_quality(AIR_QUALITY_RECORD_ID, forecast_type)
        except Exception as e:
            print(f"Failed to unsubscribe from forecast '{forecast_type}':", e)
    io.disconnect()
