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

# Import Adafruit IO REST Client
from Adafruit_IO import RESTClient

# Get wifi details and more from a wifi_settings.py.py file
try:
    from wifi_settings import settings
except ImportError:
    print("WiFi settings are kept in wifi_settings.py.py, please add them there!")
    raise


# ESP32 Setup
esp32_cs = DigitalInOut(board.D9)
esp32_ready = DigitalInOut(board.D10)
esp32_reset = DigitalInOut(board.D5)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, settings, board.NEOPIXEL)

"""
# PyPortal ESP32 Setup
import microcontroller
esp32_cs = DigitalInOut(microcontroller.pin.PB14)
esp32_ready = DigitalInOut(microcontroller.pin.PB16)
esp32_reset = DigitalInOut(microcontroller.pin.PB17)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, settings, board.NEOPIXEL)
"""

# Set your Adafruit IO Username and Key in wifi_settings.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
ADAFRUIT_IO_USER = settings['adafruit_io_user']
ADAFRUIT_IO_KEY = settings['adafruit_io_key']

# Create an instance of the Adafruit IO REST client
io = RESTClient(ADAFRUIT_IO_USER, ADAFRUIT_IO_KEY, wifi)

# Weather Location ID
location_id = 2127

print('Getting weather record from IO...')
# Get the specified weather record with current weather
# and all available forecast information.
forecast = io.receive_weather(location_id)

# Get today's forecast
current_forecast = forecast['current']
print('It is {0} and {1}*F.'.format(current_forecast['summary'], current_forecast['temperature']))
print('with a humidity of {0}%'.format(current_forecast['humidity']))

# Get tomorrow's forecast
tom_forecast = forecast['forecast_days_1']
print('\nTomorrow has a low of {0}*F and a high of {1}*F.'.format(
    tom_forecast['temperatureLow'], tom_forecast['temperatureHigh']))
print('with a humidity of {0}%'.format(tom_forecast['humidity']))
