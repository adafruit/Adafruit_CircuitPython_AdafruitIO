"""
Send data to Adafruit IO, and retrieve it.
"""
import time
import board
import busio
import adafruit_io
from digitalio import DigitalInOut, Direction

# ESP32 SPI
import microcontroller
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager

# Get wifi details and more from a settings.py file
try:
    from settings import settings
except ImportError:
    print("WiFi settings are kept in settings.py, please add them there!")
    raise

# PyPortal ESP32 Setup
esp32_cs = DigitalInOut(microcontroller.pin.PB14) # PB14
esp32_ready = DigitalInOut(microcontroller.pin.PB16)
esp32_gpio0 = DigitalInOut(microcontroller.pin.PB15)
esp32_reset = DigitalInOut(microcontroller.pin.PB17)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, settings, board.NEOPIXEL)

# Adafruit IO Setup
ADAFRUIT_IO_USER = 'YOUR_ADAFRUIT_IO_USERNAME'
ADAFRUIT_IO_KEY = 'YOUR_ADAFRUIT_IO_PASSWORD'
ADAFRUIT_IO_FEED = 'testfeed'
aio = adafruit_io.Client(ADAFRUIT_IO_USER, ADAFRUIT_IO_KEY, wifi)

counter = 0
while True:
    try:
        data = counter
        print('Sending {0} to Adafruit IO...'.format(data))
        aio.send_data(ADAFRUIT_IO_FEED, data)
        print('Data sent!')

        print('Receiving Feed {0}...'.format(ADAFRUIT_IO_FEED))
        data = aio.receive_data(ADAFRUIT_IO_FEED)
        print('Feed Value:', data['value'])

        counter = counter  + 1
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        continue
    response = None