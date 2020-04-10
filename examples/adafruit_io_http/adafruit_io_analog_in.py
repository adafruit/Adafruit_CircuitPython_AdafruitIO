"""
Example of reading an analog light sensor
and sending the value to Adafruit IO
"""
import time
import board
import busio
from digitalio import DigitalInOut
from analogio import AnalogIn
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import NeoPixel Library
import neopixel

# Import Adafruit IO HTTP Client
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

# Delay between polling and sending light sensor data, in seconds
SENSOR_DELAY = 30

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# ESP32 Setup
try:
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)
except AttributeError:
    esp32_cs = DigitalInOut(board.D9)
    esp32_ready = DigitalInOut(board.D10)
    esp32_reset = DigitalInOut(board.D5)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(
    board.NEOPIXEL, 1, brightness=0.2
)  # Uncomment for Most Boards
"""Uncomment below for ItsyBitsy M4"""
# status_light = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

# Create an instance of the Adafruit IO HTTP client
io = IO_HTTP(aio_username, aio_key, wifi)

try:
    # Get the 'light' feed from Adafruit IO
    light_feed = io.get_feed("light")
except AdafruitIO_RequestError:
    # If no 'light' feed exists, create one
    light_feed = io.create_new_feed("light")

# Set up an analog light sensor on the PyPortal
adc = AnalogIn(board.LIGHT)

while True:
    light_value = adc.value
    print("Light Level: ", light_value)
    print("Sending to Adafruit IO...")
    io.send_data(light_feed["key"], light_value)
    print("Sent!")
    # delay sending to Adafruit IO
    time.sleep(SENSOR_DELAY)
