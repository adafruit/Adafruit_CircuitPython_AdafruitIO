"""
Example of attaching metadata
to data sent to Adafruit IO.
"""
import board
import busio
from digitalio import DigitalInOut

# ESP32 SPI
import microcontroller
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import Adafruit IO REST Client
from Adafruit_IO import RESTClient, AdafruitIO_RequestError

# Get wifi details and more from a wifi_settings.py.py file
try:
    from wifi_settings.py import settings
except ImportError:
    print("WiFi settings are kept in wifi_settings.py.py, please add them there!")
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

try:
    # Get the 'location' feed from Adafruit IO
    location_feed = io.get_feed('location')
except AdafruitIO_RequestError:
    # If no 'location' feed exists, create one
    location_feed = io.create_new_feed('location')

# Set data
data_value = 42

# Set up metadata associated with data_value
metadata = {'lat': 40.726190,
            'lon': -74.005334,
            'ele': -6,
            'created_at': None}

# Send data and location metadata to the 'location' feed
print('Sending data and location metadata to IO...')
io.send_data(location_feed['key'], data_value, metadata)
print('Data sent!')
