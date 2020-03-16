"""
Example of getting weather
from the Adafruit IO Weather Service
NOTE: This example is for Adafruit IO
Plus subscribers only.
"""
import board
import busio
from digitalio import DigitalInOut

# ESP32 SPI
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import NeoPixel Library
import neopixel

# Import Adafruit IO HTTP Client
from adafruit_io.adafruit_io import IO_HTTP

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

# Weather Location ID
# (to obtain this value, visit
# https://io.adafruit.com/services/weather
# and copy over the location ID)
location_id = 1234

print("Getting weather record from IO...")
# Get the specified weather record with current weather
# and all available forecast information.
forecast = io.receive_weather(location_id)

# Get today's forecast
current_forecast = forecast["current"]
print(
    "It is {0} and {1}*F.".format(
        current_forecast["summary"], current_forecast["temperature"]
    )
)
print("with a humidity of {0}%".format(current_forecast["humidity"] * 100))

# Get tomorrow's forecast
tom_forecast = forecast["forecast_days_1"]
print(
    "\nTomorrow has a low of {0}*F and a high of {1}*F.".format(
        tom_forecast["temperatureLow"], tom_forecast["temperatureHigh"]
    )
)
print("with a humidity of {0}%".format(tom_forecast["humidity"] * 100))
