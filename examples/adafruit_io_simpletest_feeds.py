"""
Example of interacting with Adafruit IO feeds
"""
import board
import busio
from digitalio import DigitalInOut

# ESP32 SPI
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import NeoPixel Library
import neopixel

# Import Adafruit IO REST Client
from adafruit_io.adafruit_io import RESTClient

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# ESP32 Setup
esp32_cs = DigitalInOut(board.D9)
esp32_ready = DigitalInOut(board.D10)
esp32_reset = DigitalInOut(board.D5)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
"""Use below for Most Boards"""
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2) # Uncomment for Most Boards
"""Uncomment below for ItsyBitsy M4"""
#status_light = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

"""
# PyPortal ESP32 Setup
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
"""

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets['aio_username']
aio_key = secrets['aio_key']

# Create an instance of the Adafruit IO REST client
io = RESTClient(aio_username, aio_key, wifi)

# Create a new 'circuitpython' feed with a description
print('Creating new Adafruit IO feed...')
feed = io.create_new_feed('circuitpython', 'a Adafruit IO CircuitPython feed')

# List a specified feed
print('Retrieving new Adafruit IO feed...')
specified_feed = io.get_feed('circuitpython')
print(specified_feed)

# Delete a specified feed by feed key
print('Deleting feed...')
io.delete_feed(specified_feed['key'])
print('Feed deleted!')
