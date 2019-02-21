"""
Example of turning on and off a LED
from an Adafruit IO Dashboard.
"""
import time
import board
import microcontroller
import busio
from digitalio import DigitalInOut, Direction

# ESP32 SPI
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import Adafruit IO REST Client
from Adafruit_IO import RESTClient, AdafruitIO_RequestError

# Get wifi details and more from a wifi_settings.py.py file
try:
    from wifi_settings import settings
except ImportError:
    print("WiFi settings are kept in wifi_settings.py.py, please add them there!")
    raise

# PyPortal ESP32 Setup
esp32_cs = DigitalInOut(microcontroller.pin.PB14)
esp32_ready = DigitalInOut(microcontroller.pin.PB16)
esp32_reset = DigitalInOut(microcontroller.pin.PB17)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, settings, board.NEOPIXEL)

# Set your Adafruit IO Username and Key in wifi_settings.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
ADAFRUIT_IO_USER = settings['adafruit_io_user']
ADAFRUIT_IO_KEY = settings['adafruit_io_key']

# Create an instance of the Adafruit IO REST client
io = RESTClient(ADAFRUIT_IO_USER, ADAFRUIT_IO_KEY, wifi)

try:
    # Get the 'digital' feed from Adafruit IO
    digital_feed = io.get_feed('digital')
except AdafruitIO_RequestError:
    # If no 'digital' feed exists, create one
    digital_feed = io.create_new_feed('digital')

# Set up LED
LED = DigitalInOut(board.D13)
LED.direction = Direction.OUTPUT

while True:
    # Get data from 'digital' feed
    feed_data = io.receive_data(digital_feed['key'])

    # Check if data is ON or OFF
    if int(feed_data['value'] == 1):
        print('received <- ON\n')
    elif int(feed_data['value'] == 0):
        print('received <= OFF\n')

    # Set the LED to the feed value
    LED.value = int(feed_data['value'])

    time.sleep(0.5)
