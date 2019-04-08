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

# Create Adafruit IO Client
io = RESTClient(aio_username, aio_key, wifi)

"""
Generic Test Assertions
"""

def assertAlmostEqual(x, y, places=None, msg=''):
    """Raises an AssertionError if two float values are not equal.
    (from https://github.com/micropython/micropython-lib/blob/master/unittest/unittest.py)
    """
    if x == y:
        return
    if places is None:
        places = 2
    if round(abs(y-x), places) == 0:
        return
    if not msg:
        msg = '%r != %r within %r places' % (x, y, places)
    assert False, msg

def assertRaises(exc, func=None, *args, **kwargs):
    """Raises based on context.
    (from https://github.com/micropython/micropython-lib/blob/master/unittest/unittest.py)
    """
    if func is None:
        return AssertRaisesContext(exc)

    try:
        func(*args, **kwargs)
        assert False, "%r not raised" % exc
    except Exception as e:
        if isinstance(e, exc):
            return
        raise

def assertIsNone(x):
    """Raises an AssertionError if x is None.
    """
    if x is None:
        raise AssertionError('%r is None'%x)

def assertEqual(val_1, val_2):
    """Raises an AssertionError if the two specified values are not equal.
    """
    if val_1 != val_2:
        raise AssertionError('Values are not equal:', val_1, val_2)

def delete_feed(io_feed_name):
    """Deletes a specified Adafruit IO Feed.
    """
    try:
        io.delete_feed(io_feed_name)
    except AdafruitIO_RequestError:
        # feed doesnt exist
        pass

def delete_group(io_group_name):
    """Deletes a specified Adafruit IO Group.
    """
    try:
        io.delete_group(io_group_name)
    except AdafruitIO_RequestError:
        # feed doesnt exist
        pass

"""
Data Functionality
"""
def send_receive():
    """Sending a random int. to a feed and receiving it back.
    send_data, receive_data
    """
    print('Testing send_receive...')
    delete_feed('testfeed')
    test_feed = io.create_new_feed('testfeed')
    tx_data = randint(1, 100)
    # send the value
    io.send_data(test_feed['key'], tx_data)
    # and get it back...
    rx_data = io.receive_data(test_feed['key'])
    assertEqual(int(rx_data['value']), tx_data)
    print("OK!")

def send_location_data():
    """Sending a random location to a feed.
    send_data
    """
    print('Testing send_location_data...')
    delete_feed('testfeed')
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
    assertEqual(int(rx_data['value']), value)
    assertAlmostEqual(float(rx_data['lat']), metadata['lat'])
    assertAlmostEqual(float(rx_data['lon']), metadata['lon'])
    assertAlmostEqual(float(rx_data['ele']), metadata['ele'])
    print('OK!')

"""
Feed Functionality
"""
def test_create_feed():
    """create_new_feed
    """
    print('Test create_new_feed')
    delete_feed('testfeed')
    test_feed = io.create_new_feed('testfeed')
    assertEqual(test_feed['name'], 'testfeed')
    print('OK!')

def test_delete_feed():
    """delete_feed
    """
    print('Test delete_feed()')
    delete_feed('testfeed')
    test_feed = io.create_new_feed('testfeed')
    assertRaises(AdafruitIO_RequestError, io.receive_data, 'testfeed')

def test_delete_nonexistent_feed():
    """delete_feed
    """
    print('Test delete_feed')
    delete_feed('testfeed')
    assertRaises(AdafruitIO_RequestError, io.delete_feed, 'testfeed')

"""
Group Functionality
"""

def create_group():
    print('Testing create_new_group()')
    io.delete_group('testgroup')
    response = io.create_new_group('testgroup', 'testing')
    assertEqual(response['name'], 'testgroup')
    assertEqual(response['description'], 'testing')

# delete group, like delete feed

# add a feed to a group and check if it's in the group

"""
Connected Services Functionality
"""
def test_receive_time():
    """receive_time
    """
    print('Testing receive_time()...')
    current_time = io.receive_time()
    assertIsNone(current_time[0])
    assertIsNone(current_time[1])
    assertIsNone(current_time[2])
    print('OK!')

# tests to run
tests = [send_receive, send_location_data, test_receive_time, test_create_feed,
            test_delete_feed, create_group]

# start the timer
start_time = time.monotonic()
while True:
    try:
        for i in range(len(tests)):
            tests[i]()
            time.sleep(1)
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying...\n", e)
        wifi.reset()
        continue
    final_time = time.monotonic()
    print("Ran {0} tests in {1} seconds".format(len(tests), final_time - start_time))
    break
