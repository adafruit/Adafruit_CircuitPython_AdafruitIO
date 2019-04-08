"""
Adafruit IO CircuitPython Tester
---------------------------------------

Tests methods within adafruit_io for
compatibility with the Adafruit IO API.
"""
from random import randint, uniform
import time
import board
import busio
from digitalio import DigitalInOut

# ESP32 SPI
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

# Import NeoPixel Library
import neopixel

# Import Adafruit IO REST Client
from adafruit_io.adafruit_io import RESTClient, AdafruitIO_RequestError

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# PyPortal ESP32 Setup
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets['aio_username']
aio_key = secrets['aio_key']


def assertEqual(val_1, val_2):
    """Raises an AssertionError if the two specified values are not equal.
    """
    if val_1 is not val_2:
        raise AssertionError('Values are not equal:', val_1, val_2)

def delete_feed(io_client, io_feed):
    """Deletes a specified Adafruit IO Feed.
    """
    try:
        io_client.delete_feed(io_feed)
    except AdafruitIO_RequestError:
        # feed doesnt exist
        pass

def send_receive():
    """Sending a random int. to a feed and receiving it
    """
    print('Testing send_receive...')
    io = RESTClient(aio_username, aio_key, wifi)
    delete_feed(io, 'testfeed')
    test_feed = io.create_new_feed('testfeed')
    tx_data = randint(1, 100)
    # send the value
    io.send_data(test_feed['key'], tx_data)
    # and get it back...
    rx_data = io.receive_data(test_feed['key'])
    assertEqual(int(rx_data['value']), tx_data)
    print("OK!")

def send_location_data():
    """Sending a random location to a feed
    """
    print('Testing send_location_data...')
    io = RESTClient(aio_username, aio_key, wifi)
    delete_feed(io, 'testfeed')
    test_feed = io.create_new_feed('testfeed')
    # value
    value = randint(0, 100)
    # Set up metadata associated with value
    metadata = {'lat': uniform(1, 100),
                'lon': uniform(1, 100),
                'ele': randint(0, 1000),
                'created_at': None}
    io.send_data(test_feed['key'], value, metadata)
    rx_data = io.receive_data(test_feed['key'])
    assertEqual(int(rx_data['value']), value)
    assertEqual(float(rx_data['lat']), metadata['lat'])
    assertEqual(float(rx_data['lon']), metadata['lon'])
    assertEqual(int(rx_data['ele']), metadata['ele'])
    assertEqual(rx_data['created_at'], metadata['created_at'])
    print('OK!')

# tests to run
tests = [send_receive(), send_location_data()]

# start the timer
start_time = time.monotonic()
while True:
    try:
        for i in len(tests) - 1:
            print(i)
            tests[test]
            time.sleep(1)
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    final_time = time.monotonic()
    total_time = final_time-start_time
    print("Ran {0} tests in {1}".format(len(tests), total_time))
