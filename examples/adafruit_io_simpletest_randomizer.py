"""
Example of using Adafruit IO's
random data service.
"""
import time
import board
import busio
from digitalio import DigitalInOut

# ESP32 SPI
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import Adafruit IO REST Client
from adafruit_io.adafruit_io import RESTClient

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

# Random Data ID
# (to obtain this value, visit
# https://io.adafruit.com/services/words
# and copy over the location ID)
random_data_id = 1234

while True:
    try:
        print('Fetching random data from Adafruit IO...')
        random_data = io.receive_random_data(random_data_id)
        print('Random Data: ', random_data['value'])
        print('Data Seed: ', random_data['seed'])
        print('Waiting 1 minute to fetch new randomized data...')
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    time.sleep(60)
