# SPDX-FileCopyrightText: 2026 Adafruit Industries
# SPDX-License-Identifier: MIT

"""CPython example of subscribing to the Adafruit IO+ Air Quality Service over MQTT.

This feature is only available to Adafruit IO+ subscribers.

To obtain an Air Quality record ID, visit:
https://io.adafruit.com/services/air_quality
"""

import time
from os import getenv

import adafruit_connection_manager
import adafruit_minimqtt.adafruit_minimqtt as MQTT

from adafruit_io.adafruit_io import IO_MQTT

# Adafruit IO keys (set as environment variables)
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

if not aio_username or not aio_key:
    raise RuntimeError("Missing ADAFRUIT_AIO_USERNAME or ADAFRUIT_AIO_KEY environment variables.")

# Socket/SSL helpers for CPython
radio = adafruit_connection_manager.CPythonNetwork()
socket_pool = adafruit_connection_manager.get_radio_socketpool(radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(radio)

# Air Quality record ID
# (create or view records at https://io.adafruit.com/services/air_quality)
AIR_QUALITY_RECORD_ID = 3

# Available forecast types depend on the service.
# Typical values are "current", "forecast_today", and "forecast_tomorrow".
FORECAST_TYPES = ("current", "forecast_today", "forecast_tomorrow")


def connected(client):
    print("Connected to Adafruit IO!")
    for forecast_type in FORECAST_TYPES:
        print(
            "Subscribing to air quality updates for record",
            AIR_QUALITY_RECORD_ID,
            "forecast:",
            forecast_type,
        )
        client.subscribe_to_air_quality(AIR_QUALITY_RECORD_ID, forecast_type)


def disconnected(client):
    print("Disconnected from Adafruit IO!")


def subscribe(client, userdata, topic, granted_qos):
    print(f"Subscribed to {topic} with QOS level {granted_qos}")


def unsubscribe(client, userdata, topic, pid):
    print(f"Unsubscribed from {topic} with PID {pid}")


def message(client, feed_id, payload):
    # For integration topics, feed_id will usually be "air_quality".
    print(f"{feed_id} update: {payload}")


mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=8883,
    username=aio_username,
    password=aio_key,
    is_ssl=True,
    socket_pool=socket_pool,
    ssl_context=ssl_context,
)

io = IO_MQTT(mqtt_client)

io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_message = message

print("Connecting to Adafruit IO...")
io.connect()

try:
    while True:
        try:
            io.loop()
        except (ValueError, RuntimeError) as e:
            print("Failed to get data, retrying\n", e)
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
