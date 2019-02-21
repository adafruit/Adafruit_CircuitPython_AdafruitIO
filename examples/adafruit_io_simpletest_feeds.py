"""
Example of interacting with Adafruit IO feeds
"""
import time
import board
import busio
from digitalio import DigitalInOut, Direction

# ESP32 SPI
import microcontroller
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import Adafruit IO REST Client
from Adafruit_IO import RESTClient, AdafruitIO_RequestError, AdafruitIO_ThrottleError

# Get wifi details and more from a settings.py file
try:
    from settings import settings
except ImportError:
    print("WiFi settings are kept in settings.py, please add them there!")
    raise

# PyPortal ESP32 Setup
esp32_cs = DigitalInOut(microcontroller.pin.PB14)
esp32_ready = DigitalInOut(microcontroller.pin.PB16)
esp32_gpio0 = DigitalInOut(microcontroller.pin.PB15)
esp32_reset = DigitalInOut(microcontroller.pin.PB17)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, settings, board.NEOPIXEL)

# Set your Adafruit IO Username and Key in settings.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
ADAFRUIT_IO_USER = settings['adafruit_io_user']
ADAFRUIT_IO_KEY = settings['adafruit_io_key']

# Create an instance of the Adafruit IO REST client
io = RESTClient(ADAFRUIT_IO_USER, ADAFRUIT_IO_KEY, wifi)

# Create a new 'circuitpython' feed with a description
print('Creating new Adafruit IO feed...')
feed = io.create_new_feed('circuitpython', 'a Adafruit IO CircuitPython feed')
print(feed)

# List a specified feed
print('Retrieving new Adafruit IO feed...')
specified_feed = io.get_feed('circuitpython')
print(specified_feed)

# Delete a specified feed by feed key
print('Deleting feed...')
io.delete_feed(specified_feed['key'])
print('Feed deleted!')