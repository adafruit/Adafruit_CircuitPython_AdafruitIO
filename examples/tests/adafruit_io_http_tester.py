"""
CircuitPython_AdafruitIO IO_HTTP Tester
--------------------------------------------------

Tests Adafruit IO CircuitPython HTTP method
coverage with a WiFi CircuitPython device.

* Author(s): Brent Rubell for Adafruit Industries
"""
from random import randint, uniform
import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
import neopixel
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

# REQUIRES MicroPython's UnitTest
# https://github.com/micropython/micropython-lib/tree/master/unittest
import unittest

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# ESP32 Setup
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
aio_username = secrets["aio_user"]
aio_key = secrets["aio_password"]


class Test_IO_HTTP(unittest.TestCase):

    # Tests for Adafruit IO Authentication
    def test_set_user_key(self):
        """__init__ constructor
        correctly exposes provided credentials.
        """
        username = "adabot"
        key = "mho"
        io = IO_HTTP(username, key, wifi)
        self.assertEqual(username, io.username)
        self.assertEqual(key, io.key)

    def test_incorrect_user_pass_action(self):
        """Incorrect credentials provided to __init__
        should raise a RequestError.
        """
        username = "adabot"
        key = "mho"
        io = IO_HTTP(username, key, wifi)
        with self.assertRaises(AdafruitIO_RequestError):
            test_feed = io.get_feed("errorfeed")
            pass

    # Tests for Adafruit IO Data Methods
    def test_txrx(self):
        """Sends a random integer value to a feed and receives it back.
        """
        # Create an Adafruit IO HTTP Client
        io = IO_HTTP(aio_username, aio_key, wifi)
        try:
            test_feed = io.get_feed("testfeed")
        except AdafruitIO_RequestError:
            test_feed = io.create_new_feed("testfeed")
        tx_data = randint(1, 100)
        # send the value
        io.send_data(test_feed["key"], tx_data)
        # and get it back...
        rx_data = io.receive_data(test_feed["key"])
        self.assertEqual(int(rx_data["value"]), tx_data)

    def test_send_location_data(self):
        """Sets location metadata.
        send_data
        """
        # Create an Adafruit IO HTTP Client
        io = IO_HTTP(aio_username, aio_key, wifi)
        io.delete_feed('testfeed')
        test_feed = io.create_new_feed('testfeed')
        # value
        value = randint(1, 100)
        # Set up metadata associated with value
        metadata = {'lat': uniform(1, 100),
                    'lon': uniform(1, 100),
                    'ele': 10,
                    'created_at': None}
        io.send_data(test_feed['key'], value, metadata)
        rx_data = io.receive_data(test_feed['key'])
        self.assertEqual(int(rx_data['value']), value)
        self.assertAlmostEqual(float(rx_data['lat']), metadata['lat'])
        self.assertAlmostEqual(float(rx_data['lon']), metadata['lon'])
        self.assertAlmostEqual(float(rx_data['ele']), metadata['ele'])

    # Test for Adafruit IO Feed Methods
    def test_create_feed(self):
        """Test creating a new feed.
        """
        # Create an Adafruit IO HTTP Client
        io = IO_HTTP(aio_username, aio_key, wifi)
        io.delete_feed('testfeed')
        test_feed = io.create_new_feed('testfeed')
        self.assertEqual(test_feed['name'], 'testfeed')

    def test_delete_feed(self):
        """delete_feed by feed key
        """
        # Create an Adafruit IO HTTP Client
        io = IO_HTTP(aio_username, aio_key, wifi)
        io.delete_feed('testfeed')
        with self.assertRaises(AdafruitIO_RequestError):
            io.receive_data('testfeed'['key'])
            pass

    def test_delete_nonexistent_feed(self):
        """delete nonexistent feed by feed key
        """
        # Create an Adafruit IO HTTP Client
        io = IO_HTTP(aio_username, aio_key, wifi)
        io.delete_feed('testfeed')
        with self.assertRaises(AdafruitIO_RequestError):
            io.delete_feed['testfeed']


if __name__ == "__main__":
    # Pass the NetworkManager Object to UnitTest.py
    unittest.get_wifi(wifi)
    unittest.main()
