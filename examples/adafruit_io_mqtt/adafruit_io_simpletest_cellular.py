# SPDX-FileCopyrightText: Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Brent Rubell for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example of using the Adafruit IO CircuitPython MQTT client
# to subscribe to an Adafruit IO feed and publish random data
# to be received by the feed.
import time
from os import getenv
from random import randint

import adafruit_connection_manager
import adafruit_fona.adafruit_fona_socket as pool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import board
import busio
import digitalio
from adafruit_fona.adafruit_fona import FONA
from adafruit_fona.adafruit_fona_gsm import GSM

from adafruit_io.adafruit_io import IO_MQTT

# Get Fona details and Adafruit IO keys, ensure these are setup in settings.toml
# (visit io.adafruit.com if you need to create an account, or if you need your Adafruit IO key.)
apn = getenv("apn")
apn_username = getenv("apn_username")
apn_password = getenv("apn_password")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

# Create a serial connection for the FONA connection
uart = busio.UART(board.TX, board.RX)
rst = digitalio.DigitalInOut(board.D4)

# Initialize FONA module (this may take a few seconds)
fona = FONA(uart, rst)

# initialize gsm
gsm = GSM(fona, (apn, apn_username, apn_password))

while not gsm.is_attached:
    print("Attaching to network...")
    time.sleep(0.5)

while not gsm.is_connected:
    print("Connecting to network...")
    gsm.connect()
    time.sleep(5)


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print("Connected to Adafruit IO!  Listening for DemoFeed changes...")
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe("DemoFeed")


def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print(f"Subscribed to {topic} with QOS level {granted_qos}")


def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a feed.
    print(f"Unsubscribed from {topic} with PID {pid}")


def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")


def publish(client, userdata, topic, pid):
    # This method is called when the client publishes data to a feed.
    print(f"Published to {topic} with PID {pid}")
    if userdata is not None:
        print("Published User data: ", end="")
        print(userdata)


def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print(f"Feed {feed_id} received new value: {payload}")


ssl_context = adafruit_connection_manager.create_fake_ssl_context(pool, fona)

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
io.on_publish = publish

# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()

# Below is an example of manually publishing a new  value to Adafruit IO.
last = 0
print("Publishing a new message every 10 seconds...")
while True:
    # Explicitly pump the message loop.
    io.loop()
    # Send a new message every 10 seconds.
    if (time.monotonic() - last) >= 5:
        value = randint(0, 100)
        print(f"Publishing {value} to DemoFeed.")
        io.publish("DemoFeed", value)
        last = time.monotonic()
