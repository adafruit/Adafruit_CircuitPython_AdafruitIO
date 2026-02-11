# SPDX-FileCopyrightText: 2026 Adafruit Industries
# SPDX-License-Identifier: MIT

# CPython version of the Adafruit IO MQTT time example.
#
# This example runs on a computer (CPython) instead of CircuitPython hardware.
# It uses adafruit_connection_manager.CPythonNetwork to provide the socket pool
# and SSL context for adafruit_minimqtt.

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

# Socket/SSL helper for CPython
radio = adafruit_connection_manager.CPythonNetwork()
socket_pool = adafruit_connection_manager.get_radio_socketpool(radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(radio)

TIME_TOPICS = ("seconds", "millis", "iso", "hours")


def connected(client):
    print("Connected to Adafruit IO!")
    for time_topic in TIME_TOPICS:
        client.subscribe_to_time(time_topic)


def disconnected(client):
    print("Disconnected from Adafruit IO!")


def subscribe(client, userdata, topic, granted_qos):
    print(f"Subscribed to {topic} with QOS level {granted_qos}")


def unsubscribe(client, userdata, topic, pid):
    print(f"Unsubscribed from {topic} with PID {pid}")


def message(client, topic_name, payload):
    # For time topics, topic_name will be the suffix like 'seconds'/'iso'.
    print(f"Time {topic_name}: {payload}")


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
        print("Use Ctrl-C to unsubscribe and disconnect...")
        time.sleep(1)
    # Normal loop ends here. Use Ctrl-C to Unsubscribe and disconnect/exit.

except KeyboardInterrupt:
    try:
        print("\nKeyboardInterrupt: processing pending messages before disconnecting...")
        io.loop()
    except Exception:
        pass
    print("\nUnsubscribing from time topics and disconnecting...")
    for time_topic in TIME_TOPICS:
        try:
            print("Processing messages... (io.loop())")
            io.loop()
            print("Processing complete.")
        except Exception:
            pass
        try:
            print(f"Unsubscribing from time topic '{time_topic}'...")
            io.unsubscribe_from_time(time_topic)
            print(f"Successfully unsubscribed from time topic '{time_topic}'.")
        except Exception as e:
            print(f"Failed to unsubscribe from time topic '{time_topic}':", e)
            try:
                io.reconnect()
                io.loop()
                print(f"Unsubscribing from time topic '{time_topic}'...")
                io.unsubscribe_from_time(time_topic)
                print(f"Successfully unsubscribed from time topic '{time_topic}'.")
            except Exception as e:
                print(f"Failed to unsubscribe from time topic '{time_topic}':", e)

    # loop for another 3s collecting io loop messages
    print("Processing final messages for 3 seconds...")
    for _ in range(3):
        try:
            io.loop()
        except Exception as e:
            print("Failed to get data, retrying\n", e)
            continue
        time.sleep(1)
    io.disconnect()
